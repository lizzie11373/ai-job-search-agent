from job_agent.llm.client import call_llm_json
from collections.abc import Iterable

from job_agent.models.email import EmailLink
from job_agent.models.job_candidate import JobCandidate


def extract_job_candidates_from_email(
    *,
    source: str,
    message_id: str,
    email_body: str,
    email_links: Iterable[EmailLink] | None = None,
) -> list[JobCandidate]:
    """
    Extract zero or more distinct jobs from one job-related email.

    One email may contain multiple jobs, so the output is a list.

    This step performs discovery extraction only. It does NOT:

    - verify that a job still exists
    - resolve an authoritative official job page
    - decide VERIFIED / UNVERIFIED
    - perform canonical job-level deduplication
    - create JobOpportunity objects

    Discovery URLs may point to a provider such as LinkedIn or Indeed.
    They are provenance only and are NOT canonical job identity.
    """

    if not email_body.strip():
        raise ValueError("Email body cannot be empty.")

    links = list(email_links or [])
    if links:
        link_context = "\n".join(
            f"- {link.text or '[no link text]'} | {link.url}"
            for link in links
        )
    else:
        link_context = "[No extracted HTML links]"

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict job discovery extraction system. "
                "Extract each distinct concrete job opportunity explicitly "
                "present in the provided email body. "
                "One email may contain zero, one, or many jobs. "
                "Create one output item per distinct job. "
                "Use only information explicitly present in the email. "
                "Do not infer missing facts, do not use outside knowledge, "
                "and do not merge different jobs just because they have "
                "similar titles. "
                "The extracted URL is discovery provenance only; it may be "
                "a provider URL and must not be treated as an authoritative "
                "official job page. "
                "Return JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                "Extract all concrete job opportunities from this email.\n\n"
                f"EMAIL BODY:\n{email_body}\n\n"
                f"EXTRACTED HTML LINKS:\n{link_context}\n\n"
                "Use the extracted links as additional email evidence. Match a "
                "job to a URL only when the surrounding link text/body supports "
                "that association.\n\n"
                "Return JSON using exactly this structure:\n"
                "{\n"
                '  "jobs": [\n'
                "    {\n"
                '      "title": "Job title",\n'
                '      "company": "Company name",\n'
                '      "location": "Location or empty string",\n'
                '      "source_url": "Job link or empty string",\n'
                '      "source_item_id": "Provider/requisition ID if explicitly present, otherwise empty string"\n'
                "    }\n"
                "  ]\n"
                "}\n\n"
                "Important rules:\n"
                "- Return one item per distinct concrete job.\n"
                "- title and company must be explicitly supported.\n"
                "- Do not invent location, URLs, or IDs.\n"
                "- Ignore navigation links, unsubscribe links, ads, and general content.\n"
            ),
        },
    ]

    result = call_llm_json(messages)

    raw_jobs = result.get("jobs", [])

    if not isinstance(raw_jobs, list):
        raise ValueError("LLM response field 'jobs' must be a list.")

    job_candidates = []

    for item in raw_jobs:
        if not isinstance(item, dict):
            raise ValueError("Each extracted job must be a JSON object.")

        title = str(item.get("title", "")).strip()
        company = str(item.get("company", "")).strip()
        location = str(item.get("location", "")).strip()
        source_url = str(item.get("source_url", "")).strip()
        source_item_id = str(item.get("source_item_id", "")).strip()

        if not title:
            raise ValueError("Extracted job title cannot be empty.")

        if not company:
            raise ValueError("Extracted job company cannot be empty.")

        job_candidates.append(
            JobCandidate(
                source=source,
                source_message_id=message_id,
                title=title,
                company=company,
                location=location or None,
                source_url=source_url or None,
                source_item_id=source_item_id or None,
            )
        )

    return job_candidates
