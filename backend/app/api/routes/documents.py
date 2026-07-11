# backend/app/api/routes/documents.py
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.documents import DocumentRepository
from app.database.repositories.collections import CollectionRepository
from app.schemas.documents import DocumentResponse, DocumentUploadResponse, BatchUploadResult
from app.config import settings

router = APIRouter()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db_session() as session:
        yield session


@router.get("/collection/{collection_id}", response_model=list[DocumentResponse])
async def list_documents(
    collection_id: str, session: AsyncSession = Depends(get_session)
):
    """List all documents in a collection."""
    collection_repo = CollectionRepository(session)
    collection = await collection_repo.get_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    doc_repo = DocumentRepository(session)
    documents = await doc_repo.get_by_collection(collection_id)
    return documents


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    collection_id: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Upload a document, save it to disk, create DB record, and index it."""
    # Verify collection exists
    collection_repo = CollectionRepository(session)
    collection = await collection_repo.get_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # Determine storage path
    docs_dir = settings.data_dir / "documents"
    docs_dir.mkdir(parents=True, exist_ok=True)

    file_name = file.filename or "unknown"
    file_path = docs_dir / file_name

    # Read and save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    file_size = len(content)
    file_type = Path(file_name).suffix.lower().lstrip(".") or "unknown"

    # Create DB record
    doc_repo = DocumentRepository(session)
    document = await doc_repo.create(
        collection_id=collection_id,
        file_path=str(file_path),
        file_type=file_type,
        file_size=file_size,
    )

    # Index the document
    from app.ingestion.indexer import DocumentIndexer
    from app.ingestion.embedder import LMStudioEmbedder
    from app.retrieval.qdrant_client import QdrantClient

    embedder = LMStudioEmbedder()
    qdrant = QdrantClient()
    indexer = DocumentIndexer(embedder=embedder, qdrant=qdrant)

    try:
        result = await indexer.index_file(str(file_path), collection_id)
        if result["status"] == "success":
            await doc_repo.update_status(document.id, "indexed")
            return DocumentUploadResponse(
                document_id=document.id,
                file_name=file_name,
                status="indexed",
                message=f"Indexed {result['chunks_indexed']} chunks",
            )
        else:
            await doc_repo.update_status(
                document.id, "error", result.get("error", "Unknown error")
            )
            return DocumentUploadResponse(
                document_id=document.id,
                file_name=file_name,
                status="error",
                message=result.get("error", "Unknown error"),
            )
    except Exception as e:
        await doc_repo.update_status(document.id, "error", str(e))
        return DocumentUploadResponse(
            document_id=document.id,
            file_name=file_name,
            status="error",
            message=str(e),
        )



@router.post("/upload_batch", response_model=list[BatchUploadResult])
async def upload_documents_batch(
    collection_id: str = Form(...),
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Upload multiple documents in batch."""
    # Verify collection exists
    collection_repo = CollectionRepository(session)
    collection = await collection_repo.get_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Determine storage path
    docs_dir = settings.data_dir / "documents"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize indexer once for all files
    from app.ingestion.indexer import DocumentIndexer
    from app.ingestion.embedder import LMStudioEmbedder
    from app.retrieval.qdrant_client import QdrantClient
    
    embedder = LMStudioEmbedder()
    qdrant = QdrantClient()
    indexer = DocumentIndexer(embedder=embedder, qdrant=qdrant)
    
    results = []
    doc_repo = DocumentRepository(session)
    
    for file in files:
        try:
            file_name = file.filename or "unknown"
            file_path = docs_dir / file_name
            
            # Read and save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            file_size = len(content)
            file_type = Path(file_name).suffix.lower().lstrip(".") or "unknown"
            
            # Create DB record
            document = await doc_repo.create(
                collection_id=collection_id,
                file_path=str(file_path),
                file_type=file_type,
                file_size=file_size,
            )
            
            # Index the document
            result = await indexer.index_file(str(file_path), collection_id)
            if result["status"] == "success":
                await doc_repo.update_status(document.id, "indexed")
                results.append(
                    BatchUploadResult(
                        file_name=file_name,
                        status="success",
                        document_id=document.id,
                        message=f"Indexed {result['chunks_indexed']} chunks",
                    )
                )
            else:
                await doc_repo.update_status(document.id, "error", result.get("error", "Unknown error"))
                results.append(
                    BatchUploadResult(
                        file_name=file_name,
                        status="error",
                        document_id=document.id,
                        message=result.get("error", "Unknown error"),
                    )
                )
        except Exception as e:
            results.append(
                BatchUploadResult(
                    file_name=file.filename or "unknown",
                    status="error",
                    document_id=None,
                    message=str(e),
                )
            )
    
    return results

@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str, session: AsyncSession = Depends(get_session)
):
    """Delete a document from DB and remove from vector index."""
    doc_repo = DocumentRepository(session)
    document = await doc_repo.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove from vector index
    from app.ingestion.indexer import DocumentIndexer
    from app.ingestion.embedder import LMStudioEmbedder
    from app.retrieval.qdrant_client import QdrantClient

    embedder = LMStudioEmbedder()
    qdrant = QdrantClient()
    indexer = DocumentIndexer(embedder=embedder, qdrant=qdrant)

    try:
        await indexer.remove_document(document.file_path)
    except Exception:
        pass  # Best effort; don't fail the delete if index removal fails

    await doc_repo.delete(document_id)
    return None
