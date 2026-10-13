from dataclasses import dataclass
import json

from job_agent.llm.client import call_llm_json
from job_agent.models.job_candidate import JobCandidate
from job_agent.web.models import PageSnapshot


MAX_EVALUATION_TEXT_CHARS = 12_000
HEAD_CHARS = 8_000
TAIL_CHARS = 4_000


@dataclass(frozen=True)
class JobPageEvaluation:
    page: PageSnapshot
    is_match: bool
    sufficiently_complete: bool
    reason: str


def _page_text_for_llm(text: str) -> str:
    text = (text or "").strip()
    if len(text) <= MAX_EVALUATION_TEXT_CHARS:
        return text

    return (
        text[:HEAD_CHARS]
        + "\n\n...[middle truncated for bounded verification cost]...\n\n"
        + text[-TAIL_CHARS:]
    )


def _structured_posting_metadata(page: PageSnapshot) -> list[dict]:
    metadata = []

    for posting in getattr(page, "job_postings", ()):
        metadata.append(
            {
                "title": posting.title,
                "company": posting.company,
                "locations": list(posting.locations),
                "applicant_locations": list(posting.applicant_locations),
                "job_location_type": posting.job_location_type,
                "identifier": posting.identifier,
            }
        )

    return metadata


def evaluate_job_pages(
    *,
    job_candidate: JobCandidate,
    pages: list[PageSnapshot],
) -> list[JobPageEvaluation]:
    """
    Semantically verify a small fetched-page batch with one LLM call.

    The question is intentionally narrower than exact cross-site identity:
    Is each page sufficiently consistent with the email discovery lead AND
    sufficiently complete to support downstream job analysis?

    We do NOT require:
        - exact title string equality
        - exact company string equality
        - exact location string equality
        - the same provider job ID
        - an employer-official or ATS page
        - proof that this is the exact same cross-site posting
    """
    if not pages:
        return []

    page_payload = []
    for index, page in enumerate(pages):
        page_payload.append(
            {
                "page_index": index,
                "url": page.final_url,
                "page_title": page.title,
                "structured_job_posting": _structured_posting_metadata(page),
                "visible_text": _page_text_for_llm(page.text),
            }
        )

    lead = {
        "title": job_candidate.title,
        "company": job_candidate.company,
        "location": job_candidate.location,
        "source": job_candidate.source,
        "source_item_id": job_candidate.source_item_id,
    }

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict job-posting verification component. "
                "Evaluate each fetched public page against one discovery lead. "
                "A page passes only if BOTH conditions are true: "
                "(1) it is semantically consistent with the same job opportunity "
                "described by the lead, considering reasonable company/title/location "
                "variants; and (2) it contains a sufficiently complete job description "
                "for downstream requirement and fit analysis. "
                "Do not require exact string equality, the same provider job ID, an "
                "employer-official page, an ATS page, or proof of exact cross-site "
                "posting identity. Third-party specific job pages are allowed. "
                "Reject generic search/careers pages, articles, salary/review pages, "
                "snippets/previews that are too incomplete, materially different roles, "
                "and wrong company/location postings. Return JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                "DISCOVERY LEAD:\n"
                + json.dumps(lead, ensure_ascii=False, indent=2)
                + "\n\nFETCHED PAGES:\n"
                + json.dumps(page_payload, ensure_ascii=False, indent=2)
                + "\n\nReturn exactly this structure:\n"
                "{\n"
                '  "pages": [\n'
                "    {\n"
                '      "page_index": 0,\n'
                '      "is_match": true,\n'
                '      "sufficiently_complete": true,\n'
                '      "reason": "brief reason"\n'
                "    }\n"
                "  ]\n"
                "}\n"
                "Return one decision for every provided page_index."
            ),
        },
    ]

    result = call_llm_json(messages)
    raw_pages = result.get("pages")

    if not isinstance(raw_pages, list):
        raise ValueError("LLM response field 'pages' must be a list.")

    parsed: dict[int, JobPageEvaluation] = {}

    for item in raw_pages:
        if not isinstance(item, dict):
            raise ValueError("Each page evaluation must be a JSON object.")

        page_index = item.get("page_index")
        is_match = item.get("is_match")
        sufficiently_complete = item.get("sufficiently_complete")
        reason = str(item.get("reason", "")).strip()

        if not isinstance(page_index, int) or not (0 <= page_index < len(pages)):
            raise ValueError(f"Invalid page_index from LLM: {page_index!r}")
        if page_index in parsed:
            raise ValueError(f"Duplicate page_index from LLM: {page_index}")
        if not isinstance(is_match, bool):
            raise ValueError("LLM field 'is_match' must be boolean.")
        if not isinstance(sufficiently_complete, bool):
            raise ValueError("LLM field 'sufficiently_complete' must be boolean.")

        parsed[page_index] = JobPageEvaluation(
            page=pages[page_index],
            is_match=is_match,
            sufficiently_complete=sufficiently_complete,
            reason=reason,
        )

    missing = [index for index in range(len(pages)) if index not in parsed]
    if missing:
        raise ValueError(f"LLM omitted page decisions for indexes: {missing}")

    return [parsed[index] for index in range(len(pages))]
