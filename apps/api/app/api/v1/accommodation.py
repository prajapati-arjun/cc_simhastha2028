"""Public Accommodation & essential services API (PRD section 17, roadmap item 2.5)."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.v1.helpers import LimitQuery, OffsetQuery, count_of
from app.core.deps import DbSession
from app.models.accommodation import (
    Accommodation,
    AccommodationType,
    EssentialService,
    EssentialServiceCategory,
)
from app.schemas.accommodation import (
    AccommodationOut,
    EssentialServiceOut,
)
from app.schemas.common import ListEnvelope, build_envelope
from app.services.accommodation import (
    accommodation_list_query,
    essential_service_list_query,
    get_published_accommodation_or_404,
    get_published_essential_service_or_404,
)

router = APIRouter(prefix="/accommodation", tags=["accommodation"])


# --------------------------------------------------------------------------
# Accommodation
#
# NOTE ON ROUTE ORDER: the literal "/services" routes are declared before
# "/{accommodation_ref}" on purpose. Starlette matches routes in declaration
# order, and "/{accommodation_ref}" would otherwise swallow a request for
# "/accommodation/services" with accommodation_ref="services" before the
# literal route ever gets a chance to match.
# --------------------------------------------------------------------------
@router.get(
    "",
    response_model=ListEnvelope[AccommodationOut],
    summary="List published accommodation",
    description=(
        "PRD section 17: `verified` distinguishes officially verified entries "
        "from third-party/commercial ones. Every seeded row is `false` - "
        "nothing in this prototype has been signed off by an authority."
    ),
)
def list_accommodation(
    db: DbSession,
    accommodation_type: AccommodationType | None = Query(
        default=None, description="Filter by accommodation type."
    ),
    verified: bool = Query(
        default=False, description="If true, return only verified listings."
    ),
    limit: int = LimitQuery,
    offset: int = OffsetQuery,
) -> ListEnvelope[AccommodationOut]:
    stmt = accommodation_list_query(accommodation_type, verified)
    total = count_of(db, stmt)
    rows = (
        db.execute(stmt.order_by(Accommodation.id.asc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return ListEnvelope[AccommodationOut].model_validate(
        build_envelope(rows, [AccommodationOut.model_validate(row) for row in rows], total)
    )


@router.get(
    "/services",
    response_model=ListEnvelope[EssentialServiceOut],
    summary="List published essential services",
    description=(
        "Food service, bhandara, drinking water, toilet and changing-facility "
        "points (PRD section 17)."
    ),
)
def list_essential_services(
    db: DbSession,
    category: EssentialServiceCategory | None = Query(
        default=None, description="Filter by service category."
    ),
    limit: int = LimitQuery,
    offset: int = OffsetQuery,
) -> ListEnvelope[EssentialServiceOut]:
    stmt = essential_service_list_query(category)
    total = count_of(db, stmt)
    rows = (
        db.execute(stmt.order_by(EssentialService.id.asc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return ListEnvelope[EssentialServiceOut].model_validate(
        build_envelope(
            rows, [EssentialServiceOut.model_validate(row) for row in rows], total
        )
    )


@router.get(
    "/services/{service_ref}",
    response_model=EssentialServiceOut,
    summary="Get one published essential service",
    description="Accepts either the numeric id or the slug.",
    responses={404: {"description": "No published essential service with that id or slug."}},
)
def get_essential_service(service_ref: str, db: DbSession) -> EssentialServiceOut:
    return EssentialServiceOut.model_validate(
        get_published_essential_service_or_404(db, service_ref)
    )


@router.get(
    "/{accommodation_ref}",
    response_model=AccommodationOut,
    summary="Get one published accommodation listing",
    description="Accepts either the numeric id or the slug.",
    responses={404: {"description": "No published accommodation with that id or slug."}},
)
def get_accommodation(accommodation_ref: str, db: DbSession) -> AccommodationOut:
    return AccommodationOut.model_validate(
        get_published_accommodation_or_404(db, accommodation_ref)
    )
