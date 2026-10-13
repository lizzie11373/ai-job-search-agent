import json

from job_agent.models.candidate import CandidateEvidenceBase
from job_agent.models.job import JobRequirement
from job_agent.models.evaluation import (
    RequirementEvidenceMapping,
    NegativeConclusionVerification,
)
from job_agent.llm.client import call_llm_json


ALLOWED_RECONCILED_SUPPORT_LEVELS = {
    "STRONG",
    "PARTIAL",
    "WEAK",
}


def reconcile_counter_evidence(
    requirement: JobRequirement,
    verification: NegativeConclusionVerification,
    evidence_base: CandidateEvidenceBase,
) -> RequirementEvidenceMapping:
    """
    Reconcile a first-pass negative conclusion when the second-pass
    verifier found counter-evidence.

    The verifier has already identified which evidence may support
    the requirement and the relationship of each evidence item.

    This function does NOT search the full evidence base again and
    does NOT redo relationship matching.

    It only determines the final requirement-level support strength.
    """

    if verification.status != "COUNTER_EVIDENCE_FOUND":
        raise ValueError(
            "Reconciliation should only run when "
            "COUNTER_EVIDENCE_FOUND."
        )

    if not verification.counter_evidence_matches:
        raise ValueError(
            "COUNTER_EVIDENCE_FOUND requires at least "
            "one counter-evidence match."
        )

    if requirement.grounding_status != "VALIDATED":
        raise ValueError(
            f"Requirement {requirement.requirement_id} "
            f"is not validated."
        )

    # ---------------------------------------------------------
    # Build a compact representation of the evidence that
    # the second-pass verifier recovered.
    # ---------------------------------------------------------

    recovered_evidence = []

    for evidence_match in verification.counter_evidence_matches:

        evidence = evidence_base.get_evidence(
            evidence_match.evidence_id
        )

        if evidence is None:
            raise ValueError(
                f"Evidence not found: "
                f"{evidence_match.evidence_id}"
            )

        if evidence.grounding_status != "VALIDATED":
            raise ValueError(
                f"Evidence {evidence.evidence_id} "
                f"is not validated."
            )

        recovered_evidence.append(
            {
                "evidence_id": evidence.evidence_id,
                "claim": evidence.claim,
                "relationship": evidence_match.relationship,
                "relationship_reason": evidence_match.reason,
            }
        )

    requirement_payload = {
        "requirement_id": requirement.requirement_id,
        "requirement": requirement.requirement,
        "category": requirement.category,
        "requirement_level": requirement.requirement_level,
    }

    # ---------------------------------------------------------
    # Narrow reconciliation task
    # ---------------------------------------------------------

    system_prompt = """
You are a strict requirement-level reconciliation system.

A first-pass matcher originally concluded that a job requirement was
NOT_CLEARLY_SUPPORTED.

A second-pass verifier then found candidate evidence that the first pass
had missed.

The evidence-to-requirement relationships have already been identified.

Your task is NOT to search for additional evidence.
Your task is NOT to re-evaluate the evidence relationships.

Your only task is to determine the final overall support level for the
job requirement using the recovered evidence provided.

Use only the information provided.

Allowed support levels:

STRONG
- The recovered evidence clearly and substantially demonstrates the
  requirement.

PARTIAL
- The recovered evidence meaningfully supports the requirement, but an
  important part of the requirement is still not clearly demonstrated.

WEAK
- The recovered evidence provides limited, indirect, or adjacent support.

Do not return NOT_CLEARLY_SUPPORTED because meaningful supporting evidence
has already been found.

Return valid JSON only.
"""

    user_prompt = f"""
Determine the final support level for this job requirement.

JOB REQUIREMENT:

{json.dumps(requirement_payload, indent=2)}

RECOVERED SUPPORTING EVIDENCE:

{json.dumps(recovered_evidence, indent=2)}

Return JSON in exactly this structure:

{{
  "support_level": "PARTIAL",
  "reason": "Overall explanation of why the recovered evidence provides this level of support."
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

    support_level = result.get(
        "support_level",
        "",
    ).strip()

    if (
        support_level
        not in ALLOWED_RECONCILED_SUPPORT_LEVELS
    ):
        raise ValueError(
            f"Invalid reconciled support level: "
            f"{support_level}"
        )

    reason = result.get(
        "reason",
        "",
    ).strip()

    return RequirementEvidenceMapping(
        requirement_id=requirement.requirement_id,

        # Important:
        # We reuse the EvidenceMatch objects already discovered
        # by the negative verifier.
        evidence_matches=verification.counter_evidence_matches,

        support_level=support_level,
        reason=reason,
    )


def finalize_mappings(
    mappings: list[RequirementEvidenceMapping],
    verifications: list[NegativeConclusionVerification],
    requirements: list[JobRequirement],
    evidence_base: CandidateEvidenceBase,
) -> list[RequirementEvidenceMapping]:
    """
    Produce final requirement-evidence mappings.

    Positive first-pass mappings:
        Keep unchanged.

    First-pass NOT_CLEARLY_SUPPORTED +
    NO_COUNTER_EVIDENCE_FOUND:
        Keep the original negative mapping.

    First-pass NOT_CLEARLY_SUPPORTED +
    COUNTER_EVIDENCE_FOUND:
        Reconcile using the recovered evidence.
    """

    requirements_by_id = {
        requirement.requirement_id: requirement
        for requirement in requirements
    }

    verifications_by_id = {
        verification.requirement_id: verification
        for verification in verifications
    }

    finalized_mappings = []

    for mapping in mappings:

        # -----------------------------------------------------
        # Case 1:
        # Positive first-pass result
        # No second-pass work required.
        # -----------------------------------------------------

        if (
            mapping.support_level
            != "NOT_CLEARLY_SUPPORTED"
        ):
            finalized_mappings.append(mapping)
            continue

        # -----------------------------------------------------
        # Every first-pass negative conclusion must have
        # gone through the negative verifier.
        # -----------------------------------------------------

        verification = verifications_by_id.get(
            mapping.requirement_id
        )

        if verification is None:
            raise ValueError(
                f"Missing negative verification for "
                f"{mapping.requirement_id}"
            )

        # -----------------------------------------------------
        # Case 2:
        # Second pass also found no supporting evidence.
        #
        # The original NOT_CLEARLY_SUPPORTED conclusion
        # survives.
        # -----------------------------------------------------

        if (
            verification.status
            == "NO_COUNTER_EVIDENCE_FOUND"
        ):
            finalized_mappings.append(mapping)
            continue

        # -----------------------------------------------------
        # Case 3:
        # Second pass found evidence that first pass missed.
        #
        # We need a narrow reconciliation call to determine
        # WEAK / PARTIAL / STRONG.
        # -----------------------------------------------------

        if (
            verification.status
            == "COUNTER_EVIDENCE_FOUND"
        ):

            requirement = requirements_by_id.get(
                mapping.requirement_id
            )

            if requirement is None:
                raise ValueError(
                    f"Requirement not found: "
                    f"{mapping.requirement_id}"
                )

            reconciled_mapping = (
                reconcile_counter_evidence(
                    requirement=requirement,
                    verification=verification,
                    evidence_base=evidence_base,
                )
            )

            finalized_mappings.append(
                reconciled_mapping
            )

            continue

        raise ValueError(
            f"Unknown verification status: "
            f"{verification.status}"
        )

    return finalized_mappings