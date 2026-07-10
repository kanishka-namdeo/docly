# backend/app/api/routes/collections.py
from fastapi import APIRouter, HTTPException, Depends
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
from app.database.repositories.collections import CollectionRepository
from app.schemas.collections import CollectionCreate, CollectionUpdate, CollectionResponse

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
    await repo.delete(collection_id)
    return None
