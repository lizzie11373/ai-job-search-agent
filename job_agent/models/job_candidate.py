from dataclasses import dataclass
from enum import StrEnum


class ResolutionExecutionStatus(StrEnum):
    """Technical outcome of one JobCandidate resolution attempt."""

    COMPLETED = "COMPLETED"
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"


class JobVerificationResult(StrEnum):
    """Business result of a resolution attempt that completed normally."""

    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class JobVerificationLevel(StrEnum):
    """Grounding provenance for a VERIFIED job posting."""

    # New V1 meaning: a specific public posting was fetched, structurally usable,
    # semantically consistent with the discovery lead, and complete enough for
    # downstream analysis. It may be employer-owned, ATS-hosted, or third-party.
    PUBLIC_POSTING = "PUBLIC_POSTING"

    # Kept temporarily for backward compatibility with earlier experiments.
    EMPLOYER_OFFICIAL = "EMPLOYER_OFFICIAL"
    TRUSTED_PROVIDER = "TRUSTED_PROVIDER"


class JobResolutionReason(StrEnum):
    """Compact reason taxonomy used for observability and later evaluation."""

    ANALYSIS_READY_PUBLIC_POSTING = "ANALYSIS_READY_PUBLIC_POSTING"
    NO_SUITABLE_POSTING_FOUND = "NO_SUITABLE_POSTING_FOUND"

    SEARCH_ERROR = "SEARCH_ERROR"
    SEMANTIC_VERIFICATION_ERROR = "SEMANTIC_VERIFICATION_ERROR"

    # Legacy values retained so older persisted/logged runs do not break imports.
    ANALYSIS_READY_PROVIDER_POSTING = "ANALYSIS_READY_PROVIDER_POSTING"
    ANALYSIS_READY_OFFICIAL_POSTING = "ANALYSIS_READY_OFFICIAL_POSTING"
    PROVIDER_PAGE_NOT_FOUND = "PROVIDER_PAGE_NOT_FOUND"
    PROVIDER_CONTENT_INACCESSIBLE = "PROVIDER_CONTENT_INACCESSIBLE"
    INSUFFICIENT_JOB_DESCRIPTION = "INSUFFICIENT_JOB_DESCRIPTION"
    NO_TRUSTWORTHY_POSTING_FOUND = "NO_TRUSTWORTHY_POSTING_FOUND"
    NETWORK_ERROR = "NETWORK_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    SERVER_ERROR = "SERVER_ERROR"
    IDENTITY_RESOLUTION_ERROR = "IDENTITY_RESOLUTION_ERROR"


@dataclass
class JobCandidate:
    """
    Transient discovery lead extracted from an email or other ingestion source.

    Discovery and verification remain separate:
        JobCandidate = "I heard this opportunity exists"
        VERIFIED     = "I found a sufficiently consistent, sufficiently complete JD"

    Technical failure remains separate from the normal UNVERIFIED business outcome.
    """

    source: str
    source_message_id: str
    title: str
    company: str

    location: str | None = None
    source_url: str | None = None
    source_item_id: str | None = None

    execution_status: ResolutionExecutionStatus | None = None
    verification_result: JobVerificationResult | None = None
    verification_level: JobVerificationLevel | None = None
    resolution_reason: JobResolutionReason | None = None
    resolution_error: str | None = None

    def mark_verified(
        self,
        *,
        level: JobVerificationLevel,
        reason: JobResolutionReason,
    ) -> None:
        self.execution_status = ResolutionExecutionStatus.COMPLETED
        self.verification_result = JobVerificationResult.VERIFIED
        self.verification_level = level
        self.resolution_reason = reason
        self.resolution_error = None

    def mark_unverified(
        self,
        *,
        reason: JobResolutionReason,
    ) -> None:
        self.execution_status = ResolutionExecutionStatus.COMPLETED
        self.verification_result = JobVerificationResult.UNVERIFIED
        self.verification_level = None
        self.resolution_reason = reason
        self.resolution_error = None

    def mark_technical_failure(
        self,
        *,
        reason: JobResolutionReason,
        error: Exception | str,
    ) -> None:
        self.execution_status = ResolutionExecutionStatus.TECHNICAL_FAILURE
        self.verification_result = None
        self.verification_level = None
        self.resolution_reason = reason
        self.resolution_error = str(error)
