"""Public temples API (PRD section 13, contract section 2)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.v1.helpers import LimitQuery, OffsetQuery, count_of, published_rows
from app.core.deps import DbSession
from app.models.content import Temple
from app.schemas.common import ListEnvelope, build_envelope
from app.schemas.content import TempleOut

router = APIRouter(prefix="/temples", tags=["temples"])


@router.get(
    "",
    response_model=ListEnvelope[TempleOut],
    summary="List published temples and spiritual destinations",
    description=(
        "Returns the seeded temple directory. `verified` is false on every "
        "seeded row - nothing in this prototype has been signed off by a "
        "temple authority, and timings/aarti/accessibility text is explicitly "
        "marked placeholder."
    ),
)
def list_temples(
    db: DbSession,
    limit: int = LimitQuery,
    offset: int = OffsetQuery,
) -> ListEnvelope[TempleOut]:
    stmt = published_rows(Temple)
    total = count_of(db, stmt)
    rows = (
        db.execute(stmt.order_by(Temple.id.asc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return ListEnvelope[TempleOut].model_validate(
        build_envelope(rows, [TempleOut.model_validate(row) for row in rows], total)
    )


@router.get(
    "/{slug}",
    response_model=TempleOut,
    summary="Get one published temple by slug",
    responses={404: {"description": "No published temple with that slug."}},
)
def get_temple(slug: str, db: DbSession) -> TempleOut:
    row = db.execute(
        published_rows(Temple).where(Temple.slug == slug)
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Temple not found"
        )
    return TempleOut.model_validate(row)
