from pathlib import Path

import pytest

from job_agent.models.candidate import EvidenceUnit
from job_agent.storage.candidate_repository import (
    get_active_resume_source,
    list_candidate_sources,
    load_all_candidate_evidence,
    load_candidate_evidence_base,
)
from job_agent.storage.database import initialize_database
from job_agent.workflows import candidate_profile_ingestion as workflow


def _evidence(claim: str, document_name: str = "resume.md") -> EvidenceUnit:
    return EvidenceUnit(
        evidence_id="E001",
        claim=claim,
        source_document=document_name,
        source_section="Experience",
        source_text=claim,
        evidence_type="EXPERIENCE",
        grounding_status="VALIDATED",
    )


def test_resume_replacement_deactivates_old_source_but_keeps_evidence(
    tmp_path: Path,
    monkeypatch,
):
    db_path = tmp_path / "job_agent.db"
    source_dir = tmp_path / "sources"
    initialize_database(db_path)

    claims = iter(["Old resume evidence", "New resume evidence"])
    monkeypatch.setattr(
        workflow,
        "extract_evidence_from_document",
        lambda document_name, document_text: [
            _evidence(next(claims), document_name)
        ],
    )
    monkeypatch.setattr(
        workflow,
        "validate_evidence",
        lambda evidence, document_text: evidence,
    )

    first = workflow.ingest_uploaded_resume_markdown(
        filename="resume.md",
        content=b"# Old Resume",
        source_dir=source_dir,
        db_path=db_path,
    )
    second = workflow.ingest_uploaded_resume_markdown(
        filename="resume.md",
        content=b"# New Resume",
        source_dir=source_dir,
        db_path=db_path,
    )

    assert first.added_evidence_ids == ("E001",)
    assert second.added_evidence_ids == ("E002",)

    sources = list_candidate_sources(db_path=db_path)
    assert len(sources) == 2
    old_source = next(s for s in sources if s.source_id == first.source_id)
    new_source = next(s for s in sources if s.source_id == second.source_id)
    assert old_source.is_active is False
    assert new_source.is_active is True
    assert get_active_resume_source(db_path=db_path).source_id == second.source_id

    active = load_candidate_evidence_base(db_path=db_path)
    assert [e.evidence_id for e in active.evidence_units] == ["E002"]
    assert [e.claim for e in active.evidence_units] == ["New resume evidence"]

    all_evidence = load_all_candidate_evidence(db_path=db_path)
    assert [e.evidence_id for e in all_evidence.evidence_units] == [
        "E001",
        "E002",
    ]


def test_failed_resume_replacement_preserves_current_resume(
    tmp_path: Path,
    monkeypatch,
):
    db_path = tmp_path / "job_agent.db"
    source_dir = tmp_path / "sources"
    initialize_database(db_path)

    monkeypatch.setattr(
        workflow,
        "extract_evidence_from_document",
        lambda document_name, document_text: [
            _evidence("Stable old resume", document_name)
        ],
    )
    monkeypatch.setattr(
        workflow,
        "validate_evidence",
        lambda evidence, document_text: evidence,
    )

    first = workflow.ingest_uploaded_resume_markdown(
        filename="resume.md",
        content=b"# Stable Resume",
        source_dir=source_dir,
        db_path=db_path,
    )

    def fail_extract(**kwargs):
        raise RuntimeError("simulated extraction failure")

    monkeypatch.setattr(
        workflow,
        "extract_evidence_from_document",
        fail_extract,
    )

    with pytest.raises(RuntimeError, match="simulated extraction failure"):
        workflow.ingest_uploaded_resume_markdown(
            filename="new_resume.md",
            content=b"# Broken Resume",
            source_dir=source_dir,
            db_path=db_path,
        )

    active_resume = get_active_resume_source(db_path=db_path)
    assert active_resume is not None
    assert active_resume.source_id == first.source_id
    assert [e.evidence_id for e in load_candidate_evidence_base(
        db_path=db_path
    ).evidence_units] == ["E001"]

    # The failed staged upload is cleaned up; the successful source remains.
    stored_files = list(source_dir.glob("*.md"))
    assert len(stored_files) == 1


def test_supporting_materials_accumulate(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    counter = {"n": 0}
    def fake_extract(document_name, document_text):
        counter["n"] += 1
        return [_evidence(f"Support {counter['n']}", document_name)]

    monkeypatch.setattr(workflow, "extract_evidence_from_document", fake_extract)
    monkeypatch.setattr(
        workflow,
        "validate_evidence",
        lambda evidence, document_text: evidence,
    )

    workflow.ingest_candidate_document(
        document_name="project_a.md",
        document_text="# A",
        db_path=db_path,
    )
    workflow.ingest_candidate_document(
        document_name="project_b.md",
        document_text="# B",
        db_path=db_path,
    )

    sources = list_candidate_sources(db_path=db_path, active_only=True)
    assert [s.source_type.value for s in sources] == ["SUPPORTING", "SUPPORTING"]
    assert len(load_candidate_evidence_base(db_path=db_path).evidence_units) == 2


def test_first_managed_resume_excludes_legacy_source_less_evidence_from_future_matching(
    tmp_path: Path,
    monkeypatch,
):
    from job_agent.models.candidate import CandidateEvidenceBase
    from job_agent.storage.candidate_repository import save_candidate_evidence_base

    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    # Simulate prototype evidence from the uploaded source-of-truth DB.
    save_candidate_evidence_base(
        CandidateEvidenceBase(
            evidence_units=[
                _evidence("Legacy prototype evidence", "legacy.md")
            ]
        ),
        db_path=db_path,
    )
    assert [e.claim for e in load_candidate_evidence_base(
        db_path=db_path
    ).evidence_units] == ["Legacy prototype evidence"]

    monkeypatch.setattr(
        workflow,
        "extract_evidence_from_document",
        lambda document_name, document_text: [
            _evidence("Current resume evidence", document_name)
        ],
    )
    monkeypatch.setattr(
        workflow,
        "validate_evidence",
        lambda evidence, document_text: evidence,
    )

    workflow.ingest_uploaded_resume_markdown(
        filename="resume.md",
        content=b"# Current Resume",
        source_dir=tmp_path / "sources",
        db_path=db_path,
    )

    active_claims = [
        e.claim
        for e in load_candidate_evidence_base(
            db_path=db_path
        ).evidence_units
    ]
    assert active_claims == ["Current resume evidence"]

    # Legacy evidence was not deleted and remains available historically.
    all_claims = [
        e.claim
        for e in load_all_candidate_evidence(
            db_path=db_path
        ).evidence_units
    ]
    assert all_claims == [
        "Legacy prototype evidence",
        "Current resume evidence",
    ]
