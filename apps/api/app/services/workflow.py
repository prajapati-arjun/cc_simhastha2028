"""
Guarded publication and case-status state machines.

Status is never a free-form column write. Every change goes through
`apply_transition`, which consults an explicit allowed-transition table and
refuses anything not listed. That matters for two reasons:

  1. Publication controls what millions of pilgrims can see. An accidental
     PATCH that sets `status` to an arbitrary string would put unreviewed
     content on a public safety surface.
  2. PRD section 28 specifies a five-stage editorial workflow. Sprint 1 ships
     the two-stage stub, but because the rules live in one table rather than
     scattered across route handlers, replacing this with the full workflow is
     a change to CONTENT_TRANSITIONS, not a rewrite of every admin endpoint.
"""
from __future__ import annotations

from app.models.enums import ContentStatus, LostFoundStatus, MissingPersonStatus


class InvalidTransition(Exception):
    """Raised when a status change is not permitted. Surfaces as HTTP 409."""

    def __init__(self, entity: str, current: str, requested: str, allowed: set[str]):
        self.entity = entity
        self.current = current
        self.requested = requested
        self.allowed = allowed
        allowed_text = ", ".join(sorted(allowed)) or "none"
        super().__init__(
            f"Cannot move {entity} from '{current}' to '{requested}'. "
            f"Allowed from '{current}': {allowed_text}."
        )


#: draft -> published -> archived lifecycle for Event/Announcement/Temple/Ghat.
#: Note `archived` is terminal: restoring archived content is an editorial
#: decision that should create a new revision, not silently republish.
CONTENT_TRANSITIONS: dict[str, set[str]] = {
    ContentStatus.DRAFT.value: {
        ContentStatus.PUBLISHED.value,
        ContentStatus.ARCHIVED.value,
    },
    ContentStatus.PUBLISHED.value: {
        ContentStatus.DRAFT.value,
        ContentStatus.ARCHIVED.value,
    },
    ContentStatus.ARCHIVED.value: set(),
}

#: Lost & Found verification queue.
LOST_FOUND_TRANSITIONS: dict[str, set[str]] = {
    LostFoundStatus.SUBMITTED.value: {
        LostFoundStatus.UNDER_REVIEW.value,
        LostFoundStatus.REJECTED.value,
    },
    LostFoundStatus.UNDER_REVIEW.value: {
        LostFoundStatus.VERIFIED.value,
        LostFoundStatus.REJECTED.value,
    },
    LostFoundStatus.VERIFIED.value: {
        LostFoundStatus.MATCHED.value,
        LostFoundStatus.CLOSED.value,
    },
    LostFoundStatus.MATCHED.value: {LostFoundStatus.CLOSED.value},
    LostFoundStatus.CLOSED.value: set(),
    LostFoundStatus.REJECTED.value: set(),
}

#: Missing-person verification queue. Deliberately has no path back out of
#: `resolved` or `closed`: reopening a missing-person case is a decision that
#: belongs with police, not with a CMS content manager clicking a dropdown.
MISSING_PERSON_TRANSITIONS: dict[str, set[str]] = {
    MissingPersonStatus.SUBMITTED.value: {
        MissingPersonStatus.UNDER_REVIEW.value,
        MissingPersonStatus.CLOSED.value,
    },
    MissingPersonStatus.UNDER_REVIEW.value: {
        MissingPersonStatus.VERIFIED.value,
        MissingPersonStatus.CLOSED.value,
    },
    MissingPersonStatus.VERIFIED.value: {
        MissingPersonStatus.RESOLVED.value,
        MissingPersonStatus.CLOSED.value,
    },
    MissingPersonStatus.RESOLVED.value: set(),
    MissingPersonStatus.CLOSED.value: set(),
}


def apply_transition(
    table: dict[str, set[str]],
    entity: str,
    current: str,
    requested: str,
) -> str:
    """
    Validate a status change and return the new status.

    A no-op change (current == requested) is accepted so that a PATCH which
    resends the whole object, unchanged status included, is not rejected.
    """
    if current == requested:
        return requested
    allowed = table.get(current, set())
    if requested not in allowed:
        raise InvalidTransition(entity, current, requested, allowed)
    return requested
