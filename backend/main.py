"""FastAPI application entry point.

PHASE 1 SCOPE:
- Basic API endpoints for ingestion and embeddings
- No authentication (Phase 1 only)
- CORS enabled for development

FUTURE PHASES:
- Authentication/authorization
- Rate limiting
- Advanced error handling
- WebSocket support for real-time updates
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.api import ingest, embeddings

import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Phase 1: RNA expression data ingestion and embedding generation",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Phase 1, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(ingest.router, prefix="/ingest", tags=["ingestion"])
app.include_router(embeddings.router, prefix="/embeddings", tags=["embeddings"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RNA State Intelligence Platform API",
        "version": settings.api_version,
        "phase": 1,
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
