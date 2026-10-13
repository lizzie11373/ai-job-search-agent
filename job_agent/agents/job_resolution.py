import logging
from http.client import HTTPException
from urllib.error import URLError

from job_agent.agents.job_page_validator import (
    FetchedPageDisposition,
    validate_fetched_job_page,
)
from job_agent.agents.job_relevance_evaluator import evaluate_job_pages
from job_agent.agents.job_search_filter import (
    SearchResultDisposition,
    filter_job_search_results,
)
from job_agent.agents.job_search_query_builder import build_job_search_query
from job_agent.models.job_candidate import (
    JobCandidate,
    JobResolutionReason,
    JobVerificationLevel,
)
from job_agent.models.resolved_job_posting import ResolvedJobPosting
from job_agent.search.client import search_web
from job_agent.web.client import fetch_web_page
from job_agent.web.models import PageSnapshot


logger = logging.getLogger(__name__)


DIRECT_WEB_SEARCH_SOURCES = {
    "LINKEDIN",
    "INDEED",
}

MAX_SEARCH_RESULTS = 30
FETCH_BATCH_SIZE = 5
MAX_FETCH_RESULTS = 15


class JobResolutionTechnicalError(RuntimeError):
    """Workflow-level technical failure that should be retried later."""


def _normalized_source(job_candidate: JobCandidate) -> str:
    return (job_candidate.source or "").strip().upper()


def _source_goes_directly_to_web_search(
    job_candidate: JobCandidate,
) -> bool:
    return (
        _normalized_source(job_candidate)
        in DIRECT_WEB_SEARCH_SOURCES
    )


def _build_resolved_posting(
    *,
    job_candidate: JobCandidate,
    snapshot: PageSnapshot,
) -> ResolvedJobPosting:
    """
    Build the transient verified-posting domain object.

    `posting_url` means the fetched public posting used for downstream
    analysis. It is not claimed to be a globally canonical cross-site
    identity.
    """

    return ResolvedJobPosting(
        source_candidate=job_candidate,
        posting_url=snapshot.final_url,
        jd_text=snapshot.text,
        verification_level=JobVerificationLevel.PUBLIC_POSTING,
        posting_title=None,
        posting_company=None,
        posting_location=None,
    )


def _raise_technical_failure(
    *,
    job_candidate: JobCandidate,
    reason: JobResolutionReason,
    error: Exception | str,
) -> None:
    job_candidate.mark_technical_failure(
        reason=reason,
        error=error,
    )

    raise JobResolutionTechnicalError(
        f"{reason.value}: {error}"
    )


def _first_verified_page(
    *,
    job_candidate: JobCandidate,
    pages: list[PageSnapshot],
) -> PageSnapshot | None:
    """
    One bounded semantic-verification call over one small page batch.

    Page order is preserved so Search-provider ranking remains the V1
    candidate ordering.
    """

    if not pages:
        return None

    try:
        evaluations = evaluate_job_pages(
            job_candidate=job_candidate,
            pages=pages,
        )
    except Exception as error:
        _raise_technical_failure(
            job_candidate=job_candidate,
            reason=(
                JobResolutionReason.SEMANTIC_VERIFICATION_ERROR
            ),
            error=error,
        )

    for evaluation in evaluations:
        if (
            evaluation.is_match
            and evaluation.sufficiently_complete
        ):
            return evaluation.page

    return None


def _try_other_source_url_fast_path(
    *,
    job_candidate: JobCandidate,
) -> ResolvedJobPosting | None:
    """
    For non-LinkedIn/non-Indeed sources, try source_url exactly once.

    Any ordinary miss immediately falls back to Web Search.
    """

    source_url = (
        job_candidate.source_url or ""
    ).strip()

    if not source_url:
        return None

    try:
        snapshot = fetch_web_page(source_url)
    except (
        HTTPException,
        URLError,
        ValueError,
        TimeoutError,
        OSError,
    ) as error:
        logger.info(
            "Source URL fast path failed; falling back to Web Search "
            "(%s: %s)",
            type(error).__name__,
            error,
        )
        return None

    validation = validate_fetched_job_page(snapshot)

    if (
        validation.disposition
        != FetchedPageDisposition.USABLE
    ):
        return None

    verified_page = _first_verified_page(
        job_candidate=job_candidate,
        pages=[validation.snapshot],
    )

    if verified_page is None:
        return None

    return _build_resolved_posting(
        job_candidate=job_candidate,
        snapshot=verified_page,
    )


