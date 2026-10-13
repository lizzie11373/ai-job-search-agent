from job_agent.models.job import JobRequirement
from job_agent.llm.client import call_llm_json


ALLOWED_CATEGORIES = {
    "RESPONSIBILITY",
    "EXPERIENCE",
    "SKILL",
    "DOMAIN_KNOWLEDGE",
    "EDUCATION",
    "LICENSE",
    "CERTIFICATION",
    "OTHER",
}


CATEGORY_ALIASES = {
    "LICENSURE": "LICENSE",
    "LICENSES": "LICENSE",
    "PROFESSIONAL_LICENSE": "LICENSE",
    "CERTIFICATE": "CERTIFICATION",
    "CERTIFICATES": "CERTIFICATION",
    "CERTIFICATIONS": "CERTIFICATION",
    "CREDENTIAL": "CERTIFICATION",
    "CREDENTIALS": "CERTIFICATION",
}


ALLOWED_REQUIREMENT_LEVELS = {
    "CORE",
    "REQUIRED",
    "PREFERRED",
}


def _normalize_category(value: object) -> str:
    """
    Normalize LLM-produced requirement categories without allowing a
    non-critical taxonomy mismatch to abort an entire Agent Run.

    Requirement category is descriptive metadata. Requirement Fit is
    driven by requirement_level + evidence support, so an unfamiliar
    category can safely fall back to OTHER while preserving the actual
    requirement text for downstream validation and matching.
    """
    category = str(value or "").strip().upper().replace(" ", "_")
    category = CATEGORY_ALIASES.get(category, category)

    if category in ALLOWED_CATEGORIES:
        return category

    return "OTHER"


def extract_requirements_from_jd(
    jd_text: str,
) -> list[JobRequirement]:

    if not jd_text.strip():
        raise ValueError(
            "JD text cannot be empty."
        )

    system_prompt = """
You are a strict job requirement extraction system.

Your task is to extract atomic job requirements from a
job description.

Use ONLY information explicitly stated in the provided
job description.

Do NOT:
- infer unstated requirements
- strengthen wording
- add outside knowledge
- guess what the employer probably wants
- combine unrelated requirements into one item

Each extracted requirement must represent one atomic
requirement or responsibility.

For every requirement, return:

1. requirement
   A concise normalized statement of the requirement.

2. category
   Must be exactly one of:
   - RESPONSIBILITY
   - EXPERIENCE
   - SKILL
   - DOMAIN_KNOWLEDGE
   - EDUCATION
   - LICENSE
   - CERTIFICATION
   - OTHER

   Use LICENSE for professional licensure requirements.
   Use CERTIFICATION for explicitly required or preferred
   professional certifications or credentials.

3. requirement_level
   Must be exactly one of:

   CORE
   Use for primary responsibilities or core duties of the role.

   REQUIRED
   Use for explicitly required, minimum, mandatory,
   must-have, or minimum qualification requirements.

   PREFERRED
   Use only when the job description explicitly presents
   something as preferred, desired, nice-to-have, a plus,
   or equivalent wording.

4. jd_source_text
   Copy the exact supporting text from the job description.
   This must be verbatim and directly support the extracted
   requirement.

5. jd_section
   The section of the job description where the requirement
   appears, such as:
   - Responsibilities
   - Minimum Qualifications
   - Preferred Qualifications
   - About the Role
   - Other

Important rules:

- Do not classify something as PREFERRED unless the JD
  explicitly frames it that way.
- A primary job responsibility should generally be CORE.
- An explicit minimum qualification should generally be REQUIRED.
- Preserve the distinction between what the candidate will DO
  and what the candidate must HAVE.
- Every requirement must have direct source evidence.
- If the JD does not support a requirement, do not extract it.

Return JSON only.

Required JSON format:

{
  "requirements": [
    {
      "requirement": "...",
      "category": "RESPONSIBILITY",
      "requirement_level": "CORE",
      "jd_source_text": "...",
      "jd_section": "Responsibilities"
    }
  ]
}
"""

    user_prompt = f"""
JOB DESCRIPTION:

{jd_text}
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

    raw_requirements = result.get(
        "requirements",
        []
    )

    if not isinstance(
        raw_requirements,
        list,
    ):
        raise ValueError(
            "LLM response field 'requirements' "
            "must be a list."
        )

    requirements = []

    for index, item in enumerate(
        raw_requirements,
        start=1,
    ):

        if not isinstance(
            item,
            dict,
        ):
            raise ValueError(
                "Each requirement must be "
                "a JSON object."
            )

        requirement = str(
            item.get(
                "requirement",
                "",
            )
        ).strip()

        category = _normalize_category(
            item.get(
                "category",
                "",
            )
        )

        requirement_level = str(
            item.get(
                "requirement_level",
                "",
            )
        ).strip().upper()

        jd_source_text = str(
            item.get(
                "jd_source_text",
                "",
            )
        ).strip()

        jd_section = str(
            item.get(
                "jd_section",
                "",
            )
        ).strip()

        # =====================================================
        # BASIC OUTPUT VALIDATION
        # =====================================================

        if not requirement:
            raise ValueError(
                "Requirement text cannot be empty."
            )

        if (
            requirement_level
            not in ALLOWED_REQUIREMENT_LEVELS
        ):
            raise ValueError(
                "Unknown requirement level: "
                f"{requirement_level}"
            )

        if not jd_source_text:
            raise ValueError(
                "JD source text cannot be empty."
            )

        if not jd_section:
            jd_section = "Other"

        requirement_id = (
            f"R{index:03d}"
        )

        requirements.append(
            JobRequirement(
                requirement_id=(
                    requirement_id
                ),
                requirement=(
                    requirement
                ),
                category=(
                    category
                ),
                requirement_level=(
                    requirement_level
                ),
                jd_source_text=(
                    jd_source_text
                ),
                jd_section=(
                    jd_section
                ),
                grounding_status=(
                    "UNVALIDATED"
                ),
            )
        )

    return requirements
