from pathlib import Path
from types import SimpleNamespace

import job_agent.workflows.core_workflow as workflow

from job_agent.models.candidate import CandidateEvidenceBase
from job_agent.models.job_candidate import (
    JobCandidate,
    JobResolutionReason,
    JobVerificationLevel,
)
from job_agent.models.opportunity import PursuitPriority
from job_agent.models.resolved_job_posting import (
    ResolvedJobPosting,
)
from job_agent.storage.database import (
    get_connection,
    initialize_database,
)
from job_agent.storage.opportunity_repository import (
    load_job_opportunity,
)


def _candidate() -> JobCandidate:
    return JobCandidate(
        source="LINKEDIN",
        source_message_id="email-1",
        source_item_id="job-1",
        source_url="https://linkedin.example/jobs/1",
        title="AI Application Engineer",
        company="Example AI",
        location="San Francisco, CA",
    )


def _evidence_base() -> CandidateEvidenceBase:
    return CandidateEvidenceBase(
        evidence_units=[
            SimpleNamespace(
                evidence_id="E001",
                claim="Built Python LLM applications.",
                source_document="resume.md",
                source_section="Projects",
                source_text="Built Python LLM applications.",
                evidence_type="PROJECT",
                grounding_status="VALIDATED",
            )
        ]
    )


