from pathlib import Path
from types import SimpleNamespace
import sqlite3

import pytest

from job_agent.models.candidate import CandidateEvidenceBase, EvidenceUnit
from job_agent.models.opportunity import (
    JobOpportunity,
    PursuitPriority,
    UserDecision,
)
from job_agent.models.preference import PreferenceCheckResult
from job_agent.storage.candidate_repository import save_candidate_evidence_base
from job_agent.storage.database import initialize_database
from job_agent.storage.opportunity_repository import (
    create_completed_job_opportunity_analysis,
    load_job_opportunity,
    load_job_requirements,
    load_requirement_mappings,
    set_user_decision,
)


def _build_analysis(opportunity_id: str = "J001"):
    opportunity = JobOpportunity(
        opportunity_id=opportunity_id,
        title="AI Application Engineer",
        company="Example AI Company",
        source="MOCK_JOB_ALERT",
        location="San Francisco, CA",
        source_url="https://example.com/alert/1",
        source_message_id="email-1",
        source_item_id="item-1",
        posting_url=f"https://example.com/jobs/{opportunity_id}",
        jd_text="Strong Python skills and LLM application experience.",
        requirement_fit_score=82.5,
        pursuit_priority=PursuitPriority.STRONG_OPPORTUNITY,
        preference_results={
            "location": PreferenceCheckResult.MATCH,
            "work_mode": PreferenceCheckResult.UNKNOWN,
        },
        strong_matches=["Python"],
        main_gaps=["Production deployment"],
        created_at="2026-09-21T20:00:00+00:00",
    )
    requirement = SimpleNamespace(
        requirement_id="R001",
        requirement="Strong Python skills",
        category="SKILL",
        requirement_level="REQUIRED",
        jd_source_text="Strong Python skills",
        jd_section="Qualifications",
        grounding_status="VALIDATED",
    )
    mapping = SimpleNamespace(
        requirement_id="R001",
        support_level="STRONG",
        reason="Direct grounded Python evidence.",
        evidence_matches=[
            SimpleNamespace(
                evidence_id="E001",
                relationship="DIRECT",
                reason="Direct Python evidence.",
            )
        ],
    )
    return opportunity, [requirement], [mapping]


def _insert_evidence(db_path: Path) -> None:
    save_candidate_evidence_base(
        CandidateEvidenceBase(
            evidence_units=[
                EvidenceUnit(
                    evidence_id="E001",
                    claim="Built Python LLM applications.",
                    source_document="resume.md",
                    source_section="Projects",
                    source_text="Built Python LLM applications.",
                    evidence_type="PROJECT",
                    grounding_status="VALIDATED",
                )
            ]
        ),
        db_path=db_path,
    )


def test_create_completed_analysis_and_load_children(tmp_path: Path):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    _insert_evidence(db_path)
    opportunity, requirements, mappings = _build_analysis()

    create_completed_job_opportunity_analysis(
        opportunity=opportunity,
        requirements=requirements,
        mappings=mappings,
        db_path=db_path,
    )

    loaded = load_job_opportunity("J001", db_path=db_path)
    assert loaded is not None
    assert loaded.requirement_fit_score == 82.5
    assert loaded.user_decision is None
    assert loaded.created_at == "2026-09-21T20:00:00+00:00"
    assert len(load_job_requirements("J001", db_path=db_path)) == 1
    loaded_mappings = load_requirement_mappings("J001", db_path=db_path)
    assert loaded_mappings[0].evidence_matches[0].evidence_id == "E001"


def test_analysis_is_create_only_and_cannot_be_overwritten(tmp_path: Path):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    _insert_evidence(db_path)
    opportunity, requirements, mappings = _build_analysis()

    create_completed_job_opportunity_analysis(
        opportunity=opportunity,
        requirements=requirements,
        mappings=mappings,
        db_path=db_path,
    )

    opportunity.requirement_fit_score = 1.0
    with pytest.raises(sqlite3.IntegrityError):
        create_completed_job_opportunity_analysis(
            opportunity=opportunity,
            requirements=requirements,
            mappings=mappings,
            db_path=db_path,
        )

    loaded = load_job_opportunity("J001", db_path=db_path)
    assert loaded is not None
    assert loaded.requirement_fit_score == 82.5


def test_user_decision_mutates_without_touching_analysis(tmp_path: Path):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    _insert_evidence(db_path)
    opportunity, requirements, mappings = _build_analysis()
    create_completed_job_opportunity_analysis(
        opportunity=opportunity,
        requirements=requirements,
        mappings=mappings,
        db_path=db_path,
    )

    before = load_job_opportunity("J001", db_path=db_path)
    assert before is not None

    for decision in (
        UserDecision.SAVE_FOR_LATER,
        UserDecision.PURSUE_NOW,
        UserDecision.PASS,
    ):
        updated = set_user_decision("J001", decision, db_path=db_path)
        assert updated.user_decision == decision
        assert updated.requirement_fit_score == before.requirement_fit_score
        assert updated.pursuit_priority == before.pursuit_priority
        assert updated.preference_results == before.preference_results
        assert updated.strong_matches == before.strong_matches
        assert updated.main_gaps == before.main_gaps
        assert updated.created_at == before.created_at
