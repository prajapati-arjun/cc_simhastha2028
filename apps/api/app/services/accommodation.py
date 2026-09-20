"""Accommodation & essential services queries (PRD section 17, roadmap item 2.5)."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.api.v1.helpers import published_rows
from app.models.accommodation import (
    Accommodation,
    AccommodationType,
    EssentialService,
    EssentialServiceCategory,
)


def accommodation_list_query(
    accommodation_type: AccommodationType | None, verified_only: bool
) -> Select:
    stmt = published_rows(Accommodation)
    if accommodation_type is not None:
        stmt = stmt.where(Accommodation.accommodation_type == accommodation_type.value)
    if verified_only:
        stmt = stmt.where(Accommodation.verified.is_(True))
    return stmt


def get_published_accommodation_or_404(db: Session, ref: str) -> Accommodation:
    stmt = published_rows(Accommodation)
    if ref.isdigit():
        stmt = stmt.where(Accommodation.id == int(ref))
    else:
        stmt = stmt.where(Accommodation.slug == ref)
    row = db.execute(stmt).scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Accommodation not found"
        )
    return row


def essential_service_list_query(category: EssentialServiceCategory | None) -> Select:
    stmt = published_rows(EssentialService)
    if category is not None:
        stmt = stmt.where(EssentialService.category == category.value)
    return stmt


def get_published_essential_service_or_404(db: Session, ref: str) -> EssentialService:
    stmt = published_rows(EssentialService)
    if ref.isdigit():
        stmt = stmt.where(EssentialService.id == int(ref))
    else:
        stmt = stmt.where(EssentialService.slug == ref)
    row = db.execute(stmt).scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Essential service not found"
        )
    return row


__all__ = [
    "accommodation_list_query",
    "get_published_accommodation_or_404",
    "essential_service_list_query",
    "get_published_essential_service_or_404",
]
