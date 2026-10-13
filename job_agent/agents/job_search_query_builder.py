from job_agent.models.job_candidate import JobCandidate


def _quote(value: str) -> str:
    cleaned = " ".join(value.split())
    return f'"{cleaned}"'


def build_job_search_query(job_candidate: JobCandidate) -> str:
    """
    Build the single generic Web Search query used by JD Resolution V1.

    The query uses only discovery identity signals:
        - company
        - title
        - location, when available

    It intentionally does NOT add "careers", "jobs", ATS names, provider
    job IDs, candidate evidence, preferences, or fit signals. Search should
    maximize recall; semantic verification happens only after pages are fetched.
    """
    company = job_candidate.company.strip()
    title = job_candidate.title.strip()

    if not company:
        raise ValueError("JobCandidate company cannot be empty.")
    if not title:
        raise ValueError("JobCandidate title cannot be empty.")

    parts = [_quote(company), _quote(title)]

    location = (job_candidate.location or "").strip()
    if location:
        parts.append(_quote(location))

    return " ".join(parts)
