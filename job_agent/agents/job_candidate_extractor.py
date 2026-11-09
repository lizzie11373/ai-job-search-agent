import logging

from job_agent.llm.client import call_llm_json
from job_agent.models.job_candidate import JobCandidate


logger = logging.getLogger(__name__)


def extract_job_candidates_from_email(
    *,
    source: str,
    message_id: str,
    email_body: str,
    email_links: list[str] | tuple[str, ...] | None = None,
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

    Fault-isolation policy:

    - A structurally invalid top-level LLM response remains a technical
      failure and raises.
    - A malformed individual extracted item is skipped so one bad candidate
      does not stop processing the rest of the email or the Agent Run.
    - A valid JobCandidate still requires both an explicitly supported
      title and company.

    Title-fidelity policy:

    - Discovery should preserve the job identity as presented in the alert.
    - Use the complete title associated with the concrete job listing/card.
    - Do not shorten, summarize, normalize, canonicalize, or rewrite titles.
    - If descriptive text later contains a shorter title-like phrase, it
      must not overwrite the complete listing/card title.

    Email-link policy:

    - email_links are optional links extracted from the same source email.
    - They may be used as provenance for source_url/source_item_id when a
      link can be associated with a concrete job from the email body.
    - They must not be used to invent a missing title or company.
    """

    if not email_body.strip():
        raise ValueError("Email body cannot be empty.")

    normalized_links = [
        str(link).strip()
        for link in (email_links or [])
        if str(link).strip()
    ]

    links_section = (
        "\n".join(f"- {link}" for link in normalized_links)
        if normalized_links
        else "(none)"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict job discovery extraction system. "
                "Extract each distinct concrete job opportunity explicitly "
                "present in the provided email body. "
                "One email may contain zero, one, or many jobs. "
                "Create one output item per distinct job. "
                "Use only information explicitly present in the email body "
                "and the extracted links from that same email. "
                "Do not infer missing facts, do not use outside knowledge, "
                "and do not merge different jobs just because they have "
                "similar titles. "
                "For each concrete job, preserve the complete job title "
                "exactly as it appears in the job listing or job card in "
                "the alert. "
                "Do not shorten, summarize, normalize, canonicalize, or "
                "rewrite the title. "
                "If the same job contains multiple title-like phrases, "
                "prefer the complete listing/card title associated with "
                "the job link over shorter title references that appear "
                "later in descriptive text. "
                "If either the job title or company cannot be explicitly "
                "identified from the email, omit that job entirely. "
                "Extracted links from the same email may be used as "
                "discovery provenance for source_url or source_item_id when "
                "they can be associated with a concrete job, but links "
                "must not be used to invent a missing title or company. "
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
                "EXTRACTED LINKS FROM THE SAME EMAIL:\n"
                f"{links_section}\n\n"
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
                "- title and company must both be explicitly supported.\n"
                "- Copy the complete title from the job listing/card exactly "
                "as presented in the alert.\n"
                "- Do not shorten, summarize, normalize, canonicalize, or "
                "rewrite the title.\n"
                "- If multiple title-like phrases refer to the same job, "
                "use the complete title associated with the listing/card "
                "and job link, not a shorter title mentioned later in "
                "descriptive text.\n"
                "- If either title or company is missing or unclear, do not "
                "return that job item.\n"
                "- Use extracted email links only when they can be associated "
                "with a concrete job from the email body.\n"
                "- Do not use a URL or domain name by itself to invent a "
                "missing title or company.\n"
                "- If a job link is uncertain, leave source_url empty.\n"
                "- Do not invent location, URLs, or IDs.\n"
                "- Ignore navigation links, unsubscribe links, ads, and "
                "general content.\n"
            ),
        },
    ]

    result = call_llm_json(messages)

    raw_jobs = result.get("jobs", [])

    if not isinstance(raw_jobs, list):
        raise ValueError("LLM response field 'jobs' must be a list.")

    job_candidates: list[JobCandidate] = []

    for index, item in enumerate(raw_jobs):
        if not isinstance(item, dict):
            logger.warning(
                "Skipping malformed extracted job candidate at index %s: "
                "item is not a JSON object.",
                index,
            )
            continue

        title = str(item.get("title", "")).strip()
        company = str(item.get("company", "")).strip()
        location = str(item.get("location", "")).strip()
        source_url = str(item.get("source_url", "")).strip()
        source_item_id = str(item.get("source_item_id", "")).strip()

        if not title:
            logger.warning(
                "Skipping malformed extracted job candidate at index %s: "
                "title is empty.",
                index,
            )
            continue

        if not company:
            logger.warning(
                "Skipping malformed extracted job candidate at index %s: "
                "company is empty.",
                index,
            )
            continue

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
