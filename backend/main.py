"""
Environmental Safety Platform - FastAPI Backend
Production-grade API for real-time environmental intelligence
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime, timedelta
import uvicorn

from api.routes import location, analysis, forecast, search
from core.config import settings

app = FastAPI(
    title="Environmental Safety Platform API",
    description="Real-time environmental intelligence and habitability risk assessment",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(location.router, prefix="/api/v1", tags=["Location"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(forecast.router, prefix="/api/v1", tags=["Forecast"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])

@app.get("/")
async def root():
    return {
        "name": "Environmental Safety Platform API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

