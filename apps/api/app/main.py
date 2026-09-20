"""
FastAPI application entrypoint.

This is a DevOps-owned scaffold: it wires up the app, CORS, and a health
check endpoint so the container has something real to boot and the local
dev stack (docker-compose) can be verified end-to-end. Backend Architect
owns everything under app/api/* (routers), app/models/*, app/schemas/*,
app/db/* — mount new routers onto `app` here, don't rebuild this file.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import (
    accommodation,
    admin,
    announcements,
    auth,
    command_center,
    crowd,
    emergency,
    events,
    ghats,
    incidents,
    lost_found,
    missing_person,
    parking,
    planner,
    temples,
)
from app.core.config import settings
from app.services.workflow import InvalidTransition

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Simhastha 2028 - Ujjain Digital Experience Platform API. "
        "Sprint 1 / Phase 1 (Foundation).\n\n"
        "**This is a demo prototype.** No endpoint in this API is connected to "
        "live police, medical, fire, CCTV or government dispatch systems. The "
        "SOS endpoint is simulated and dispatches nothing. Emergency directory "
        "phone numbers are deliberately fake placeholders. Temple timings, "
        "aarti schedules and accessibility details are placeholder text, not "
        "authority-verified information."
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


@app.exception_handler(InvalidTransition)
def invalid_transition_handler(request: Request, exc: InvalidTransition) -> JSONResponse:
    """
    Map a rejected workflow move to 409 Conflict.

    Handled centrally so every current and future route that calls
    apply_transition() reports the same status and message shape, rather than
    each handler remembering to catch it.
    """
    return JSONResponse(status_code=409, content={"detail": str(exc)})


# --- API v1 routers -------------------------------------------------------
API_V1_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(events.router, prefix=API_V1_PREFIX)
app.include_router(temples.router, prefix=API_V1_PREFIX)
app.include_router(ghats.router, prefix=API_V1_PREFIX)
app.include_router(emergency.router, prefix=API_V1_PREFIX)
app.include_router(announcements.router, prefix=API_V1_PREFIX)
app.include_router(lost_found.router, prefix=API_V1_PREFIX)
app.include_router(missing_person.router, prefix=API_V1_PREFIX)
app.include_router(planner.router, prefix=API_V1_PREFIX)
app.include_router(accommodation.router, prefix=API_V1_PREFIX)
app.include_router(parking.router, prefix=API_V1_PREFIX)
app.include_router(crowd.router, prefix=API_V1_PREFIX)
app.include_router(command_center.router, prefix=API_V1_PREFIX)
app.include_router(incidents.router, prefix=API_V1_PREFIX)
app.include_router(admin.router, prefix=API_V1_PREFIX)
