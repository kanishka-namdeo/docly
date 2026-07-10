from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.session import init_db
from app.api.routes import collections, documents, conversations, chat, settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

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
