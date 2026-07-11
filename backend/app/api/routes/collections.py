# backend/app/api/routes/collections.py
import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.collections import CollectionRepository
from app.schemas.collections import CollectionCreate, CollectionUpdate, CollectionResponse
from app.ingestion.embedder import LMStudioEmbedder
from app.ingestion.indexer import DocumentIndexer
from app.retrieval.qdrant_client import QdrantClient

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db_session() as session:
        yield session


@router.get("/", response_model=list[CollectionResponse])
async def list_collections(session: AsyncSession = Depends(get_session)):
    repo = CollectionRepository(session)
    collections = await repo.get_all()
    return collections


@router.post("/", response_model=CollectionResponse, status_code=201)
async def create_collection(
    body: CollectionCreate, session: AsyncSession = Depends(get_session)
):
    repo = CollectionRepository(session)
    collection = await repo.create(name=body.name, description=body.description)
    return collection


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: str, session: AsyncSession = Depends(get_session)
):
    repo = CollectionRepository(session)
    collection = await repo.get_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: str,
    body: CollectionUpdate,
    session: AsyncSession = Depends(get_session),
):
    repo = CollectionRepository(session)
    try:
        updated = await repo.update(
            collection_id, **body.model_dump(exclude_unset=True)
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Collection not found")
    return updated


@router.delete("/{collection_id}", status_code=204)
async def delete_collection(
    collection_id: str, session: AsyncSession = Depends(get_session)
):
    repo = CollectionRepository(session)
    collection = await repo.get_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Clean up Qdrant vectors before deleting from database
    try:
        embedder = LMStudioEmbedder()
        qdrant = QdrantClient()
        indexer = DocumentIndexer(embedder=embedder, qdrant=qdrant)
        
        for document in collection.documents:
            try:
                await indexer.remove_document(document.file_path)
                logger.info(f"Removed document {document.id} from Qdrant")
            except Exception as e:
                logger.warning(f"Failed to remove document {document.id} from Qdrant: {e}")
    except Exception as e:
        logger.error(f"Failed to initialize indexer for cleanup: {e}")
    
    await repo.delete(collection_id)
    return None


@router.post("/{collection_id}/watch")
async def enable_watch(
    collection_id: str,
    watch_path: str,
    session: AsyncSession = Depends(get_session)
):
    """Enable file watching for a collection."""
    repo = CollectionRepository(session)
    collection = await repo.get_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    try:
        updated = await repo.update(collection_id, watch_path=watch_path)
        logger.info(f"Enabled watch on {watch_path} for collection {collection_id}")
        return {"status": "watching", "path": watch_path, "collection_id": collection_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{collection_id}/unwatch")
async def disable_watch(
    collection_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Disable file watching for a collection."""
    repo = CollectionRepository(session)
    collection = await repo.get_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    try:
        updated = await repo.update(collection_id, watch_path=None)
        logger.info(f"Disabled watch for collection {collection_id}")
        return {"status": "not watching", "collection_id": collection_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
