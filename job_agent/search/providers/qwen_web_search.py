import os
from urllib.parse import urlsplit

from job_agent.llm.client import get_llm_client
from job_agent.search.models import (
    SearchResponse,
    SearchResult,
    SearchUsage,
)


def _get_search_model() -> str:
    model = os.getenv("SEARCH_MODEL")

    if not model:
        raise ValueError(
            "SEARCH_MODEL environment variable is not set. "
            "Set it to a Qwen model that supports Responses API "
            "web_search in your Alibaba Cloud region."
        )

    return model


def _normalize_search_source_url(
    value,
) -> str | None:
    """
    Validate one URL emitted by the external web-search tool before it
    becomes one of our SearchResult domain values.

    We intentionally REJECT malformed values rather than trying to
    repair them. Search tools may occasionally return source metadata
    that is not a fetchable absolute URL (for example a relative path,
    whitespace/control characters, or other contaminated text).

    This is a deterministic boundary-validation problem, not a semantic
    matching problem, so Python is the right place to handle it.
    """

    if value is None:
        return None

    url = str(value).strip()

    if not url:
        return None

    # Raw whitespace and ASCII control characters are not valid in the
    # absolute HTTP URLs that our fetch layer expects.
    if any(
        character.isspace()
        or ord(character) < 32
        or ord(character) == 127
        for character in url
    ):
        return None

    try:
        parsed = urlsplit(url)
    except ValueError:
        return None

    if parsed.scheme.lower() not in {
        "http",
        "https",
    }:
        return None

    if not parsed.netloc:
        return None

    return url


def search_web_with_qwen(
    query: str,
) -> SearchResponse:
    """
    Execute exactly one bounded web-search operation.

    Product goal:
        Resolve an existing email-derived job lead to the employer's
        current authoritative job posting / application page.

    This search is NOT general job discovery.

    Precision policy:
    - Prefer the exact current employer-controlled posting or the
      employer's authoritative ATS / application / requisition page.
    - Search using company, full title, and location when available.
    - Allow harmless formatting / wording variants in the official
      title; do not broaden into unrelated roles.
    - Prefer a page where a person can inspect the current opening and,
      when applicable, apply for that opening.
    - Do NOT treat related news, press releases, blog posts, event
      pages, faculty/person profiles, historical announcements, or
      generic careers indexes as the target posting.
    - Do NOT use LinkedIn, Indeed, Glassdoor, ZipRecruiter, or other
      discovery aggregators as the authoritative result.
    - If no authoritative current posting can be found, do not invent
      one.

    Technical failure of the search API itself intentionally bubbles
    upward. Individual malformed source URLs returned in search metadata
    are rejected at this adapter boundary.
    """

    query = query.strip()

    if not query:
        raise ValueError(
            "Search query cannot be empty."
        )

    client = get_llm_client()
    model = _get_search_model()

    response = client.responses.create(
        model=model,
        input=(
            "You are resolving one existing job-alert lead to its "
            "authoritative employer-controlled job posting.\n\n"
            "SEARCH OBJECTIVE:\n"
            "Find the current official job posting, application page, "
            "or employer-controlled ATS/requisition page corresponding "
            "to the job lead below.\n\n"
            "IMPORTANT SEARCH RULES:\n"
            "- This is resolution, not new-job discovery.\n"
            "- Prioritize the exact role represented by the full title.\n"
            "- Use location as supporting evidence, not a reason to "
            "silently switch to another role.\n"
            "- Prefer a current job/application/requisition page.\n"
            "- Do not substitute related employer pages such as news, "
            "press releases, events, people/faculty profiles, historical "
            "announcements, program descriptions, or generic careers "
            "indexes for the actual job posting.\n"
            "- Do not treat LinkedIn, Indeed, Glassdoor, ZipRecruiter, "
            "or other job aggregators as the authoritative source.\n"
            "- Employer ATS systems count as authoritative even when "
            "their domain name differs from the employer's main site.\n"
            "- Use web search rather than model memory.\n\n"
            "JOB LEAD:\n"
            f"{query}"
        ),
        tools=[
            {
                "type": "web_search",
            }
        ],
        tool_choice="required",
        extra_body={
            "enable_thinking": False,
        },
        store=False,
    )

    urls: list[str] = []
    web_search_calls = 0

    for item in response.output:

        if item.type != "web_search_call":
            continue

        web_search_calls += 1

        action = getattr(
            item,
            "action",
            None,
        )

        if action is None:
            continue

        sources = getattr(
            action,
            "sources",
            None,
        ) or []

        for source in sources:

            normalized_url = (
                _normalize_search_source_url(
                    getattr(
                        source,
                        "url",
                        None,
                    )
                )
            )

            if not normalized_url:
                continue

            if normalized_url not in urls:
                urls.append(
                    normalized_url
                )

    usage = getattr(
        response,
        "usage",
        None,
    )

    search_usage = SearchUsage(
        input_tokens=(
            getattr(
                usage,
                "input_tokens",
                None,
            )
            if usage is not None
            else None
        ),
        output_tokens=(
            getattr(
                usage,
                "output_tokens",
                None,
            )
            if usage is not None
            else None
        ),
        total_tokens=(
            getattr(
                usage,
                "total_tokens",
                None,
            )
            if usage is not None
            else None
        ),
        web_search_calls=web_search_calls,
    )

    return SearchResponse(
        query=query,
        results=[
            SearchResult(
                url=url,
            )
            for url in urls
        ],
        usage=search_usage,
    )
