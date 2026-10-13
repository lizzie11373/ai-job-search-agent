from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from job_agent.models.job_candidate import JobVerificationLevel
from job_agent.models.preference import (
    JobAttributeProfile,
    PreferenceCheckResult,
)


# ---------------------------------------------------------------------------
# Backward-compatible enums
# ---------------------------------------------------------------------------

class ExecutionStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JDVerificationResult(StrEnum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class PursuitPriority(StrEnum):
    TOP_PRIORITY = "TOP_PRIORITY"
    STRONG_OPPORTUNITY = "STRONG_OPPORTUNITY"
    WORTH_CONSIDERING = "WORTH_CONSIDERING"
    DEPRIORITIZE = "DEPRIORITIZE"


class UserDecision(StrEnum):
    PASS = "PASS"
    SAVE_FOR_LATER = "SAVE_FOR_LATER"
    PURSUE_NOW = "PURSUE_NOW"


@dataclass
class JobOpportunity:
    """
    Durable completed analysis snapshot for one verified, non-duplicate posting.

    Once persisted, analysis fields are treated as historical product state.
    The only normal mutable field is user_decision.
    """

    opportunity_id: str
    title: str
    company: str
    source: str
    posting_url: str
    jd_text: str

    verification_level: JobVerificationLevel = (
        JobVerificationLevel.PUBLIC_POSTING
    )
    location: str | None = None

    # Discovery provenance.
    source_url: str | None = None
    source_message_id: str | None = None
    source_item_id: str | None = None

    # Grounded attributes snapshot used for preference evaluation.
    job_attributes: JobAttributeProfile = field(
        default_factory=JobAttributeProfile
    )

    # Opportunity-analysis results.
    requirement_fit_score: float | None = None
    pursuit_priority: PursuitPriority | None = None
    preference_results: dict[
        str,
        PreferenceCheckResult,
    ] = field(default_factory=dict)
    strong_matches: list[str] = field(default_factory=list)
    main_gaps: list[str] = field(default_factory=list)

    # Shared timestamp for all NEW opportunities created by one Agent Run.
    created_at: str | None = None

    # Human-in-the-loop state. This is independently mutable.
    user_decision: UserDecision | None = None

    def __post_init__(self) -> None:
        self.opportunity_id = self.opportunity_id.strip()
        self.title = self.title.strip()
        self.company = self.company.strip()
        self.source = self.source.strip()
        self.posting_url = self.posting_url.strip()
        self.jd_text = self.jd_text.strip()

        if not self.opportunity_id:
            raise ValueError("JobOpportunity requires opportunity_id.")
        if not self.title:
            raise ValueError("JobOpportunity requires title.")
        if not self.company:
            raise ValueError("JobOpportunity requires company.")
        if not self.posting_url:
            raise ValueError("JobOpportunity requires posting_url.")
        if not self.jd_text:
            raise ValueError("JobOpportunity requires a non-empty JD.")

    @property
    def canonical_job_url(self) -> str:
        """Temporary compatibility alias. New code uses posting_url."""
        return self.posting_url

    @property
    def jd_source_url(self) -> str:
        """Temporary compatibility alias for older prototype code."""
        return self.posting_url
