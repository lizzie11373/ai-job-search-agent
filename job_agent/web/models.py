from dataclasses import dataclass, field


@dataclass(frozen=True)
class JobPostingMetadata:
    """
    Structured identity metadata extracted from machine-readable
    JobPosting JSON-LD on an official job page.

    This is retrieval evidence, not a VERIFIED / UNVERIFIED result.
    """

    title: str | None = None
    company: str | None = None
    locations: tuple[str, ...] = field(default_factory=tuple)
    applicant_locations: tuple[str, ...] = field(default_factory=tuple)
    job_location_type: str | None = None
    identifier: str | None = None


@dataclass(frozen=True)
class PageSnapshot:
    """
    Provider-neutral snapshot of one fetched web page.

    This is retrieval data, not a verification business result.
    A page may be reachable but still be the wrong job.

    job_postings contains any machine-readable JobPosting JSON-LD
    objects discovered in the page HTML.
    """

    requested_url: str
    final_url: str
    status_code: int
    content_type: str | None
    title: str | None
    text: str
    job_postings: tuple[JobPostingMetadata, ...] = field(
        default_factory=tuple
    )
