"""Public ghats API (PRD section 9/13, decision D-03, contract section 3)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.v1.helpers import LimitQuery, OffsetQuery, count_of, published_rows
from app.core.deps import DbSession
from app.core.notices import GHAT_STATUS_NOTICE
from app.models.content import Ghat
from app.schemas.common import ListEnvelope, build_envelope
from app.schemas.content import GhatOut, GhatStatusOut

router = APIRouter(prefix="/ghats", tags=["ghats"])


@router.get(
    "",
    response_model=ListEnvelope[GhatOut],
    summary="List published bathing ghats",
)
def list_ghats(
    db: DbSession,
    limit: int = LimitQuery,
    offset: int = OffsetQuery,
) -> ListEnvelope[GhatOut]:
    stmt = published_rows(Ghat)
    total = count_of(db, stmt)
    rows = (
        db.execute(stmt.order_by(Ghat.id.asc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    return ListEnvelope[GhatOut].model_validate(
        build_envelope(rows, [GhatOut.model_validate(row) for row in rows], total)
    )


@router.get(
    "/{ghat_ref}/status",
    response_model=GhatStatusOut,
    summary="Get the operational status of one ghat",
    description=(
        "Accepts either the numeric ghat id or its slug. "
        "**This is seeded placeholder data.** No crowd sensor, CCTV feed or "
        "headcount source is connected to this prototype, so `crowd_level` is "
        "always null - clients must render 'not available' rather than "
        "substituting a colour-coded badge."
    ),
    responses={404: {"description": "No published ghat with that id or slug."}},
)
def get_ghat_status(ghat_ref: str, db: DbSession) -> GhatStatusOut:
    stmt = published_rows(Ghat)

    # The contract pins this single path for both key types (PRD section 37
    # names /ghats/{id}/status, while the UI routes on slug), so resolve either.
    if ghat_ref.isdigit():
        stmt = stmt.where(Ghat.id == int(ghat_ref))
    else:
        stmt = stmt.where(Ghat.slug == ghat_ref)

    row = db.execute(stmt).scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ghat not found"
        )

    return GhatStatusOut(
        ghat_id=row.id,
        slug=row.slug,
        name=row.name,
        status=row.operational_status,
        # Hardcoded null on purpose, and typed as `None` in GhatStatusOut so
        # the response model itself cannot carry a crowd level. No sensor or
        # CCTV feed exists this sprint; if someone populates Ghat.crowd_level
        # by hand, that value must still never reach a pilgrim deciding where
        # to enter a river. Wiring a real feed means changing this line and
        # the schema together, deliberately.
        crowd_level=None,
        advisory=row.advisory,
        data_source=row.data_source,
        prototype_notice=GHAT_STATUS_NOTICE,
        updated_at=row.updated_at,
    )