def _search_candidates(
    job_candidate: JobCandidate,
):
    """
    Perform exactly one generic Web Search and preserve provider ranking.
    """

    query = build_job_search_query(job_candidate)

    try:
        search_response = search_web(query)
    except Exception as error:
        _raise_technical_failure(
            job_candidate=job_candidate,
            reason=JobResolutionReason.SEARCH_ERROR,
            error=error,
        )

    top_results = list(
        search_response.results
    )[:MAX_SEARCH_RESULTS]

    filtered = filter_job_search_results(
        top_results
    )

    return [
        item.result
        for item in filtered
        if (
            item.disposition
            == SearchResultDisposition.KEEP
        )
    ]


def _resolve_via_web_search(
    *,
    job_candidate: JobCandidate,
) -> list[ResolvedJobPosting]:
    """
    Bounded retrieval pipeline:

        ONE generic Web Search
        -> conservative URL cleanup
        -> preserve search ranking
        -> fetch 5 at a time
        -> structural validation
        -> one semantic-verification call per usable batch
        -> early stop on first sufficient match
        -> at most 15 fetch attempts
        -> otherwise normal UNVERIFIED
    """

    search_results = _search_candidates(
        job_candidate
    )

    candidates = search_results[
        :MAX_FETCH_RESULTS
    ]

    # Cross-batch dedupe:
    # two different Search URLs may redirect to the same final page.
    seen_final_urls: set[str] = set()

    for batch_start in range(
        0,
        len(candidates),
        FETCH_BATCH_SIZE,
    ):
        batch = candidates[
            batch_start:
            batch_start + FETCH_BATCH_SIZE
        ]

        usable_pages: list[
            PageSnapshot
        ] = []

        for result in batch:
            try:
                snapshot = fetch_web_page(
                    result.url
                )
            except (
                HTTPException,
                URLError,
                ValueError,
                TimeoutError,
                OSError,
            ) as error:
                logger.warning(
                    "Skipping unfetchable search candidate %r "
                    "(%s: %s)",
                    result.url,
                    type(error).__name__,
                    error,
                )
                continue

            validation = validate_fetched_job_page(
                snapshot
            )

            if (
                validation.disposition
                != FetchedPageDisposition.USABLE
            ):
                continue

            final_url = (
                validation.snapshot.final_url
                or ""
            ).strip()

            if not final_url:
                continue

            if final_url in seen_final_urls:
                continue

            seen_final_urls.add(
                final_url
            )

            usable_pages.append(
                validation.snapshot
            )

        verified_page = _first_verified_page(
            job_candidate=job_candidate,
            pages=usable_pages,
        )

        if verified_page is not None:
            posting = _build_resolved_posting(
                job_candidate=job_candidate,
                snapshot=verified_page,
            )

            job_candidate.mark_verified(
                level=(
                    JobVerificationLevel.PUBLIC_POSTING
                ),
                reason=(
                    JobResolutionReason
                    .ANALYSIS_READY_PUBLIC_POSTING
                ),
            )

            return [posting]

    job_candidate.mark_unverified(
        reason=(
            JobResolutionReason
            .NO_SUITABLE_POSTING_FOUND
        ),
    )

    return []


def resolve_job_candidate(
    job_candidate: JobCandidate,
) -> list[ResolvedJobPosting]:
    """
    V1 source-aware JD Resolution / Verification policy.

    LINKEDIN / INDEED:
        skip source_url and directly run the bounded Web Search path.

    OTHER SOURCES:
        try source_url once;
        if it does not produce a verified analysis-ready posting,
        immediately fall back to the same bounded Web Search path.

    No branch enters an iterative LLM-driven Search/Reason/Act loop.
    """

    if not _source_goes_directly_to_web_search(
        job_candidate
    ):
        direct_posting = (
            _try_other_source_url_fast_path(
                job_candidate=job_candidate,
            )
        )

        if direct_posting is not None:
            job_candidate.mark_verified(
                level=(
                    JobVerificationLevel.PUBLIC_POSTING
                ),
                reason=(
                    JobResolutionReason
                    .ANALYSIS_READY_PUBLIC_POSTING
                ),
            )

            return [direct_posting]

    return _resolve_via_web_search(
        job_candidate=job_candidate
    )
