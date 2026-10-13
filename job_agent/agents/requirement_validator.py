import re

from job_agent.models.job import JobRequirement
from job_agent.llm.client import call_llm_json


ALLOWED_CATEGORIES = {
    "RESPONSIBILITY",
    "EXPERIENCE",
    "SKILL",
    "DOMAIN_KNOWLEDGE",
    "EDUCATION",
    "OTHER",
}


ALLOWED_REQUIREMENT_LEVELS = {
    "CORE",
    "REQUIRED",
    "PREFERRED",
}


def normalize_whitespace(
    text: str,
) -> str:
    """
    Normalize formatting-only whitespace differences.

    Example:

    "Build applications using large\\nlanguage models"

    becomes:

    "Build applications using large language models"

    This allows provenance validation to tolerate line wrapping
    while still requiring the source wording to exist in the JD.
    """

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def validate_requirement_grounding(
    requirement: str,
    category: str,
    requirement_level: str,
    jd_source_text: str,
    jd_section: str,
) -> bool:

    system_prompt = """
You are a strict job requirement grounding validator.

Your task is to determine whether an extracted job requirement
is fully supported by the provided information from the job
description.

You must evaluate ONLY:

1. the extracted requirement
2. its category
3. its requirement level
4. the provided JD source text
5. the JD section containing that source text

Do NOT use:
- outside knowledge
- assumptions about the employer
- assumptions about the role
- information not represented in the provided source text
  or section label
- plausible but unstated interpretations


============================================================
REQUIREMENT VALIDATION
============================================================

The normalized requirement must be directly supported by the
JD source text.

The requirement must not:
- exaggerate the source
- strengthen the source
- broaden the source
- materially change its meaning


============================================================
CATEGORY VALIDATION
============================================================

The category must be consistent with the requirement and its
source.

Allowed categories:

RESPONSIBILITY
EXPERIENCE
SKILL
DOMAIN_KNOWLEDGE
EDUCATION
OTHER


============================================================
REQUIREMENT LEVEL VALIDATION
============================================================

Allowed requirement levels:

CORE
REQUIRED
PREFERRED


CORE

Use for primary responsibilities or duties of the role.

A requirement located in a section such as:

- Responsibilities
- What You'll Do
- Role Responsibilities
- Duties

may support classification as CORE when the source text
describes work the person in the role will perform.

The source sentence itself does NOT need to contain the word
"core".


REQUIRED

Use for explicit minimum, mandatory, required, or must-have
qualifications.

A requirement located in a section such as:

- Minimum Qualifications
- Required Qualifications
- Requirements
- Basic Qualifications

may support classification as REQUIRED.

The individual bullet itself does NOT need to contain the word
"required" when the section clearly establishes that meaning.


PREFERRED

Use for explicitly preferred, desired, nice-to-have, bonus,
or optional qualifications.

A requirement located in a section such as:

- Preferred Qualifications
- Preferred Experience
- Nice to Have
- Bonus Qualifications

may support classification as PREFERRED.

The individual bullet itself does NOT need to contain the word
"preferred" when the section clearly establishes that meaning.


============================================================
IMPORTANT
============================================================

The JD section is part of the grounding evidence.

For example:

JD section:
Preferred Qualifications

Source text:
Experience with vector databases.

Requirement level:
PREFERRED

This may be fully grounded because the section heading provides
the preferred framing.


Return JSON only.

Required format:

{
  "is_grounded": true
}

or

{
  "is_grounded": false
}
"""

    user_prompt = f"""
EXTRACTED REQUIREMENT:

{requirement}


CATEGORY:

{category}


REQUIREMENT LEVEL:

{requirement_level}


JD SECTION:

{jd_section}


JD SOURCE TEXT:

{jd_source_text}
"""

    result = call_llm_json(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
    )

    is_grounded = result.get(
        "is_grounded"
    )

    if not isinstance(
        is_grounded,
        bool,
    ):
        raise ValueError(
            "LLM response field 'is_grounded' "
            "must be a boolean."
        )

    return is_grounded


def validate_requirements(
    requirements: list[JobRequirement],
    original_jd_text: str,
) -> list[JobRequirement]:

    if not original_jd_text.strip():
        raise ValueError(
            "Original JD text cannot be empty."
        )

    normalized_original_jd = (
        normalize_whitespace(
            original_jd_text
        )
    )

    for requirement in requirements:

        # =====================================================
        # 1. BASIC ENUM VALIDATION
        # =====================================================

        if (
            requirement.category
            not in ALLOWED_CATEGORIES
        ):
            requirement.grounding_status = (
                "REJECTED"
            )
            continue

        if (
            requirement.requirement_level
            not in ALLOWED_REQUIREMENT_LEVELS
        ):
            requirement.grounding_status = (
                "REJECTED"
            )
            continue

        # =====================================================
        # 2. REQUIRED SOURCE FIELDS
        # =====================================================

        if not requirement.jd_source_text.strip():
            requirement.grounding_status = (
                "REJECTED"
            )
            continue

        if not requirement.jd_section.strip():
            requirement.grounding_status = (
                "REJECTED"
            )
            continue

        # =====================================================
        # 3. DETERMINISTIC PROVENANCE CHECK
        # =====================================================
        #
        # Previously:
        #
        #     source_text in original_jd_text
        #
        # This was too brittle because formatting such as:
        #
        #     "large language\\nmodels"
        #
        # and:
        #
        #     "large language models"
        #
        # represent the same source wording.
        #
        # We therefore normalize WHITESPACE ONLY.
        #
        # We are NOT doing fuzzy semantic matching here.
        # The wording must still occur in the JD.
        # =====================================================

        normalized_source_text = (
            normalize_whitespace(
                requirement.jd_source_text
            )
        )

        if (
            normalized_source_text
            not in normalized_original_jd
        ):
            requirement.grounding_status = (
                "REJECTED"
            )
            continue

        # =====================================================
        # 4. SEMANTIC GROUNDING VALIDATION
        # =====================================================
        #
        # jd_section is included because section structure
        # carries explicit semantics:
        #
        # Responsibilities
        #     → CORE
        #
        # Minimum Qualifications
        #     → REQUIRED
        #
        # Preferred Qualifications
        #     → PREFERRED
        #
        # =====================================================

        is_grounded = (
            validate_requirement_grounding(
                requirement=(
                    requirement.requirement
                ),
                category=(
                    requirement.category
                ),
                requirement_level=(
                    requirement.requirement_level
                ),
                jd_source_text=(
                    requirement.jd_source_text
                ),
                jd_section=(
                    requirement.jd_section
                ),
            )
        )

        if is_grounded:

            requirement.grounding_status = (
                "VALIDATED"
            )

        else:

            requirement.grounding_status = (
                "REJECTED"
            )

    return requirements