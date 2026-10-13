from dataclasses import dataclass, field


@dataclass(frozen=True)
class SearchResult:
    """
    Provider-neutral web search result.

    Qwen Responses web_search currently guarantees a source URL.
    We intentionally do not invent title/snippet fields that the
    provider does not reliably expose in search sources.
    """

    url: str


@dataclass(frozen=True)
class SearchUsage:
    """
    Minimal usage instrumentation for cost / latency evaluation.
    """

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    web_search_calls: int = 0


@dataclass(frozen=True)
class SearchResponse:
    """
    Provider-neutral result returned to the application layer.

    Raw Qwen / OpenAI-compatible response objects never leave
    the provider adapter.
    """

    query: str
    results: list[SearchResult] = field(default_factory=list)
    usage: SearchUsage = field(default_factory=SearchUsage)
