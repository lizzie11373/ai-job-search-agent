from job_agent.models.candidate import EvidenceUnit
from job_agent.llm.client import call_llm_json


def extract_evidence_from_document(
    document_name: str,
    document_text: str,
) -> list[EvidenceUnit]:
    """
    Extract factual candidate evidence from a user-provided document.

    The LLM performs semantic information extraction only.
    Python assigns IDs and workflow state deterministically.

    Every extracted evidence unit starts as UNVALIDATED and must
    pass the evidence validation pipeline before entering the
    CandidateEvidenceBase.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict candidate evidence extraction system. "
                "Extract only factual evidence explicitly supported by the "
                "user-provided document. "
                "Do not infer missing facts. "
                "Do not exaggerate responsibilities, impact, ownership, "
                "technical complexity, or outcomes. "
                "Do not use outside knowledge. "
                "Each claim must be directly supported by source_text. "
                "source_text must be copied verbatim from the document. "
                "Return JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                "Extract candidate evidence from the following document.\n\n"
                f"DOCUMENT NAME:\n{document_name}\n\n"
                f"DOCUMENT:\n{document_text}\n\n"
                "Return JSON using exactly this structure:\n"
                "{\n"
                '  "evidence_units": [\n'
                "    {\n"
                '      "claim": "A conservative factual claim",\n'
                '      "source_section": "Section name",\n'
                '      "source_text": "Exact verbatim text from the document",\n'
                '      "evidence_type": "PROJECT"\n'
                "    }\n"
                "  ]\n"
                "}\n\n"
                "Important rules:\n"
                "- Extract only facts explicitly supported by the document.\n"
                "- Keep claims conservative and specific.\n"
                "- Never strengthen participation into leadership.\n"
                "- Never invent metrics or outcomes.\n"
                "- source_text must appear verbatim in the original document.\n"
            ),
        },
    ]

    result = call_llm_json(messages)

    raw_evidence_units = result.get("evidence_units", [])

    evidence_units = []

    for index, item in enumerate(raw_evidence_units, start=1):

        evidence = EvidenceUnit(
            evidence_id=f"E{index:03d}",
            claim=item.get("claim", "").strip(),
            source_document=document_name,
            source_section=item.get("source_section", "").strip(),
            source_text=item.get("source_text", "").strip(),
            evidence_type=item.get("evidence_type", "").strip(),
            grounding_status="UNVALIDATED",
        )

        evidence_units.append(evidence)

    return evidence_units