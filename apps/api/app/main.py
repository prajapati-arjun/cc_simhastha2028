"""
FastAPI application entrypoint.

This is a DevOps-owned scaffold: it wires up the app, CORS, and a health
check endpoint so the container has something real to boot and the local
dev stack (docker-compose) can be verified end-to-end. Backend Architect
owns everything under app/api/* (routers), app/models/*, app/schemas/*,
app/db/* — mount new routers onto `app` here, don't rebuild this file.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Simhastha 2028 - Ujjain Digital Experience Platform API. "
        "Sprint 1 / Phase 1 (Foundation) scaffold."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict:
    """Liveness/readiness check used by docker-compose and local verification."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "env": settings.ENV,
    }


# NOTE for Backend Architect: register feature routers here, e.g.
#   from app.api.v1 import events, temples, ghats, emergency, lost_found, missing_person
#   app.include_router(events.router, prefix="/api/v1")
