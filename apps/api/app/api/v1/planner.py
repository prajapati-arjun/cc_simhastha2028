"""Pilgrimage Planner API (PRD section 7, Sprint 2, contract section 10)."""
from __future__ import annotations

from fastapi import APIRouter, status

from app.core.deps import DbSession
from app.schemas.planner import PlannerRequest, PlannerResponse
from app.services.planner import generate_itinerary

router = APIRouter(prefix="/planner", tags=["planner"])


@router.post(
    "/itinerary",
    response_model=PlannerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a personalised pilgrimage itinerary",
    description=(
        "**Demo prototype.** Builds a day-by-day plan from this project's own "
        "published temples, ghats and events using simple, deterministic "
        "scheduling rules. This is not an AI/RAG assistant and not a live "
        "booking or availability system. Nothing is persisted - call again to "
        "regenerate after changing preferences."
    ),
)
def create_itinerary(payload: PlannerRequest, db: DbSession) -> PlannerResponse:
    return generate_itinerary(db, payload)
