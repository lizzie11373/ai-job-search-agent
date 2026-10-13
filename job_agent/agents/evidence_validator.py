from job_agent.models.candidate import EvidenceUnit
from job_agent.llm.client import call_llm_json


def validate_claim_grounding(
    claim: str,
    source_text: str,
) -> bool:
    """
    Use an LLM to determine whether a claim is fully supported
    by the provided source text.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict evidence grounding validator. "
                "Your task is to determine whether a candidate claim "
                "is fully supported by the provided source text. "
                "Do not use outside knowledge. "
                "Do not make assumptions. "
                "Do not treat plausible inference as evidence. "
                "Return JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                "Validate the following candidate evidence.\n\n"
                f"SOURCE TEXT:\n{source_text}\n\n"
                f"CLAIM:\n{claim}\n\n"
                "Return JSON in exactly this structure:\n"
                '{\n'
                '  "supported": true\n'
                '}\n\n'
                "Set supported to true only if the source text "
                "directly supports the full claim."
            ),
        },
    ]

    result = call_llm_json(messages)

    return result.get("supported") is True


def validate_evidence(
    evidence_units: list[EvidenceUnit],
    original_document_text: str,
) -> list[EvidenceUnit]:
    """
    Validate extracted evidence before it enters CandidateEvidenceBase.

    Validation has two layers:

    1. Deterministic provenance validation.
    2. LLM semantic grounding validation.
    """

    validated_evidence = []

    for evidence in evidence_units:

        # --------------------------------------------------
        # 1. Deterministic provenance validation
        # --------------------------------------------------

        if not evidence.source_text:
            evidence.grounding_status = "REJECTED"
            continue

        if evidence.source_text not in original_document_text:
            evidence.grounding_status = "REJECTED"
            continue

        # --------------------------------------------------
        # 2. Semantic grounding validation
        # --------------------------------------------------

        semantic_grounding_passed = validate_claim_grounding(
            claim=evidence.claim,
            source_text=evidence.source_text,
        )

        if not semantic_grounding_passed:
            evidence.grounding_status = "REJECTED"
            continue

        # --------------------------------------------------
        # 3. Evidence passed all validation gates
        # --------------------------------------------------

        evidence.grounding_status = "VALIDATED"
        validated_evidence.append(evidence)

    return validated_evidence