from pathlib import Path
from types import SimpleNamespace
import sqlite3

import pytest

from job_agent.models.candidate import CandidateSourceType, EvidenceUnit
from job_agent.models.opportunity import (
    JobOpportunity,
    PursuitPriority,
    UserDecision,
)
from job_agent.models.preference import PreferenceCheckResult
from job_agent.storage.candidate_repository import (
    build_candidate_source_id,
    replace_resume_source,
)
from job_agent.storage.database import get_connection, initialize_database
from job_agent.storage.opportunity_repository import (
    create_completed_job_opportunity_analysis,
)
from job_agent.services.ui_service import (
    get_opportunity_detail,
    list_needs_review,
    list_reviewed,
    set_user_decision,
)


def _evidence(evidence_id: str, claim: str, source_document: str) -> EvidenceUnit:
    return EvidenceUnit(
        evidence_id=evidence_id,
        claim=claim,
        source_document=source_document,
        source_section="Projects",
        source_text=f"Original: {claim}",
        evidence_type="PROJECT",
        grounding_status="VALIDATED",
    )


def _save_opportunity(
    db_path: Path,
    *,
    opportunity_id: str,
    evidence_id: str,
    score: float,
    priority: PursuitPriority,
    created_at: str,
):
    opportunity = JobOpportunity(
        opportunity_id=opportunity_id,
        title=f"Role {opportunity_id}",
        company="Example",
        source="TEST",
        posting_url=f"https://jobs.example.com/{opportunity_id}",
        jd_text="Required: Python",
        requirement_fit_score=score,
        pursuit_priority=priority,
        preference_results={
            "location": PreferenceCheckResult.MATCH,
            "work_mode": PreferenceCheckResult.UNKNOWN,
        },
        created_at=created_at,
    )
    requirement = SimpleNamespace(
        requirement_id="R001",
        requirement="Python experience",
        category="SKILL",
        requirement_level="REQUIRED",
        jd_source_text="Python experience",
        jd_section="Qualifications",
        grounding_status="VALIDATED",
    )
    mapping = SimpleNamespace(
        requirement_id="R001",
        support_level="PARTIAL",
        reason=(
            "Closely related Python experience is present, but the exact "
            "framework named in the requirement is not directly evidenced."
        ),
        evidence_matches=[
            SimpleNamespace(
                evidence_id=evidence_id,
                relationship="ADJACENT",
                reason="Internal relation reason not exposed in UI.",
            )
        ],
    )
    create_completed_job_opportunity_analysis(
        opportunity=opportunity,
        requirements=[requirement],
        mappings=[mapping],
        db_path=db_path,
    )


def test_job_detail_hydrates_inactive_historical_resume_evidence(tmp_path: Path):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    old_source = build_candidate_source_id()
    replace_resume_source(
        source_id=old_source,
        filename="old_resume.md",
        stored_path=None,
        evidence_units=[_evidence("E001", "Old resume evidence", "old_resume.md")],
        db_path=db_path,
    )
    _save_opportunity(
        db_path,
        opportunity_id="J001",
        evidence_id="E001",
        score=80,
        priority=PursuitPriority.STRONG_OPPORTUNITY,
        created_at="2026-09-21T20:00:00+00:00",
    )

    replace_resume_source(
        source_id=build_candidate_source_id(),
        filename="new_resume.md",
        stored_path=None,
        evidence_units=[_evidence("E002", "New resume evidence", "new_resume.md")],
        db_path=db_path,
    )

    detail = get_opportunity_detail("J001", db_path=db_path)
    evidence = detail.requirements[0].evidence[0]
    assert evidence.evidence_id == "E001"
    assert evidence.claim == "Old resume evidence"
    assert evidence.source_document == "old_resume.md"
    assert evidence.source_text == "Original: Old resume evidence"
    # UI detail intentionally does not expose source_section/relationship fields.
    assert not hasattr(evidence, "source_section")
    assert not hasattr(evidence, "relationship")

    connection = get_connection(db_path)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            with connection:
                connection.execute(
                    "DELETE FROM candidate_evidence WHERE evidence_id = ?",
                    ("E001",),
                )
    finally:
        connection.close()


def test_needs_review_and_reviewed_derive_from_user_decision(tmp_path: Path):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    replace_resume_source(
        source_id=build_candidate_source_id(),
        filename="resume.md",
        stored_path=None,
        evidence_units=[_evidence("E001", "Evidence", "resume.md")],
        db_path=db_path,
    )

    _save_opportunity(
        db_path,
        opportunity_id="HIGH",
        evidence_id="E001",
        score=88,
        priority=PursuitPriority.TOP_PRIORITY,
        created_at="2026-09-21T20:00:00+00:00",
    )
    _save_opportunity(
        db_path,
        opportunity_id="LOW",
        evidence_id="E001",
        score=70,
        priority=PursuitPriority.STRONG_OPPORTUNITY,
        created_at="2026-09-21T21:00:00+00:00",
    )

    assert [item.opportunity_id for item in list_needs_review(db_path)] == [
        "HIGH",
        "LOW",
    ]

    set_user_decision("HIGH", UserDecision.PURSUE_NOW, db_path=db_path)
    assert [item.opportunity_id for item in list_needs_review(db_path)] == [
        "LOW"
    ]
    reviewed = list_reviewed(db_path=db_path)
    assert [item.opportunity_id for item in reviewed] == ["HIGH"]
    assert reviewed[0].user_decision == UserDecision.PURSUE_NOW
