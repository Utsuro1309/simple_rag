from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, query
from app.services.weaviate_client import init_schema

@asynccontextmanager
async def lifespan(app: FastAPI):          # ← thêm async
    init_schema()                          # init_schema đồng bộ vẫn ổn
    yield

app = FastAPI(title="Document QA - RAG & PageIndex", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(query.router)

@app.get("/health")
async def health():
    return {"status": "ok"}