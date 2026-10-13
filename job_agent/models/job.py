from dataclasses import dataclass


@dataclass
class JobRequirement:
    requirement_id: str

    # Normalized atomic requirement extracted from the JD
    requirement: str

    # What kind of requirement this is
    # RESPONSIBILITY
    # EXPERIENCE
    # SKILL
    # DOMAIN_KNOWLEDGE
    # EDUCATION
    # OTHER
    category: str

    # How the JD frames this requirement
    # CORE      -> primary responsibility / role duty
    # REQUIRED  -> explicit minimum / must-have qualification
    # PREFERRED -> preferred / nice-to-have qualification
    requirement_level: str

    # Exact text from the original JD
    jd_source_text: str

    # Section where the requirement appeared
    jd_section: str

    # UNVALIDATED / VALIDATED / REJECTED
    grounding_status: str