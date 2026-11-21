from fastapi import APIRouter
from app.api.v1 import auth, documents, deadlines

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents & Ingestion"])
api_router.include_router(deadlines.router, prefix="/deadlines", tags=["Deadlines & Calendar"])
