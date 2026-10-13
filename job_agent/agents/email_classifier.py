from job_agent.llm.client import call_llm_json


def is_job_related_email(
    sender: str,
    subject: str,
    snippet: str,
) -> bool:
    """
    Classify whether email metadata indicates that the email may
    contain one or more concrete job opportunities.

    Important product boundary:

    - This step uses metadata only.
    - It does NOT read the full email body.
    - If True, the caller may then read the body and run
      JobCandidate extraction.

    The LLM handles semantic classification only. Python validates
    the returned JSON shape deterministically.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict email triage system for a job-search "
                "agent. Decide whether the provided EMAIL METADATA "
                "indicates that the email may contain one or more concrete "
                "job opportunities worth opening and inspecting. "
                "Examples that should usually be job-related include job "
                "alert digests, recommended jobs, recruiter messages about "
                "a concrete opening, and company career alerts. "
                "Do not classify general career advice, newsletters without "
                "concrete openings, interview tips, account notifications, "
                "or unrelated email as job-related. "
                "Use only the provided metadata. Do not use outside "
                "knowledge. Return JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                "Classify this email using only the metadata below.\n\n"
                f"SENDER:\n{sender}\n\n"
                f"SUBJECT:\n{subject}\n\n"
                f"SNIPPET:\n{snippet}\n\n"
                "Return JSON using exactly this structure:\n"
                "{\n"
                '  "is_job_related": true\n'
                "}\n"
            ),
        },
    ]

    result = call_llm_json(messages)

    value = result.get("is_job_related")

    if not isinstance(value, bool):
        raise ValueError(
            "LLM response field 'is_job_related' must be a boolean."
        )

    return value
