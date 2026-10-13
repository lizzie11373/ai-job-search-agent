from pathlib import Path
from types import SimpleNamespace

from job_agent.models.job_candidate import (
    JobCandidate,
    JobResolutionReason,
    JobVerificationLevel,
)
from job_agent.models.opportunity import (
    PursuitPriority,
)
from job_agent.models.resolved_job_posting import (
    JobDeduplicationResult,
    ResolvedJobPosting,
)
from job_agent.storage.database import (
    get_connection,
    initialize_database,
)
from job_agent.storage.opportunity_repository import (
    load_job_opportunity,
    load_job_opportunity_by_posting_url,
    load_job_requirements,
    load_requirement_mappings,
    save_complete_job_opportunity_analysis,
)


def test_verified_posting_promotes_and_persists_atomically(
    tmp_path: Path,
):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    candidate = JobCandidate(
        source="LINKEDIN",
        source_message_id="email-123",
        source_item_id="job-456",
        source_url="https://linkedin.example/source/456",
        title="AI Application Engineer",
        company="Example AI",
        location="San Francisco, CA",
    )

    candidate.mark_verified(
        level=JobVerificationLevel.PUBLIC_POSTING,
        reason=JobResolutionReason.ANALYSIS_READY_PUBLIC_POSTING,
    )

    resolved = ResolvedJobPosting(
        source_candidate=candidate,
        posting_url="https://jobs.example.com/ai-app-engineer",
        jd_text="A sufficiently complete job description.",
        verification_level=JobVerificationLevel.PUBLIC_POSTING,
    )

    resolved.deduplication_result = (
        JobDeduplicationResult.NEW
    )

    opportunity = resolved.promote_to_job_opportunity(
        opportunity_id="job_test_001"
    )

    opportunity.requirement_fit_score = 82.5
    opportunity.pursuit_priority = (
        PursuitPriority.STRONG_OPPORTUNITY
    )
    opportunity.strong_matches = [
        "Python",
        "LLM application development",
    ]
    opportunity.main_gaps = [
        "Production-scale deployment",
    ]

    # Save one candidate-evidence row because evidence_matches has an FK.
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
                    "Built LLM applications in Python.",
                    "resume.md",
                    "Projects",
                    "Built LLM applications in Python.",
                    "PROJECT",
                    "VALIDATED",
                ),
            )
    finally:
        connection.close()

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
        reason="Candidate evidence explicitly mentions Python.",
    )

    mapping = SimpleNamespace(
        requirement_id="R001",
        support_level="STRONG",
        reason="Direct grounded evidence.",
        evidence_matches=[evidence_match],
    )

    save_complete_job_opportunity_analysis(
        opportunity=opportunity,
        requirements=[requirement],
        mappings=[mapping],
        db_path=db_path,
    )

    loaded = load_job_opportunity(
        "job_test_001",
        db_path=db_path,
    )

    assert loaded is not None
    assert loaded.posting_url == (
        "https://jobs.example.com/ai-app-engineer"
    )
    assert loaded.canonical_job_url == loaded.posting_url
    assert loaded.source_message_id == "email-123"
    assert loaded.source_item_id == "job-456"
    assert loaded.requirement_fit_score == 82.5
    assert loaded.strong_matches == [
        "Python",
        "LLM application development",
    ]
    assert loaded.main_gaps == [
        "Production-scale deployment",
    ]

    duplicate_lookup = (
        load_job_opportunity_by_posting_url(
            loaded.posting_url,
            db_path=db_path,
        )
    )
    assert duplicate_lookup is not None
    assert duplicate_lookup.opportunity_id == "job_test_001"

    requirements = load_job_requirements(
        "job_test_001",
        db_path=db_path,
    )
    assert len(requirements) == 1
    assert requirements[0].requirement_id == "R001"

    mappings = load_requirement_mappings(
        "job_test_001",
        db_path=db_path,
    )
    assert len(mappings) == 1
    assert mappings[0].requirement_id == "R001"
    assert len(mappings[0].evidence_matches) == 1
    assert mappings[0].evidence_matches[0].evidence_id == "E001"


def test_source_item_id_does_not_fall_back_to_message_id():
    candidate = JobCandidate(
        source="OTHER",
        source_message_id="email-only-id",
        source_item_id=None,
        title="AI Engineer",
        company="Example",
    )

    candidate.mark_verified(
        level=JobVerificationLevel.PUBLIC_POSTING,
        reason=JobResolutionReason.ANALYSIS_READY_PUBLIC_POSTING,
    )

    resolved = ResolvedJobPosting(
        source_candidate=candidate,
        posting_url="https://example.com/jobs/1",
        jd_text="Complete enough JD.",
    )
    resolved.deduplication_result = JobDeduplicationResult.NEW

    opportunity = resolved.promote_to_job_opportunity(
        "job_test_002"
    )

    assert opportunity.source_message_id == "email-only-id"
    assert opportunity.source_item_id is None
