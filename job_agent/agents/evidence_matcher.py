import logging

from job_agent.models.candidate import (
    CandidateEvidenceBase,
)
from job_agent.models.job import (
    JobRequirement,
)
from job_agent.models.evaluation import (
    EvidenceMatch,
    RequirementEvidenceMapping,
)
from job_agent.llm.client import (
    call_llm_json,
)


logger = logging.getLogger(__name__)


ALLOWED_SUPPORT_LEVELS = {
    "STRONG",
    "PARTIAL",
    "WEAK",
    "NOT_CLEARLY_SUPPORTED",
}


ALLOWED_RELATIONSHIPS = {
    "DIRECT",
    "TRANSFERABLE",
    "ADJACENT",
}


def match_requirements_to_evidence(
    requirements: list[JobRequirement],
    evidence_base: CandidateEvidenceBase,
) -> list[RequirementEvidenceMapping]:

    # =========================================================
    # 1. FILTER TO TRUSTED INPUTS ONLY
    # =========================================================
    #
    # Matching must happen only after both sides have already
    # passed grounding validation.
    #
    # JD side:
    #   JobRequirement.grounding_status == "VALIDATED"
    #
    # Candidate side:
    #   EvidenceUnit.grounding_status == "VALIDATED"
    #
    # This follows our pipeline principle:
    #
    #   Validate before reasoning.
    # =========================================================

    validated_requirements = [
        requirement
        for requirement in requirements
        if requirement.grounding_status
        == "VALIDATED"
    ]

    validated_evidence = [
        evidence
        for evidence
        in evidence_base.evidence_units
        if evidence.grounding_status
        == "VALIDATED"
    ]

    if not validated_requirements:
        raise ValueError(
            "No validated job requirements "
            "available for matching."
        )

    # Candidate evidence may theoretically be empty.
    #
    # We allow that case because the correct result would then
    # be NOT_CLEARLY_SUPPORTED for every requirement.
    #
    # Therefore we do NOT raise an error here when
    # validated_evidence is empty.

    # =========================================================
    # 2. BUILD COMPACT REQUIREMENT PAYLOAD
    # =========================================================
    #
    # We use normalized validated requirements for reasoning.
    #
    # jd_source_text is retained in the data model for
    # provenance and auditing, but it does not need to be
    # repeatedly sent into the matcher.
    #
    # IMPORTANT:
    # "importance" no longer exists.
    # =========================================================

    requirement_payload = []

    for requirement in validated_requirements:

        requirement_payload.append(
            {
                "requirement_id": (
                    requirement.requirement_id
                ),
                "requirement": (
                    requirement.requirement
                ),
                "category": (
                    requirement.category
                ),
                "requirement_level": (
                    requirement.requirement_level
                ),
            }
        )

    # =========================================================
    # 3. BUILD COMPLETE CANDIDATE EVIDENCE PAYLOAD
    # =========================================================
    #
    # Critical architecture decision:
    #
    # DO NOT use embedding retrieval or Top-K filtering here.
    #
    # Every validated candidate claim is included.
    #
    # Reason:
    # The matching task is not:
    #
    #   "Find the most semantically similar evidence."
    #
    # It is:
    #
    #   "Determine whether the candidate's complete validated
    #    evidence base supports each job requirement."
    #
    # Complementary or transferable evidence could otherwise
    # be lost during retrieval.
    #
    # source_text is NOT sent by default because claim is the
    # compact validated representation used for reasoning.
    #
    # Original source text remains stored for provenance.
    # =========================================================

    evidence_payload = []

    for evidence in validated_evidence:

        evidence_payload.append(
            {
                "evidence_id": (
                    evidence.evidence_id
                ),
                "claim": (
                    evidence.claim
                ),
                "evidence_type": (
                    evidence.evidence_type
                ),
                "source_document": (
                    evidence.source_document
                ),
                "source_section": (
                    evidence.source_section
                ),
            }
        )

    # =========================================================
    # 4. MATCHING PROMPT
    # =========================================================

    system_prompt = """
You are a strict requirement-to-candidate-evidence matching system.

Your task is to evaluate EVERY provided job requirement against
the COMPLETE provided candidate evidence base.

Use ONLY the information provided in this input.

Do NOT use:
- outside knowledge
- assumptions about the candidate
- assumptions about the employer
- general knowledge about technologies
- plausible but unsupported candidate experience
- information that is not explicitly represented in the
  candidate evidence base

IMPORTANT:

The candidate evidence provided to you has already passed
grounding validation.

The job requirements provided to you have already passed
grounding validation.

Your task is therefore NOT to revalidate the original source
documents.

Your task is to determine the semantic relationship between
each validated job requirement and the complete validated
candidate evidence base.


============================================================
REQUIREMENT COVERAGE
============================================================

You MUST return exactly one result for EVERY job requirement.

Do not:
- skip requirements
- merge requirements
- invent new requirements
- change requirement IDs

Each requirement must receive exactly one support level.


============================================================
SUPPORT LEVELS
============================================================

The support_level must be exactly one of:

STRONG

Use when the candidate evidence clearly and substantially
supports the requirement.

The evidence should demonstrate close alignment with the
capability, responsibility, experience, skill, or knowledge
being requested.


PARTIAL

Use when the candidate evidence supports a meaningful portion
of the requirement, but an important part is missing,
narrower, less complete, or not clearly demonstrated.


WEAK

Use when there is some relevant evidence, but the connection
is limited, indirect, adjacent, or significantly weaker than
what the requirement asks for.


NOT_CLEARLY_SUPPORTED

Use when the current candidate evidence base does not clearly
support the requirement.

IMPORTANT:

NOT_CLEARLY_SUPPORTED does NOT mean:

"The candidate definitely does not have this capability."

It means only:

"The current validated evidence base does not clearly support
this requirement."


============================================================
EVIDENCE RELATIONSHIPS
============================================================

For evidence that supports a requirement, relationship must
be exactly one of:

DIRECT

The evidence directly demonstrates the capability,
experience, responsibility, skill, or knowledge requested.


TRANSFERABLE

The evidence demonstrates a meaningfully transferable
capability from another context or domain.

The transfer must be supported by the provided evidence.
Do not invent transferability merely because it sounds
plausible.


ADJACENT

The evidence is relevant and related, but does not directly
or strongly demonstrate the requested requirement.

CRITICAL FIELD-SEPARATION RULE:

relationship and support_level are DIFFERENT fields with
different allowed values.

Never use any support-level value as an evidence relationship.
In particular, STRONG, PARTIAL, WEAK, and
NOT_CLEARLY_SUPPORTED are NOT valid relationship values.

Every evidence_matches[].relationship must be exactly one of:
DIRECT, TRANSFERABLE, ADJACENT.


============================================================
IMPORTANT MATCHING RULES
============================================================

1. Evaluate each requirement against the COMPLETE candidate
   evidence base.

2. Do not rely only on obvious keyword overlap.

3. Look for complementary evidence across multiple candidate
   claims when appropriate.

4. A requirement may be supported by multiple evidence items.

5. Use only evidence IDs that actually exist in the provided
   candidate evidence base.

6. If support_level is NOT_CLEARLY_SUPPORTED:

   evidence_matches MUST be an empty list.

7. If support_level is:

   STRONG
   PARTIAL
   WEAK

   evidence_matches MUST contain at least one valid evidence
   item.

8. Do not exaggerate evidence.

9. Do not convert adjacent evidence into direct evidence just
   because the candidate appears promising.

10. Do not treat absence of evidence as evidence of absence.

11. The reason must explain why the selected evidence does or
    does not support the requirement.

12. Keep reasons concise, specific, and grounded in the
    provided candidate evidence.


============================================================
OUTPUT FORMAT
============================================================

Return JSON only.

Required format:

{
  "mappings": [
    {
      "requirement_id": "R001",
      "support_level": "STRONG",
      "reason": "...",
      "evidence_matches": [
        {
          "evidence_id": "E001",
          "relationship": "DIRECT",
          "reason": "..."
        }
      ]
    }
  ]
}

For NOT_CLEARLY_SUPPORTED:

{
  "requirement_id": "R002",
  "support_level": "NOT_CLEARLY_SUPPORTED",
  "reason": "...",
  "evidence_matches": []
}
"""

    user_prompt = f"""
VALIDATED JOB REQUIREMENTS:

{requirement_payload}


COMPLETE VALIDATED CANDIDATE EVIDENCE BASE:

{evidence_payload}
"""

    # =========================================================
    # 5. LLM SEMANTIC MATCHING
    # =========================================================

    base_messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    result = call_llm_json(
        messages=base_messages
    )

    raw_mappings = result.get(
        "mappings",
        []
    )

    if not isinstance(
        raw_mappings,
        list,
    ):
        raise ValueError(
            "LLM response field 'mappings' "
            "must be a list."
        )

    # =========================================================
    # 6. BUILD EXPECTED ID SETS
    # =========================================================

    expected_requirement_ids = {
        requirement.requirement_id
        for requirement
        in validated_requirements
    }

    valid_evidence_ids = {
        evidence.evidence_id
        for evidence
        in validated_evidence
    }

    # =========================================================
    # 7. PARSE + DETERMINISTIC OUTPUT VALIDATION
    #    WITH REQUIREMENT-LEVEL FAULT ISOLATION
    # =========================================================
    #
    # Reliability policy:
    #
    # A malformed mapping for ONE requirement must not stop the
    # rest of the opportunity or the overall Agent Run.
    #
    # We therefore:
    #
    # - keep the strict deterministic contract
    # - never silently reinterpret invalid enum values
    # - never invent missing evidence
    # - conservatively fall back the affected requirement to:
    #
    #       NOT_CLEARLY_SUPPORTED + []
    #
    # - continue processing later requirements
    #
    # Top-level failures such as an unusable LLM response,
    # network/API errors, or mappings not being a list still
    # remain technical failures and are allowed to raise.
    # =========================================================

    mappings = []
    seen_requirement_ids = set()

    def conservative_fallback(
        requirement_id: str,
        error: object,
    ) -> RequirementEvidenceMapping:
        logger.warning(
            "Falling back requirement %s to "
            "NOT_CLEARLY_SUPPORTED after invalid matcher output: %s",
            requirement_id,
            error,
        )

        return RequirementEvidenceMapping(
            requirement_id=requirement_id,
            evidence_matches=[],
            support_level="NOT_CLEARLY_SUPPORTED",
            reason=(
                "Evidence matching for this requirement could not "
                "be completed reliably, so it was conservatively "
                "treated as not clearly supported."
            ),
        )

    for item_index, item in enumerate(raw_mappings):

        if not isinstance(item, dict):
            logger.warning(
                "Skipping malformed matcher item at index %s: "
                "expected a JSON object.",
                item_index,
            )
            continue

        requirement_id = str(
            item.get("requirement_id", "")
        ).strip()

        if not requirement_id:
            logger.warning(
                "Skipping matcher item at index %s: "
                "requirement_id is empty.",
                item_index,
            )
            continue

        if requirement_id not in expected_requirement_ids:
            logger.warning(
                "Skipping matcher item with unknown "
                "requirement_id %s.",
                requirement_id,
            )
            continue

        if requirement_id in seen_requirement_ids:
            logger.warning(
                "Skipping duplicate matcher item for "
                "requirement_id %s.",
                requirement_id,
            )
            continue

        try:
            support_level = str(
                item.get("support_level", "")
            ).strip().upper()

            reason = str(
                item.get("reason", "")
            ).strip()

            raw_evidence_matches = item.get(
                "evidence_matches",
                [],
            )

            if support_level not in ALLOWED_SUPPORT_LEVELS:
                raise ValueError(
                    "Unknown support level: "
                    f"{support_level}"
                )

            if not reason:
                raise ValueError(
                    "Mapping reason cannot be empty "
                    f"for {requirement_id}."
                )

            if not isinstance(raw_evidence_matches, list):
                raise ValueError(
                    "evidence_matches must be "
                    f"a list for {requirement_id}."
                )

            evidence_matches = []
            seen_evidence_ids = set()

            for raw_match in raw_evidence_matches:

                if not isinstance(raw_match, dict):
                    raise ValueError(
                        "Each evidence match must "
                        "be a JSON object."
                    )

                evidence_id = str(
                    raw_match.get("evidence_id", "")
                ).strip()

                relationship = str(
                    raw_match.get("relationship", "")
                ).strip().upper()

                match_reason = str(
                    raw_match.get("reason", "")
                ).strip()

                if not evidence_id:
                    raise ValueError(
                        "Evidence match evidence_id "
                        "cannot be empty."
                    )

                if evidence_id not in valid_evidence_ids:
                    raise ValueError(
                        "LLM returned unknown "
                        "evidence_id: "
                        f"{evidence_id}"
                    )

                if evidence_id in seen_evidence_ids:
                    raise ValueError(
                        "Duplicate evidence match "
                        f"{evidence_id} "
                        f"for requirement "
                        f"{requirement_id}."
                    )

                seen_evidence_ids.add(evidence_id)

                if relationship not in ALLOWED_RELATIONSHIPS:
                    raise ValueError(
                        "Unknown evidence relationship: "
                        f"{relationship}"
                    )

                if not match_reason:
                    raise ValueError(
                        "Evidence match reason "
                        "cannot be empty."
                    )

                evidence_matches.append(
                    EvidenceMatch(
                        evidence_id=evidence_id,
                        relationship=relationship,
                        reason=match_reason,
                    )
                )

            if support_level == "NOT_CLEARLY_SUPPORTED":
                if evidence_matches:
                    raise ValueError(
                        "NOT_CLEARLY_SUPPORTED "
                        "must have an empty "
                        "evidence_matches list "
                        f"for {requirement_id}."
                    )
            else:
                if not evidence_matches:
                    raise ValueError(
                        f"{support_level} "
                        "must contain at least one "
                        "evidence match "
                        f"for {requirement_id}."
                    )

            mapping = RequirementEvidenceMapping(
                requirement_id=requirement_id,
                evidence_matches=evidence_matches,
                support_level=support_level,
                reason=reason,
            )

        except (ValueError, TypeError) as exc:
            mapping = conservative_fallback(
                requirement_id,
                exc,
            )

        mappings.append(mapping)
        seen_requirement_ids.add(requirement_id)

    # =========================================================
    # 9. REQUIREMENT COMPLETENESS FALLBACK
    # =========================================================
    #
    # Missing or unusable requirement mappings are preserved
    # conservatively instead of aborting the opportunity.
    # =========================================================

    for requirement in validated_requirements:

        if requirement.requirement_id in seen_requirement_ids:
            continue

        mappings.append(
            conservative_fallback(
                requirement.requirement_id,
                "Matcher did not return a usable mapping "
                "for this requirement.",
            )
        )

        seen_requirement_ids.add(
            requirement.requirement_id
        )

    # =========================================================
    # 10. PRESERVE REQUIREMENT ORDER
    # =========================================================
    #
    # LLM output order is not trusted.
    #
    # Return mappings in the same order as the validated
    # requirements.
    # =========================================================

    mapping_by_requirement_id = {
        mapping.requirement_id: mapping
        for mapping in mappings
    }

    ordered_mappings = [
        mapping_by_requirement_id[
            requirement.requirement_id
        ]
        for requirement
        in validated_requirements
    ]

    return ordered_mappings