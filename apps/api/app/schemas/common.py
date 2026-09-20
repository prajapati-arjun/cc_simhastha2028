"""Shared schema primitives: the list envelope and contract-exact timestamps."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Generic, Sequence, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

T = TypeVar("T")


def _iso_utc(value: datetime | None) -> str | None:
    """
    Render as ``2028-04-09T04:30:00Z``.

    The contract pins this exact shape, so we normalise to UTC and drop
    microseconds rather than trusting whatever offset the driver hands back.
    Naive values are assumed UTC - every timestamp column in this service is
    ``TIMESTAMP WITH TIME ZONE``, so a naive value can only come from a test
    fixture.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


#: Use for every datetime the API emits.
UtcDateTime = Annotated[datetime, PlainSerializer(_iso_utc, return_type=str)]
OptionalUtcDateTime = Annotated[
    datetime | None, PlainSerializer(_iso_utc, return_type=str | None)
]


class ORMModel(BaseModel):
    """Base for response models read straight off a SQLAlchemy row."""

    model_config = ConfigDict(from_attributes=True)


class ListEnvelope(BaseModel, Generic[T]):
    """
    Uniform list wrapper (contract section 0).

    `last_updated` backs the DataFreshnessTimestamp component: at an event where
    people act on this data, the UI has to be able to say how stale it is.
    """

    items: list[T]
    total: int
    last_updated: OptionalUtcDateTime = Field(default=None)


def build_envelope(
    rows: Sequence[Any],
    items: list[Any],
    total: int,
) -> dict[str, Any]:
    """Assemble the envelope, deriving `last_updated` from the returned rows."""
    timestamps = [
        row.updated_at for row in rows if getattr(row, "updated_at", None) is not None
    ]
    return {
        "items": items,
        "total": total,
        "last_updated": max(timestamps) if timestamps else None,
    }
