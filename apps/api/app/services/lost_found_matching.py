"""
Lost & Found candidate-matching (PRD section 16).

THIS IS A SIMPLE, EXPLICITLY DOCUMENTED HEURISTIC - NOT MACHINE LEARNING AND
NOT AN AI/NLP FEATURE. Given a case, it scores opposite-type cases (a "lost"
report is only ever compared against "found" reports and vice versa) on:

  * exact category match,
  * naive shared-keyword overlap between the two free-text descriptions,
  * how close together the two `occurred_at` timestamps are, and
  * whether the two reports name the same free-text location or were logged
    at nearly the same coordinates.

The score is a ranking aid for a human reviewer, nothing more. This module
never writes to the database and never decides that two cases ARE a match -
see app/api/v1/lost_found.py's confirm-match endpoint for the explicit human
confirmation step this project's scope decisions require before two
lost-found cases are ever linked or closed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cases import LostFoundCase
from app.models.enums import LostFoundStatus

#: A candidate below this score is not worth a reviewer's time and is
#: dropped rather than shown. Tuned by inspection, not learned.
MIN_SCORE = 1.0

#: How many days apart two `occurred_at` values can be and still count as a
#: temporal signal at all. Beyond this window, proximity contributes nothing
#: (not a penalty - an old found-item report can still be the right one).
DATE_PROXIMITY_WINDOW = timedelta(days=14)
#: Within this narrower window, proximity scores higher.
DATE_CLOSE_WINDOW = timedelta(days=2)

#: Cases in these statuses are no longer open for matching - a rejected
#: report was never a real item, and a closed case has already run its
#: course through the verification queue.
_EXCLUDED_STATUSES = frozenset({LostFoundStatus.CLOSED.value, LostFoundStatus.REJECTED.value})

#: Words this short or this common carry no matching signal on their own.
_STOPWORDS = frozenset(
    {"with", "that", "this", "from", "have", "were", "near", "about", "found", "lost"}
)


@dataclass
class CandidateMatch:
    """One scored candidate. A pure in-memory result - never persisted."""

    case: LostFoundCase
    score: float
    reasons: list[str] = field(default_factory=list)


def _tokenize(text: str) -> set[str]:
    return {word.strip(".,!?()\"'").lower() for word in text.split()}


def _keyword_overlap(a: str, b: str) -> int:
    """
    Count of shared, non-trivial words.

    Deliberately naive (no stemming, no synonyms, no NLP) - a tie-breaker
    signal on top of category/date, not a description-similarity model.
    """
    words_a = {w for w in _tokenize(a) if len(w) > 3 and w not in _STOPWORDS}
    words_b = {w for w in _tokenize(b) if len(w) > 3 and w not in _STOPWORDS}
    return len(words_a & words_b)


def score_pair(source: LostFoundCase, candidate: LostFoundCase) -> tuple[float, list[str]]:
    """Score one candidate against the source case. Higher is a better match."""
    score = 0.0
    reasons: list[str] = []

    if source.category == candidate.category:
        score += 3
        reasons.append(f"same category ({source.category})")

    overlap = _keyword_overlap(source.description, candidate.description)
    if overlap:
        score += min(overlap, 3)
        reasons.append(f"{overlap} shared description keyword(s)")

    if source.occurred_at and candidate.occurred_at:
        delta = abs(source.occurred_at - candidate.occurred_at)
        if delta <= DATE_PROXIMITY_WINDOW:
            score += 2 if delta <= DATE_CLOSE_WINDOW else 1
            reasons.append(f"reported within {delta.days} day(s) of each other")

    if (
        source.location_text
        and candidate.location_text
        and source.location_text.strip().lower() == candidate.location_text.strip().lower()
    ):
        score += 1
        reasons.append("same location text")

    if (
        source.latitude is not None
        and source.longitude is not None
        and candidate.latitude is not None
        and candidate.longitude is not None
        and abs(source.latitude - candidate.latitude) < 0.01
        and abs(source.longitude - candidate.longitude) < 0.01
    ):
        # ~1km-scale coarse proximity, not a geodesic distance - good enough
        # to break ties between "same ghat" and "across town".
        score += 1
        reasons.append("reported near the same coordinates")

    return score, reasons


def find_candidate_matches(
    db: Session, case: LostFoundCase, *, limit: int = 5
) -> list[CandidateMatch]:
    """
    Rank opposite-type, still-open cases against `case`.

    Only ever reads and scores - linking two cases together is always a
    separate, explicit admin action (POST .../confirm-match), never automatic.
    """
    opposite_type = "found" if case.report_type == "lost" else "lost"

    rows = (
        db.execute(
            select(LostFoundCase).where(
                LostFoundCase.report_type == opposite_type,
                LostFoundCase.id != case.id,
                LostFoundCase.status.not_in(_EXCLUDED_STATUSES),
            )
        )
        .scalars()
        .all()
    )

    scored: list[CandidateMatch] = []
    for row in rows:
        score, reasons = score_pair(case, row)
        if score >= MIN_SCORE:
            scored.append(CandidateMatch(case=row, score=score, reasons=reasons))

    scored.sort(key=lambda c: c.score, reverse=True)
    return scored[:limit]


__all__ = [
    "MIN_SCORE",
    "CandidateMatch",
    "score_pair",
    "find_candidate_matches",
]
