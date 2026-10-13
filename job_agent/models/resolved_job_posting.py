from dataclasses import dataclass
from enum import StrEnum

from job_agent.models.job_candidate import (
    JobCandidate,
    JobVerificationLevel,
    JobVerificationResult,
)
from job_agent.models.opportunity import JobOpportunity


class JobDeduplicationResult(StrEnum):
    """
    Outcome of the current V1 exact posting-URL duplicate check.

    NEW:
        No existing JobOpportunity uses this same resolved posting URL.

    DUPLICATE:
        An existing JobOpportunity already uses this same posting URL.

    This is intentionally conservative:
        same posting_url   -> definitely duplicate for V1
        different URL      -> NOT proof that the underlying job is different
    """

    NEW = "NEW"
    DUPLICATE = "DUPLICATE"


@dataclass
class ResolvedJobPosting:
    """
    One verified public job posting produced from a discovery JobCandidate.

    Verification means:
    - the page was fetchable and structurally usable;
    - it was semantically consistent with the discovery lead;
    - the JD was sufficiently complete for downstream analysis.

    The posting may be employer-owned, ATS-hosted, or third-party.
    """

    source_candidate: JobCandidate

    posting_url: str
    jd_text: str

    verification_level: JobVerificationLevel = (
        JobVerificationLevel.PUBLIC_POSTING
    )

    # Optional display attributes extracted from the resolved posting.
    posting_title: str | None = None
    posting_company: str | None = None
    posting_location: str | None = None

    deduplication_result: JobDeduplicationResult | None = None

    def __post_init__(self) -> None:
        self.posting_url = self.posting_url.strip()
        self.jd_text = self.jd_text.strip()

        if not self.posting_url:
            raise ValueError(
                "ResolvedJobPosting must have a posting_url."
            )

        if not self.jd_text:
            raise ValueError(
                "ResolvedJobPosting must have a non-empty full JD."
            )

    @property
    def title(self) -> str:
        if self.posting_title and self.posting_title.strip():
            return self.posting_title.strip()
        return self.source_candidate.title

    @property
    def company(self) -> str:
        if self.posting_company and self.posting_company.strip():
            return self.posting_company.strip()
        return self.source_candidate.company

    @property
    def location(self) -> str | None:
        if self.posting_location and self.posting_location.strip():
            return self.posting_location.strip()
        return self.source_candidate.location

    @property
    def canonical_job_url(self) -> str:
        """
        Temporary compatibility alias for existing tests / old prototype code.

        New code should use `posting_url`.
        """
        return self.posting_url

    @property
    def official_title(self) -> str | None:
        """Temporary compatibility alias."""
        return self.posting_title

    @property
    def official_company(self) -> str | None:
        """Temporary compatibility alias."""
        return self.posting_company

    @property
    def official_location(self) -> str | None:
        """Temporary compatibility alias."""
        return self.posting_location

    def promote_to_job_opportunity(
        self,
        opportunity_id: str,
    ) -> JobOpportunity:
        """
        Promote only VERIFIED + NEW resolved postings.

        `source_item_id` is kept as provider/job-item provenance only.
        It intentionally does NOT fall back to source_message_id.
        """

        if (
            self.source_candidate.verification_result
            != JobVerificationResult.VERIFIED
        ):
            raise ValueError(
                "Parent JobCandidate must be VERIFIED before promotion."
            )

        if self.deduplication_result != JobDeduplicationResult.NEW:
            raise ValueError(
                "ResolvedJobPosting must be NEW after posting-URL "
                "deduplication before promotion."
            )

        return JobOpportunity(
            opportunity_id=opportunity_id,
            title=self.title,
            company=self.company,
            source=self.source_candidate.source,
            location=self.location,
            source_url=self.source_candidate.source_url,
            source_message_id=self.source_candidate.source_message_id,
            source_item_id=self.source_candidate.source_item_id,
            posting_url=self.posting_url,
            jd_text=self.jd_text,
            verification_level=self.verification_level,
        )
