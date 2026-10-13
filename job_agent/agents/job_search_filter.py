from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import parse_qs, urlparse, urlunparse

from job_agent.search.models import SearchResult


class SearchResultDisposition(StrEnum):
    """Cheap URL-level routing only; no semantic job matching happens here."""

    KEEP = "KEEP"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class FilteredSearchResult:
    result: SearchResult
    disposition: SearchResultDisposition
    reason: str


_GENERIC_ROOT_PATHS = {
    "",
    "jobs",
    "careers",
    "career",
    "search",
    "job-search",
    "jobsearch",
    "openings",
}

_GENERIC_TWO_SEGMENT_PATHS = {
    ("jobs", "search"),
    ("careers", "search"),
    ("jobs", "search-results"),
    ("careers", "search-results"),
}

_NON_POSTING_TERMINALS = {
    "about",
    "contact",
    "faq",
    "help",
    "review",
    "reviews",
    "salary",
    "salaries",
    "career-advice",
}


def _normalized_url_for_dedupe(url: str) -> str:
    parsed = urlparse(url.strip())
    path = parsed.path.rstrip("/") or "/"
    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            parsed.params,
            parsed.query,
            "",  # fragments do not identify a different posting
        )
    )


def is_obviously_useless_job_url(url: str) -> bool:
    """
    Reject only URLs that are clearly not specific job-posting candidates.

    This is deliberately conservative. Specific pages on aggregators such as
    Indeed, LinkedIn, ZipRecruiter, or other third-party sites are NOT rejected
    merely because of their domain.
    """
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return True

    if parsed.scheme.lower() not in {"http", "https"}:
        return True
    if not parsed.hostname:
        return True

    segments = [segment.lower() for segment in parsed.path.split("/") if segment]

    if not segments:
        return True

    if len(segments) == 1 and segments[0] in _GENERIC_ROOT_PATHS:
        return True

    if len(segments) == 2 and tuple(segments) in _GENERIC_TWO_SEGMENT_PATHS:
        return True

    if segments[-1] in _NON_POSTING_TERMINALS:
        return True

    # Common search/index URL shapes. Keep this intentionally narrow.
    query = parse_qs(parsed.query, keep_blank_values=True)
    if segments[-1] in {"jobs", "search", "search-results"} and any(
        key.lower() in {"q", "query", "search", "keyword", "keywords"}
        for key in query
    ):
        return True

    return False


def filter_job_search_results(
    search_results: list[SearchResult],
) -> list[FilteredSearchResult]:
    """
    Preserve provider ranking while removing only obvious garbage/duplicates.

    Important boundary:
        - no title matching
        - no company matching
        - no location matching
        - no employer/ATS preference
        - no whole-domain aggregator rejection
        - no LLM call
    """
    filtered: list[FilteredSearchResult] = []
    seen: set[str] = set()

    for result in search_results:
        url = (result.url or "").strip()

        if not url:
            filtered.append(
                FilteredSearchResult(
                    result=result,
                    disposition=SearchResultDisposition.REJECTED,
                    reason="Empty URL.",
                )
            )
            continue

        if is_obviously_useless_job_url(url):
            filtered.append(
                FilteredSearchResult(
                    result=result,
                    disposition=SearchResultDisposition.REJECTED,
                    reason="Obvious generic/index/non-posting URL.",
                )
            )
            continue

        normalized = _normalized_url_for_dedupe(url)
        if normalized in seen:
            filtered.append(
                FilteredSearchResult(
                    result=result,
                    disposition=SearchResultDisposition.REJECTED,
                    reason="Duplicate URL.",
                )
            )
            continue

        seen.add(normalized)
        filtered.append(
            FilteredSearchResult(
                result=result,
                disposition=SearchResultDisposition.KEEP,
                reason="Specific-enough URL worth one fetch attempt.",
            )
        )

    return filtered
