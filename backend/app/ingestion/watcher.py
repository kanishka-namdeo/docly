"""File system auto-watch for document collections.

Monitors a directory recursively using watchdog and automatically
indexes new/modified documents or removes deleted ones from the index.
Bridges sync watchdog callbacks with the async indexer via asyncio.run().
"""

import asyncio
import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from app.ingestion.indexer import DocumentIndexer
from app.database.repositories.documents import DocumentRepository
from app.database.session import get_db_session

logger = logging.getLogger(__name__)


class DocumentEventHandler(FileSystemEventHandler):
    """Handles filesystem events for document collections.

    Debounces rapid events (create/modify) by 2 seconds so a single
    save-in-place from an editor triggers only one indexing pass.
    """

    DEBOUNCE_SECONDS = 2.0

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".md", ".html", ".htm"}

    def __init__(
        self,
        indexer: DocumentIndexer,
        collection_id: str,
    ):
        self.indexer = indexer
        self.collection_id = collection_id
        self._timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    # -- public API -----------------------------------------------------------

    def stop(self):
        """Cancel all pending debounce timers."""
        with self._lock:
            for timer in self._timers.values():
                timer.cancel()
            self._timers.clear()

    # -- watchdog callbacks ---------------------------------------------------

    def on_created(self, event: FileSystemEvent):
        if event.is_directory:
            return
        if not self._is_supported(event.src_path):
            return
        self._debounce(event.src_path, "created")

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory:
            return
        if not self._is_supported(event.src_path):
            return
        self._debounce(event.src_path, "modified")

    def on_moved(self, event: FileSystemEvent):
        """Handle a move/rename: delete old path, index new path."""
        if event.is_directory:
            return
        old_path = event.src_path
        new_path = event.dest_path
        if not self._is_supported(new_path):
            # The file was renamed to an unsupported extension — treat as delete
            self._on_deleted(old_path)
            return
        self._debounce(new_path, "moved")
        if old_path != new_path:
            self._on_deleted(old_path)

    def on_deleted(self, event: FileSystemEvent):
        if event.is_directory:
            return
        self._on_deleted(event.src_path)

    # -- internal -------------------------------------------------------------

    def _is_supported(self, path: str) -> bool:
        return Path(path).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def _debounce(self, file_path: str, event_type: str):
        """Schedule (or reschedule) indexing for *file_path* after a delay."""
        with self._lock:
            existing = self._timers.pop(file_path, None)
        if existing is not None:
            existing.cancel()

        timer = threading.Timer(
            self.DEBOUNCE_SECONDS,
            self._dispatch,
            args=(file_path, event_type),
        )
        timer.daemon = True
        with self._lock:
            self._timers[file_path] = timer
        timer.start()

    def _dispatch(self, file_path: str, event_type: str):
        """Remove the timer entry and hand off to the indexing runner."""
        with self._lock:
            self._timers.pop(file_path, None)

        if event_type == "deleted":
            self._on_deleted(file_path)
        else:
            self._on_index(file_path)

    def _on_index(self, file_path: str):
        """Bridge: run the async indexer from a sync watchdog thread."""
        try:
            asyncio.run(self._index_file(file_path))
        except Exception:
            logger.exception("Failed to index file: %s", file_path)

    def _on_deleted(self, file_path: str):
        """Bridge: run the async removal from a sync watchdog thread."""
        try:
            asyncio.run(self._remove_document(file_path))
        except Exception:
            logger.exception("Failed to remove document: %s", file_path)

    # -- async helpers --------------------------------------------------------

    async def _index_file(self, file_path: str):
        """Parse / chunk / embed a single file and update its DB status."""
        if not Path(file_path).exists():
            return

        async with get_db_session() as session:
            repo = DocumentRepository(session)
            doc = await repo.get_by_path(file_path)

        result: dict[str, Any] = await self.indexer.index_file(
            file_path, self.collection_id
        )

        async with get_db_session() as session:
            repo = DocumentRepository(session)
            if doc is None:
                # New file discovered — create the record.
                doc = await repo.create(
                    collection_id=self.collection_id,
                    file_path=file_path,
                    file_type=Path(file_path).suffix.lower().lstrip("."),
                    file_size=Path(file_path).stat().st_size,
                )

            if result["status"] == "success":
                await repo.update_status(doc.id, "indexed")
                logger.info("Indexed %s (%d chunks)", file_path, result["chunks_indexed"])
            else:
                await repo.update_status(doc.id, "error", result.get("error"))
                logger.error("Index error for %s: %s", file_path, result.get("error"))

    async def _remove_document(self, file_path: str):
        """Delete from vector index and remove the DB record."""
        await self.indexer.remove_document(file_path)

        async with get_db_session() as session:
            repo = DocumentRepository(session)
            doc = await repo.get_by_path(file_path)
            if doc is not None:
                await repo.delete(doc.id)
                logger.info("Removed document from index: %s", file_path)


class CollectionWatcher:
    """Watches a single collection's directory and dispatches events.

    Usage::

        watcher = CollectionWatcher("my-coll", "/data/docs", indexer)
        watcher.start()
        # ... later ...
        watcher.stop()
    """

    def __init__(
        self,
        collection_id: str,
        watch_path: str,
        indexer: DocumentIndexer,
    ):
        self.collection_id = collection_id
        self.watch_path = str(Path(watch_path).resolve())
        self.indexer = indexer
        self._observer: Optional[Observer] = None
        self._handler: Optional[DocumentEventHandler] = None

    @property
    def is_running(self) -> bool:
        return self._observer is not None and self._observer.is_alive()

    def start(self):
        """Begin watching *watch_path* recursively."""
        if self.is_running:
            logger.warning("CollectionWatcher already running for %s", self.collection_id)
            return

        self._handler = DocumentEventHandler(self.indexer, self.collection_id)
        self._observer = Observer()
        self._observer.schedule(
            self._handler, self.watch_path, recursive=True
        )
        self._observer.start()
        logger.info(
            "Started watching %s for collection %s",
            self.watch_path,
            self.collection_id,
        )

    def stop(self):
        """Stop the observer and cancel pending debounce timers."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

        if self._handler is not None:
            self._handler.stop()
            self._handler = None

        logger.info("Stopped watching collection %s", self.collection_id)
