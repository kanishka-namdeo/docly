from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.session import init_db
from app.api.routes import collections, documents, conversations, chat, settings
from app.ingestion.embedder import LMStudioEmbedder
from app.ingestion.indexer import DocumentIndexer
from app.retrieval.qdrant_client import QdrantClient
from app.database.models import Collection
from app.database.session import get_db_session
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    await init_db()
    
    # Initialize file watchers for collections with watch_path set
    watchers = {}
    try:
        embedder = LMStudioEmbedder()
        qdrant = QdrantClient()
        indexer = DocumentIndexer(embedder=embedder, qdrant=qdrant)
        
        # Get all collections with watch_path set
        async for session in get_db_session():
            from sqlalchemy import select
            result = await session.execute(select(Collection).where(Collection.watch_path.isnot(None)))
            collections = result.scalars().all()
            
            for collection in collections:
                try:
                    from app.ingestion.watcher import CollectionWatcher
                    watcher = CollectionWatcher(
                        collection_id=collection.id,
                        watch_path=collection.watch_path,
                        indexer=indexer
                    )
                    watcher.start()
                    watchers[collection.id] = watcher
                    logger.info(f"Started watching {collection.watch_path} for collection {collection.id}")
                except Exception as e:
                    logger.error(f"Failed to start watcher for collection {collection.id}: {e}")
            break  # Only need one session
    except Exception as e:
        logger.error(f"Failed to initialize file watchers: {e}")
    
    yield
    
    # Cleanup: stop all watchers
    for watcher in watchers.values():
        try:
            watcher.stop()
        except Exception as e:
            logger.error(f"Error stopping watcher: {e}")

app = FastAPI(title="Doc Assistant Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(collections.router, prefix="/collections", tags=["collections"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(settings.router)  # Already has prefix="/settings" in router definition

@app.get("/health")
async def health_check():
    return {"status": "ok"}
