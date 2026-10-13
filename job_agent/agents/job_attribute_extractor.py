from __future__ import annotations

import re

from job_agent.models.preference import JobAttributeProfile
from job_agent.models.resolved_job_posting import ResolvedJobPosting


_LABEL_PATTERNS = {
    "industry": re.compile(
        r"(?im)^\s*industry\s*[:\-]\s*([^\n]{1,120})$"
    ),
    "company_size": re.compile(
        r"(?im)^\s*(?:company\s+size|organization\s+size)\s*[:\-]\s*([^\n]{1,120})$"
    ),
    "employment_type": re.compile(
        r"(?im)^\s*(?:employment\s+type|job\s+type)\s*[:\-]\s*([^\n]{1,120})$"
    ),
    "work_mode": re.compile(
        r"(?im)^\s*(?:work\s+mode|work\s+arrangement|workplace\s+type)\s*[:\-]\s*([^\n]{1,120})$"
    ),
}


def _first_label_value(text: str, key: str) -> str | None:
    match = _LABEL_PATTERNS[key].search(text)
    if match is None:
        return None
    value = match.group(1).strip(" .;\t")
    return value or None


def _explicit_work_mode(text: str) -> str | None:
    labelled = _first_label_value(text, "work_mode")
    if labelled:
        return labelled

    lowered = text.lower()
    # Conservative explicit statements only; no company-level inference.
    patterns = (
        (r"\b(?:this|the) (?:position|role) is (?:fully )?remote\b", "Remote"),
        (r"\b(?:this|the) (?:position|role) is hybrid\b", "Hybrid"),
        (r"\b(?:this|the) (?:position|role) is (?:fully )?on[- ]site\b", "On-site"),
    )
    for pattern, value in patterns:
        if re.search(pattern, lowered):
            return value
    return None


def _explicit_employment_type(text: str) -> str | None:
    labelled = _first_label_value(text, "employment_type")
    if labelled:
        return labelled

    lowered = text.lower()
    patterns = (
        (r"\bfull[- ]time (?:position|role|employment)\b", "Full-Time"),
        (r"\bpart[- ]time (?:position|role|employment)\b", "Part-Time"),
        (r"\bcontract (?:position|role|employment)\b", "Contract"),
        (r"\binternship (?:position|role|program)\b", "Internship"),
        (r"\btemporary (?:position|role|employment)\b", "Temporary"),
    )
    for pattern, value in patterns:
        if re.search(pattern, lowered):
            return value
    return None


def extract_grounded_job_attributes(
    resolved_posting: ResolvedJobPosting,
) -> JobAttributeProfile:
    """
    Build a conservative preference-input snapshot from the verified posting.

    Missing attributes stay None. This function does not research the company
    or ask an LLM to infer attributes from weak context.
    """

    jd_text = resolved_posting.jd_text
    return JobAttributeProfile(
        location=resolved_posting.location,
        work_mode=_explicit_work_mode(jd_text),
        employment_type=_explicit_employment_type(jd_text),
        compensation_min=None,
        compensation_max=None,
        industry=_first_label_value(jd_text, "industry"),
        company_size=_first_label_value(jd_text, "company_size"),
    )
