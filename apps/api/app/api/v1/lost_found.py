"""
Public Lost & Found API (PRD section 16, decision D-01, contract section 5).

There are exactly two public routes here: submit a report, and read one back by
its opaque case reference. There is deliberately NO list endpoint and NO lookup
by reporter name or phone.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import AdminUser, DbSession
from app.core.notices import LOST_FOUND_NOTICE
from app.models.cases import LostFoundCase
from app.models.enums import LostFoundStatus
from app.schemas.cases import (
    CaseCreatedOut,
    LostFoundAdminOut,
    LostFoundCandidateMatchOut,
    LostFoundConfirmMatchRequest,
    LostFoundCreate,
    LostFoundPublicOut,
)
from app.services.audit import record_audit
from app.services.lost_found_matching import find_candidate_matches
from app.services.references import allocate_case_reference
from app.services.workflow import LOST_FOUND_TRANSITIONS, apply_transition

router = APIRouter(prefix="/lost-found", tags=["lost-found"])


@router.post(
    "",
    response_model=CaseCreatedOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a lost or found item report",
    description=(
        "**Demo prototype.** The report is stored in this project's own test "
        "database. It is not shared with police, railway property offices, or "
        "any lost-property authority, and no one is notified.\n\n"
        "The returned `case_reference` is the ONLY way to check this report "
        "again - there is no lookup by name or phone. Validation: "
        "`description` 10-2000 characters, `reporter_phone` required and "
        "non-empty, `occurred_at` must not be in the future."
    ),
)
def create_lost_found(payload: LostFoundCreate, db: DbSession) -> CaseCreatedOut:
    reference = allocate_case_reference(db, LostFoundCase, "LF")

    case = LostFoundCase(
        case_reference=reference,
        report_type=payload.report_type.value,
        category=payload.category.value,
        description=payload.description,
        location_text=payload.location_text,
        latitude=payload.latitude,
        longitude=payload.longitude,
        occurred_at=payload.occurred_at,
        reporter_name=payload.reporter_name,
        reporter_phone=payload.reporter_phone,
        image_url=payload.image_url,
        status=LostFoundStatus.SUBMITTED.value,
    )
    db.add(case)
    db.flush()

    record_audit(
        db,
        action="lost_found.submitted",
        entity_type="lost_found_case",
        entity_id=case.id,
        actor_user_id=None,
        detail={
            "case_reference": reference,
            "report_type": case.report_type,
            "category": case.category,
            "status": case.status,
        },
    )
    db.commit()
    db.refresh(case)

    return CaseCreatedOut(
        case_reference=case.case_reference,
        status=case.status,
        created_at=case.created_at,
        prototype_notice=LOST_FOUND_NOTICE,
    )


@router.get(
    "/{case_reference}",
    response_model=LostFoundPublicOut,
    summary="Check the status of a lost/found report by case reference",
    description=(
        "The only public read path for this resource. Returns progress and the "
        "report's own non-identifying descriptors; it does not return the "
        "reporter's name or phone number, the free-text description, the "
        "uploaded image, or the coordinates.\n\n"
        "There is no list endpoint and no search by name or phone."
    ),
    responses={404: {"description": "No report with that case reference."}},
)
def get_lost_found(case_reference: str, db: DbSession) -> LostFoundPublicOut:
    case = db.execute(
        select(LostFoundCase).where(
            # Exact match on the stored reference only. No LIKE, no prefix
            # search, no fallback to id - any of those would turn this into an
            # enumeration surface.
            LostFoundCase.case_reference == case_reference.strip().upper()
        )
    ).scalar_one_or_none()

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    return LostFoundPublicOut(
        case_reference=case.case_reference,
        report_type=case.report_type,
        category=case.category,
        status=case.status,
        created_at=case.created_at,
        updated_at=case.updated_at,
        prototype_notice=LOST_FOUND_NOTICE,
    )


# --------------------------------------------------------------------------
# Candidate matching (PRD section 16) - admin only.
#
# Reachable only with an admin bearer token, same posture as the verification
# queues in app/api/v1/admin.py: a heuristic score plus a free-text
# description is far more identifying than the public status endpoint above
# is allowed to leak.
# --------------------------------------------------------------------------
def _get_case_or_404(db: Session, item_id: int) -> LostFoundCase:
    case = db.execute(
        select(LostFoundCase).where(LostFoundCase.id == item_id)
    ).scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.get(
    "/{item_id}/candidate-matches",
    response_model=list[LostFoundCandidateMatchOut],
    summary="Suggested opposite-type matches for a case (admin review only)",
    description=(
        "**Heuristic ranking, not AI/ML.** Scores opposite-type (lost<->found) "
        "cases on category, description keyword overlap and date/location "
        "proximity - see app/services/lost_found_matching.py. This endpoint "
        "only surfaces candidates for a human reviewer; nothing here links or "
        "closes a case. Use POST .../confirm-match to do that explicitly."
    ),
    responses={404: {"description": "No such case."}},
)
def get_candidate_matches(item_id: int, db: DbSession, admin: AdminUser) -> Any:
    case = _get_case_or_404(db, item_id)
    matches = find_candidate_matches(db, case)
    return [
        LostFoundCandidateMatchOut(
            id=match.case.id,
            case_reference=match.case.case_reference,
            report_type=match.case.report_type,
            category=match.case.category,
            status=match.case.status,
            score=match.score,
            reasons=match.reasons,
            created_at=match.case.created_at,
        )
        for match in matches
    ]


@router.post(
    "/{item_id}/confirm-match",
    response_model=LostFoundAdminOut,
    summary="Confirm a match between two Lost & Found cases (admin only)",
    description=(
        "The explicit human confirmation step this project's safety scope "
        "requires (decision record: no algorithmic match ever auto-closes or "
        "auto-links a case). Both cases must already be `verified` - each "
        "moves to `matched` through the same guarded transition table the "
        "verification queue uses, so an unverified or already-closed case is "
        "rejected with 409, not silently matched. Both cases are cross-linked "
        "via `matched_case_id` and the confirmation is recorded in the audit "
        "trail."
    ),
    responses={
        404: {"description": "No such case, on either side of the match."},
        409: {"description": "Invalid status transition - one of the two cases is not `verified`."},
        422: {"description": "Attempted to match a case to itself or to a same-type case."},
    },
)
def confirm_match(
    item_id: int,
    payload: LostFoundConfirmMatchRequest,
    db: DbSession,
    admin: AdminUser,
) -> Any:
    case = _get_case_or_404(db, item_id)
    other = _get_case_or_404(db, payload.matched_case_id)

    if other.id == case.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A case cannot be matched to itself",
        )
    if other.report_type == case.report_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A case can only be matched to an opposite-type (lost<->found) case",
        )

    for row in (case, other):
        row.status = apply_transition(
            LOST_FOUND_TRANSITIONS,
            "lost_found_case",
            row.status,
            LostFoundStatus.MATCHED.value,
        )
    case.matched_case_id = other.id
    other.matched_case_id = case.id
    db.flush()

    record_audit(
        db,
        action="lost_found.match_confirmed",
        entity_type="lost_found_case",
        entity_id=case.id,
        actor_user_id=admin.id,
        detail={
            "case_reference": case.case_reference,
            "matched_case_reference": other.case_reference,
            "matched_case_id": other.id,
        },
    )
    db.commit()
    db.refresh(case)
    return LostFoundAdminOut.model_validate(case)
