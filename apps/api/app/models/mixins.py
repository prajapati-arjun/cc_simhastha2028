"""Reusable column mixins."""
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, String, event, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.models.enums import ContentStatus, DataSource


class TimestampMixin:
    """created_at / updated_at maintained by the database clock."""

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )


class SoftDeleteMixin:
    """
    Rows are retired, never physically removed. A government content system
    needs the audit trail to still resolve the entity a log row points at, so
    DELETE /api/v1/admin/* sets this column and every read filters on it.
    """

    @declared_attr
    def deleted_at(cls) -> Mapped[datetime | None]:
        return mapped_column(DateTime(timezone=True), nullable=True)


class PublishableMixin:
    """Draft/published/archived lifecycle shared by all CMS-managed content."""

    @declared_attr
    def status(cls) -> Mapped[str]:
        return mapped_column(
            String(32), nullable=False, default=ContentStatus.DRAFT.value, index=True
        )

    @declared_attr
    def data_source(cls) -> Mapped[str]:
        return mapped_column(
            String(32), nullable=False, default=DataSource.CMS.value
        )


class PointLocationMixin:
    """
    Scalar latitude/longitude are the source of truth (the API contract returns
    plain floats, never GeoJSON). `geom` is a derived, GiST-indexed PostGIS
    point kept in sync by the event listener below, so proximity queries
    ("nearest help centre") are a Phase 2 query change rather than a migration.
    """

    @declared_attr
    def latitude(cls) -> Mapped[float | None]:
        return mapped_column(Float, nullable=True)

    @declared_attr
    def longitude(cls) -> Mapped[float | None]:
        return mapped_column(Float, nullable=True)

    @declared_attr
    def geom(cls):
        return mapped_column(
            Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
            nullable=True,
        )


def _sync_point_geom(mapper, connection, target) -> None:
    """Derive `geom` from latitude/longitude on every insert and update."""
    from geoalchemy2.elements import WKTElement

    lat, lon = target.latitude, target.longitude
    if lat is None or lon is None:
        target.geom = None
    else:
        target.geom = WKTElement(f"POINT({lon} {lat})", srid=4326)


def register_point_geom_sync(model: type) -> type:
    """Class decorator wiring the lat/lng -> geom listener onto a model."""
    event.listen(model, "before_insert", _sync_point_geom)
    event.listen(model, "before_update", _sync_point_geom)
    return model
