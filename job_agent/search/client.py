import os

from job_agent.search.models import SearchResponse
from job_agent.search.providers.qwen_web_search import (
    search_web_with_qwen,
)


SUPPORTED_SEARCH_PROVIDERS = {
    "qwen",
}


def search_web(
    query: str,
) -> SearchResponse:
    """
    Provider-neutral web search interface used by the application.

    The application layer should call this function rather than
    importing a provider implementation directly.

    Changing the underlying search provider should therefore not
    require changes to JD Resolution or main.py.
    """

    provider = os.getenv(
        "WEB_SEARCH_PROVIDER",
        "qwen",
    ).strip().lower()

    if provider not in SUPPORTED_SEARCH_PROVIDERS:
        raise ValueError(
            "Unsupported WEB_SEARCH_PROVIDER: "
            f"{provider}"
        )

    if provider == "qwen":
        return search_web_with_qwen(
            query=query,
        )

    raise RuntimeError(
        "Search provider routing reached an "
        "unexpected state."
    )
