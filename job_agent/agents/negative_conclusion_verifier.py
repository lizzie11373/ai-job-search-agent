import json

from job_agent.models.candidate import CandidateEvidenceBase
from job_agent.models.job import JobRequirement
from job_agent.models.evaluation import (
    EvidenceMatch,
    RequirementEvidenceMapping,
    NegativeConclusionVerification,
)
from job_agent.llm.client import call_llm_json


ALLOWED_RELATIONSHIPS = {
    "DIRECT",
    "TRANSFERABLE",
    "ADJACENT",
}

ALLOWED_VERIFICATION_STATUSES = {
    "NO_COUNTER_EVIDENCE_FOUND",
    "COUNTER_EVIDENCE_FOUND",
}


def verify_negative_conclusion(
    requirement: JobRequirement,
    evidence_base: CandidateEvidenceBase,
) -> NegativeConclusionVerification:
    """
    Challenge a first-pass NOT_CLEARLY_SUPPORTED conclusion.

    The verifier searches the COMPLETE validated candidate evidence base
    for any evidence that the first-pass matcher may have missed.
    """

    if requirement.grounding_status != "VALIDATED":
        raise ValueError(
            f"Requirement {requirement.requirement_id} "
            f"is not validated."
        )

    validated_evidence = [
        evidence
        for evidence in evidence_base.evidence_units
        if evidence.grounding_status == "VALIDATED"
    ]

    if not validated_evidence:
        raise ValueError(
            "No validated candidate evidence available "
            "for negative conclusion verification."
        )

    # ---------------------------------------
    # Build compact full-evidence input
    # ---------------------------------------

    requirement_payload = {
        "requirement_id": requirement.requirement_id,
        "requirement": requirement.requirement,
        "category": requirement.category,
        "requirement_level": requirement.requirement_level,
    }

    evidence_payload = [
        {
            "evidence_id": evidence.evidence_id,
            "claim": evidence.claim,
            "evidence_type": evidence.evidence_type,
            "source_document": evidence.source_document,
            "source_section": evidence.source_section,
        }
        for evidence in validated_evidence
    ]

    system_prompt = """
You are a strict counter-evidence verification system.

A first-pass job matcher concluded that the candidate's current evidence
base does NOT CLEARLY SUPPORT one job requirement.

Your task is NOT to repeat the original matching judgment.

Your task is to actively challenge that negative conclusion by searching
the COMPLETE candidate evidence base for evidence that may have been missed.

IMPORTANT:
This is a counter-evidence verification task, not a semantic similarity
search.

Counter-evidence must materially challenge the original
NOT_CLEARLY_SUPPORTED conclusion.

Rules:

1. Use only the requirement and candidate evidence provided.
2. Do not use outside knowledge.
3. Do not invent candidate experience, skills, responsibilities, or outcomes.
4. Search the COMPLETE evidence base.
5. Do not require exact wording or textual similarity.
6. Multiple evidence items may jointly provide support.

7. Preserve every material qualifier in the requirement, including when
   applicable:
   - explicit domain or industry
   - numeric thresholds or years of experience
   - production or deployment context
   - lifecycle stage
   - collaboration context
   - specific tools or technologies
   - credentials, certifications, or licenses

8. Evidence that is merely analogous, transferable, or conceptually similar
   does NOT by itself count as counter-evidence when a material qualifier
   remains unsupported.

9. Experience from a different role, project, or domain may be considered,
   but it only counts as counter-evidence if it materially supports the
   actual requirement rather than only demonstrating a generally similar
   capability.

10. Do not weaken, ignore, or replace explicit requirement qualifiers in
    order to create support.

Examples:

- Customer-support decision-support experience does NOT establish
  familiarity with clinical decision-support tools.

- Local implementation does NOT establish production deployment.

- Unspecified or short-duration experience does NOT satisfy an explicit
  2+ year or 4+ year requirement.

- Individual Git usage does NOT establish collaborative development
  experience when collaboration is an explicit part of the requirement.

11. Return COUNTER_EVIDENCE_FOUND only when the recovered evidence would
    make the original NOT_CLEARLY_SUPPORTED conclusion materially
    questionable.

12. If the recovered evidence is only broadly related, analogous, adjacent,
    or transferable while an essential qualifier remains unsupported,
    return NO_COUNTER_EVIDENCE_FOUND.

13. If no meaningful counter-evidence exists, return
    NO_COUNTER_EVIDENCE_FOUND.

Allowed relationship values:

DIRECT
- The evidence directly demonstrates the capability or experience required.

TRANSFERABLE
- The evidence demonstrates a capability that genuinely transfers to the
  requirement without bypassing an explicit material qualifier.

ADJACENT
- The evidence is meaningfully related to the requirement but does not
  directly or fully demonstrate it.

Return valid JSON only.
"""

    user_prompt = f"""
A first-pass matcher concluded that the following requirement was:

NOT_CLEARLY_SUPPORTED

Challenge that conclusion.

JOB REQUIREMENT:

{json.dumps(requirement_payload, indent=2)}

COMPLETE VALIDATED CANDIDATE EVIDENCE BASE:

{json.dumps(evidence_payload, indent=2)}

Search the complete evidence base for evidence that materially challenges
the NOT_CLEARLY_SUPPORTED conclusion.

Do not return COUNTER_EVIDENCE_FOUND merely because some evidence is
conceptually similar, transferable, or adjacent. Preserve all material
qualifiers in the requirement.

Return JSON in exactly this structure:

{{
  "status": "COUNTER_EVIDENCE_FOUND",
  "counter_evidence_matches": [
    {{
      "evidence_id": "E001",
      "relationship": "TRANSFERABLE",
      "reason": "Why this evidence may support the requirement."
    }}
  ],
  "reason": "Overall explanation of the verification result."
}}

If no meaningful counter-evidence exists, return:

{{
  "status": "NO_COUNTER_EVIDENCE_FOUND",
  "counter_evidence_matches": [],
  "reason": "Why the negative conclusion remains supported."
}}
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

    return _validate_and_build_verification(
        requirement=requirement,
        result=result,
        evidence_base=evidence_base,
    )


def _validate_and_build_verification(
    requirement: JobRequirement,
    result: dict,
    evidence_base: CandidateEvidenceBase,
) -> NegativeConclusionVerification:
    """
    Deterministically validate the verifier output.

    Python checks schema consistency and IDs.
    It does not redo semantic reasoning.
    """

    status = result.get(
        "status",
        "",
    ).strip()

    if status not in ALLOWED_VERIFICATION_STATUSES:
        raise ValueError(
            f"Invalid negative verification status: {status}"
        )

    valid_evidence_ids = {
        evidence.evidence_id
        for evidence in evidence_base.evidence_units
        if evidence.grounding_status == "VALIDATED"
    }

    counter_evidence_matches = []

    for raw_match in result.get(
        "counter_evidence_matches",
        [],
    ):

        evidence_id = raw_match.get(
            "evidence_id",
            "",
        ).strip()

        relationship = raw_match.get(
            "relationship",
            "",
        ).strip()

        reason = raw_match.get(
            "reason",
            "",
        ).strip()

        if evidence_id not in valid_evidence_ids:
            raise ValueError(
                f"Negative verifier returned unknown "
                f"evidence ID: {evidence_id}"
            )

        if relationship not in ALLOWED_RELATIONSHIPS:
            raise ValueError(
                f"Negative verifier returned invalid "
                f"relationship: {relationship}"
            )

        counter_evidence_matches.append(
            EvidenceMatch(
                evidence_id=evidence_id,
                relationship=relationship,
                reason=reason,
            )
        )

    # ---------------------------------------
    # Internal consistency checks
    # ---------------------------------------

    if (
        status == "NO_COUNTER_EVIDENCE_FOUND"
        and counter_evidence_matches
    ):
        raise ValueError(
            "Verifier returned NO_COUNTER_EVIDENCE_FOUND "
            "but also returned evidence matches."
        )

    if (
        status == "COUNTER_EVIDENCE_FOUND"
        and not counter_evidence_matches
    ):
        raise ValueError(
            "Verifier returned COUNTER_EVIDENCE_FOUND "
            "but returned no evidence matches."
        )

    return NegativeConclusionVerification(
        requirement_id=requirement.requirement_id,
        status=status,
        counter_evidence_matches=counter_evidence_matches,
        reason=result.get(
            "reason",
            "",
        ).strip(),
    )


def verify_negative_mappings(
    mappings: list[RequirementEvidenceMapping],
    requirements: list[JobRequirement],
    evidence_base: CandidateEvidenceBase,
) -> list[NegativeConclusionVerification]:
    """
    Run second-pass verification ONLY for mappings that received
    NOT_CLEARLY_SUPPORTED in the first pass.
    """

    requirements_by_id = {
        requirement.requirement_id: requirement
        for requirement in requirements
    }

    verifications = []

    for mapping in mappings:

        if (
            mapping.support_level
            != "NOT_CLEARLY_SUPPORTED"
        ):
            continue

        requirement = requirements_by_id.get(
            mapping.requirement_id
        )

        if requirement is None:
            raise ValueError(
                f"Requirement not found for mapping: "
                f"{mapping.requirement_id}"
            )

        verification = verify_negative_conclusion(
            requirement=requirement,
            evidence_base=evidence_base,
        )

        verifications.append(
            verification
        )

    return verifications