from pathlib import Path

from job_agent.models.candidate import (
    CandidateEvidenceBase,
    EvidenceUnit,
)
from job_agent.storage.candidate_repository import (
    load_candidate_evidence_base,
    save_candidate_evidence_base,
)
from job_agent.storage.database import (
    initialize_database,
)
from job_agent.workflows import candidate_profile_ingestion as workflow


def _evidence(
    evidence_id: str,
    source_document: str,
    claim: str,
) -> EvidenceUnit:
    return EvidenceUnit(
        evidence_id=evidence_id,
        claim=claim,
        source_document=source_document,
        source_section="Overview",
        source_text=claim,
        evidence_type="PROJECT",
        grounding_status="VALIDATED",
    )


def test_incremental_ingestion_continues_global_evidence_ids(
    tmp_path: Path,
    monkeypatch,
):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    save_candidate_evidence_base(
        CandidateEvidenceBase(
            evidence_units=[
                _evidence(
                    "E001",
                    "resume.md",
                    "Resume fact 1",
                ),
                _evidence(
                    "E002",
                    "resume.md",
                    "Resume fact 2",
                ),
            ]
        ),
        db_path=db_path,
    )

    extracted = [
        _evidence(
            "E001",
            "rag_project.md",
            "Built a RAG assistant.",
        ),
        _evidence(
            "E002",
            "rag_project.md",
            "Evaluated retrieval strategies.",
        ),
    ]

    monkeypatch.setattr(
        workflow,
        "extract_evidence_from_document",
        lambda **kwargs: extracted,
    )
    monkeypatch.setattr(
        workflow,
        "validate_evidence",
        lambda evidence, document_text: evidence,
    )

    result = workflow.ingest_candidate_document(
        document_name="rag_project.md",
        document_text="# RAG Project",
        db_path=db_path,
    )

    assert result.added_evidence_ids == (
        "E003",
        "E004",
    )
    assert result.total_evidence_count == 4

    persisted = load_candidate_evidence_base(
        db_path=db_path,
    )

    assert [
        item.evidence_id
        for item in persisted.evidence_units
    ] == [
        "E001",
        "E002",
        "E003",
        "E004",
    ]

    assert persisted.evidence_units[2].source_document == (
        "rag_project.md"
    )


def test_second_supporting_document_keeps_appending(
    tmp_path: Path,
    monkeypatch,
):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    call_number = {"value": 0}

    def fake_extract(**kwargs):
        call_number["value"] += 1
        return [
            _evidence(
                "E001",
                kwargs["document_name"],
                f"Fact {call_number['value']}",
            )
        ]

    monkeypatch.setattr(
        workflow,
        "extract_evidence_from_document",
        fake_extract,
    )
    monkeypatch.setattr(
        workflow,
        "validate_evidence",
        lambda evidence, document_text: evidence,
    )

    first = workflow.ingest_candidate_document(
        document_name="project_a.md",
        document_text="# Project A",
        db_path=db_path,
    )
    second = workflow.ingest_candidate_document(
        document_name="project_b.md",
        document_text="# Project B",
        db_path=db_path,
    )

    assert first.added_evidence_ids == ("E001",)
    assert second.added_evidence_ids == ("E002",)
    assert second.total_evidence_count == 2
