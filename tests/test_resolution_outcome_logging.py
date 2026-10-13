from pathlib import Path

from job_agent.models.job_candidate import (
    JobCandidate,
    JobResolutionReason,
    JobVerificationLevel,
)
from job_agent.storage.database import initialize_database
from job_agent.storage.resolution_repository import (
    load_job_resolution_attempts,
    save_job_resolution_attempt,
)



def test_resolution_outcome_logging(tmp_path):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    candidate = JobCandidate(
        source="LINKEDIN",
        source_message_id="email-log-001",
        source_item_id="job-999",
        title="Product Manager",
        company="Example AI",
        location="San Francisco",
        source_url="https://www.linkedin.com/jobs/view/999",
    )
    candidate.mark_verified(
        level=JobVerificationLevel.PUBLIC_POSTING,
        reason=JobResolutionReason.ANALYSIS_READY_PUBLIC_POSTING,
    )

    attempt_id = save_job_resolution_attempt(
        job_candidate=candidate,
        resolved_posting_count=1,
        db_path=db_path,
    )
    rows = load_job_resolution_attempts(
        source_message_id="email-log-001",
        db_path=db_path,
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["attempt_id"] == attempt_id
    assert row["execution_status"] == "COMPLETED"
    assert row["verification_result"] == "VERIFIED"
    assert row["verification_level"] == "PUBLIC_POSTING"
    assert row["resolution_reason"] == "ANALYSIS_READY_PUBLIC_POSTING"
    assert row["resolved_posting_count"] == 1
