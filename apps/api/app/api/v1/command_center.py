"""Command Center API (PRD section 24). Read-only, admin-gated aggregation."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import DbSession, require_admin
from app.schemas.command_center import CommandCenterOverviewOut
from app.services.command_center import build_overview

router = APIRouter(
    prefix="/command-center",
    tags=["command-center"],
    dependencies=[Depends(require_admin)],
    responses={
        401: {"description": "Missing, malformed or expired bearer token."},
        403: {"description": "Authenticated, but this role has no admin access."},
    },
)


@router.get(
    "/overview",
    response_model=CommandCenterOverviewOut,
    summary="Aggregated operational overview for the command centre (admin only)",
    description=(
        "**Demo prototype, admin only, read-only.** Aggregates this "
        "project's own seeded/operator-entered data: the latest crowd "
        "density band per zone, open safety-case totals, and active "
        "critical announcements. Not connected to live CCTV, sensor or "
        "dispatch systems. The response is split into three sections: "
        "`observed` (real rows from our own database), `recommendations` "
        "(always empty - no model-generated recommendation engine exists in "
        "this prototype) and `human_decisions` (status values an "
        "authenticated admin set explicitly)."
    ),
)
def get_command_center_overview(db: DbSession) -> CommandCenterOverviewOut:
    return build_overview(db)
