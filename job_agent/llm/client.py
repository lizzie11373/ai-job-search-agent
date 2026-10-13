import json
import os

from dotenv import load_dotenv


load_dotenv()


def get_llm_client():
    """Create and return the shared OpenAI-compatible Qwen API client."""

    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The 'openai' package is required for live LLM calls. "
            "Install project requirements before running live workflows."
        ) from exc

    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_BASE_URL")

    if not api_key:
        raise ValueError(
            "DASHSCOPE_API_KEY environment variable is not set."
        )
    if not base_url:
        raise ValueError(
            "DASHSCOPE_BASE_URL environment variable is not set."
        )

    return OpenAI(api_key=api_key, base_url=base_url)


def call_llm(
    messages: list[dict[str, str]],
    model: str | None = None,
) -> str:
    if model is None:
        model = os.getenv("GENERATION_MODEL")
    if not model:
        raise ValueError(
            "GENERATION_MODEL environment variable is not set."
        )

    client = get_llm_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        extra_body={"enable_thinking": False},
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("LLM returned an empty response.")
    return content


def call_llm_json(
    messages: list[dict[str, str]],
    model: str | None = None,
) -> dict:
    if model is None:
        model = os.getenv("GENERATION_MODEL")
    if not model:
        raise ValueError(
            "GENERATION_MODEL environment variable is not set."
        )

    client = get_llm_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        extra_body={"enable_thinking": False},
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("LLM returned an empty response.")
    return json.loads(content)