def _insert_candidate_evidence(db_path: Path) -> None:
    connection = get_connection(db_path)
    try:
        with connection:
            connection.execute(
                """
                INSERT INTO candidate_evidence (
                    evidence_id,
                    claim,
                    source_document,
                    source_section,
                    source_text,
                    evidence_type,
                    grounding_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "E001",
                    "Built Python LLM applications.",
                    "resume.md",
                    "Projects",
                    "Built Python LLM applications.",
                    "PROJECT",
                    "VALIDATED",
                ),
            )
    finally:
        connection.close()


def _install_analysis_stubs(monkeypatch):
    requirement = SimpleNamespace(
        requirement_id="R001",
        requirement="Strong Python skills",
        category="SKILL",
        requirement_level="REQUIRED",
        jd_source_text="Strong Python skills",
        jd_section="Qualifications",
        grounding_status="VALIDATED",
    )

    evidence_match = SimpleNamespace(
        evidence_id="E001",
        relationship="DIRECT",
        reason="Direct Python evidence.",
    )

    mapping = SimpleNamespace(
        requirement_id="R001",
        support_level="STRONG",
        reason="Direct grounded evidence.",
        evidence_matches=[evidence_match],
    )

    monkeypatch.setattr(
        workflow,
        "extract_requirements_from_jd",
        lambda jd_text: [requirement],
    )
    monkeypatch.setattr(
        workflow,
        "validate_requirements",
        lambda requirements, original_jd_text: requirements,
    )
    monkeypatch.setattr(
        workflow,
        "match_requirements_to_evidence",
        lambda requirements, evidence_base: [mapping],
    )
    monkeypatch.setattr(
        workflow,
        "verify_negative_mappings",
        lambda mappings, requirements, evidence_base: [],
    )
    monkeypatch.setattr(
        workflow,
        "finalize_mappings",
        lambda mappings, verifications, requirements, evidence_base: mappings,
    )
    monkeypatch.setattr(
        workflow,
        "calculate_requirement_fit",
        lambda requirements, finalized_mappings: SimpleNamespace(
            score=88.0
        ),
    )
    monkeypatch.setattr(
        workflow,
        "calculate_pursuit_priority",
        lambda requirement_fit_score, preference_results: (
            PursuitPriority.STRONG_OPPORTUNITY
        ),
    )


def test_core_workflow_analyzes_and_persists_new_posting(
    monkeypatch,
    tmp_path: Path,
):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    _insert_candidate_evidence(db_path)
    _install_analysis_stubs(monkeypatch)

    candidate = _candidate()

    def fake_resolve(job_candidate):
        job_candidate.mark_verified(
            level=JobVerificationLevel.PUBLIC_POSTING,
            reason=JobResolutionReason.ANALYSIS_READY_PUBLIC_POSTING,
        )
        return [
            ResolvedJobPosting(
                source_candidate=job_candidate,
                posting_url="https://jobs.example.com/1",
                jd_text="Complete verified JD",
                verification_level=(
                    JobVerificationLevel.PUBLIC_POSTING
                ),
            )
        ]

    monkeypatch.setattr(
        workflow,
        "resolve_job_candidate",
        fake_resolve,
    )

    result = workflow.process_job_candidate(
        job_candidate=candidate,
        candidate_evidence_base=_evidence_base(),
        db_path=db_path,
    )

    assert len(result.analyzed_opportunities) == 1
    opportunity = result.analyzed_opportunities[0]

    assert opportunity.posting_url == "https://jobs.example.com/1"
    assert opportunity.requirement_fit_score == 88.0
    assert opportunity.strong_matches == ["Strong Python skills"]
    assert opportunity.main_gaps == []

    loaded = load_job_opportunity(
        opportunity.opportunity_id,
        db_path=db_path,
    )
    assert loaded is not None
    assert loaded.posting_url == opportunity.posting_url
    assert loaded.requirement_fit_score == 88.0


def test_second_run_is_duplicate_and_skips_analysis(
    monkeypatch,
    tmp_path: Path,
):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    _insert_candidate_evidence(db_path)
    _install_analysis_stubs(monkeypatch)

    analysis_call_count = {"count": 0}

    original_analyze = (
        workflow.analyze_and_persist_resolved_posting
    )

    def counted_analyze(**kwargs):
        analysis_call_count["count"] += 1
        return original_analyze(**kwargs)

    monkeypatch.setattr(
        workflow,
        "analyze_and_persist_resolved_posting",
        counted_analyze,
    )

    def fake_resolve(job_candidate):
        job_candidate.mark_verified(
            level=JobVerificationLevel.PUBLIC_POSTING,
            reason=JobResolutionReason.ANALYSIS_READY_PUBLIC_POSTING,
        )
        return [
            ResolvedJobPosting(
                source_candidate=job_candidate,
                posting_url="https://jobs.example.com/duplicate",
                jd_text="Complete verified JD",
            )
        ]

    monkeypatch.setattr(
        workflow,
        "resolve_job_candidate",
        fake_resolve,
    )

    first = workflow.process_job_candidate(
        job_candidate=_candidate(),
        candidate_evidence_base=_evidence_base(),
        db_path=db_path,
    )

    assert len(first.analyzed_opportunities) == 1
    assert analysis_call_count["count"] == 1

    second = workflow.process_job_candidate(
        job_candidate=_candidate(),
        candidate_evidence_base=_evidence_base(),
        db_path=db_path,
    )

    assert len(second.analyzed_opportunities) == 0
    assert len(second.duplicate_opportunity_ids) == 1
    assert analysis_call_count["count"] == 1


def test_normal_unverified_does_not_run_analysis(
    monkeypatch,
    tmp_path: Path,
):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    candidate = _candidate()

    def fake_resolve(job_candidate):
        job_candidate.mark_unverified(
            reason=JobResolutionReason.NO_SUITABLE_POSTING_FOUND
        )
        return []

    monkeypatch.setattr(
        workflow,
        "resolve_job_candidate",
        fake_resolve,
    )

    result = workflow.process_job_candidate(
        job_candidate=candidate,
        candidate_evidence_base=_evidence_base(),
        db_path=db_path,
    )

    assert result.posting_results == []
    assert result.analyzed_opportunities == []


def test_opportunity_id_is_stable():
    url = "https://jobs.example.com/role/123"

    assert (
        workflow.build_opportunity_id(url)
        == workflow.build_opportunity_id(url)
    )

    assert workflow.build_opportunity_id(url).startswith(
        "opp_"
    )
