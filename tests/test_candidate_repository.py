from job_agent.models.candidate import (
    CandidateEvidenceBase,
    EvidenceUnit,
)
from job_agent.storage.database import initialize_database
from job_agent.storage.candidate_repository import (
    load_candidate_evidence_base,
    save_candidate_evidence_base,
)


def test_save_and_load_candidate_evidence(tmp_path):
    db_path = tmp_path / "test_job_agent.db"

    initialize_database(db_path)

    original = CandidateEvidenceBase(
        evidence_units=[
            EvidenceUnit(
                evidence_id="E001",
                claim="Built an AI application using Python.",
                source_document="project.md",
                source_section="Implementation",
                source_text="Built an AI application using Python.",
                evidence_type="PROJECT",
                grounding_status="VALIDATED",
            ),
            EvidenceUnit(
                evidence_id="E002",
                claim="Implemented retrieval-augmented generation.",
                source_document="project.md",
                source_section="Retrieval",
                source_text="Implemented retrieval-augmented generation.",
                evidence_type="PROJECT",
                grounding_status="VALIDATED",
            ),
        ]
    )

    save_candidate_evidence_base(
        original,
        db_path=db_path,
    )

    loaded = load_candidate_evidence_base(
        db_path=db_path,
    )

    assert len(loaded.evidence_units) == 2

    assert loaded.evidence_units[0].evidence_id == "E001"
    assert loaded.evidence_units[0].claim == (
        "Built an AI application using Python."
    )

    assert loaded.evidence_units[1].evidence_id == "E002"
    assert loaded.evidence_units[1].grounding_status == "VALIDATED"