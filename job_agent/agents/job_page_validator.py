from dataclasses import dataclass
from enum import StrEnum

from job_agent.agents.job_search_filter import is_obviously_useless_job_url
from job_agent.web.models import PageSnapshot


MIN_VISIBLE_TEXT_LENGTH = 300


class FetchedPageDisposition(StrEnum):
    """Cheap structural page check; this is not semantic verification."""

    USABLE = "USABLE"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ValidatedFetchedPage:
    snapshot: PageSnapshot
    disposition: FetchedPageDisposition
    reason: str


def validate_fetched_job_page(
    snapshot: PageSnapshot,
) -> ValidatedFetchedPage:
    """
    Decide only whether a fetched page is worth sending to the LLM verifier.

    The validator intentionally does NOT decide whether the page matches the
    discovery lead. Fuzzy company/title/location/role alignment belongs to the
    LLM semantic verification step.
    """
    if snapshot.status_code != 200:
        return ValidatedFetchedPage(
            snapshot=snapshot,
            disposition=FetchedPageDisposition.REJECTED,
            reason=f"HTTP status {snapshot.status_code}.",
        )

    if snapshot.content_type and snapshot.content_type not in {
        "text/html",
        "application/xhtml+xml",
    }:
        return ValidatedFetchedPage(
            snapshot=snapshot,
            disposition=FetchedPageDisposition.REJECTED,
            reason="Fetched content is not HTML.",
        )

    if is_obviously_useless_job_url(snapshot.final_url):
        redirect_note = ""
        if snapshot.requested_url != snapshot.final_url:
            redirect_note = f" Redirected to {snapshot.final_url}."

        return ValidatedFetchedPage(
            snapshot=snapshot,
            disposition=FetchedPageDisposition.REJECTED,
            reason=f"Final URL is generic/non-posting.{redirect_note}",
        )

    text = (snapshot.text or "").strip()
    if len(text) < MIN_VISIBLE_TEXT_LENGTH:
        return ValidatedFetchedPage(
            snapshot=snapshot,
            disposition=FetchedPageDisposition.REJECTED,
            reason="Too little visible text for a usable JD candidate.",
        )

    return ValidatedFetchedPage(
        snapshot=snapshot,
        disposition=FetchedPageDisposition.USABLE,
        reason="Specific reachable page with enough text for semantic verification.",
    )
