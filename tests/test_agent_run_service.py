from pathlib import Path
from types import SimpleNamespace

from job_agent.models.candidate import CandidateEvidenceBase, EvidenceUnit
from job_agent.models.job_candidate import JobCandidate
from job_agent.models.opportunity import JobOpportunity, PursuitPriority
from job_agent.services import agent_run_service as service
from job_agent.services.agent_run_service import (
    AgentRunPhase,
    JobAlertEmail,
)
from job_agent.storage.candidate_repository import save_candidate_evidence_base
from job_agent.storage.database import initialize_database
from job_agent.storage.email_repository import is_email_processed


def _seed_evidence(db_path: Path) -> None:
    save_candidate_evidence_base(
        CandidateEvidenceBase(
            evidence_units=[
                EvidenceUnit(
                    evidence_id="E001",
                    claim="Evidence",
                    source_document="resume.md",
                    source_section=None,
                    source_text="Evidence",
                    evidence_type="EXPERIENCE",
                    grounding_status="VALIDATED",
                )
            ]
        ),
        db_path=db_path,
    )


def test_run_agent_is_single_orchestration_entrypoint(
    tmp_path: Path,
    monkeypatch,
):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    _seed_evidence(db_path)

    email = JobAlertEmail(
        message_id="m1",
        source="TEST_ALERT",
        sender="jobs@example.com",
        subject="Jobs for you",
        snippet="AI Engineer",
        body="AI Engineer at Example",
    )

    monkeypatch.setattr(
        service,
        "is_job_related_email",
        lambda **kwargs: True,
    )

    candidate = JobCandidate(
        source="TEST_ALERT",
        source_message_id="m1",
        title="AI Engineer",
        company="Example",
    )
    monkeypatch.setattr(
        service,
        "extract_job_candidates_from_email",
        lambda **kwargs: [candidate],
    )

    created_at_values = []
    def fake_process(**kwargs):
        created_at_values.append(kwargs["created_at"])
        assert kwargs["progress_callback"] is None
        opportunity = JobOpportunity(
            opportunity_id="J1",
            title="AI Engineer",
            company="Example",
            source="TEST_ALERT",
            posting_url="https://example.com/jobs/1",
            jd_text="JD",
            requirement_fit_score=80,
            pursuit_priority=PursuitPriority.STRONG_OPPORTUNITY,
            created_at=kwargs["created_at"],
        )
        return SimpleNamespace(
            analyzed_opportunities=[opportunity],
            duplicate_opportunity_ids=[],
        )

    monkeypatch.setattr(service, "process_job_candidate", fake_process)

    progress = []
    result = service.run_agent(
        emails=[email],
        progress_callback=progress.append,
        db_path=db_path,
    )

    assert result.processed_email_count == 1
    assert len(result.new_opportunities) == 1
    assert created_at_values == [result.run_timestamp]
    assert is_email_processed("m1", db_path=db_path) is True
    assert [event.phase for event in progress] == [
        AgentRunPhase.FINDING_JOB_ALERTS,
        AgentRunPhase.FINDING_JOB_ALERTS,
        AgentRunPhase.ANALYZING_OPPORTUNITIES,
        AgentRunPhase.ANALYZING_OPPORTUNITIES,
        AgentRunPhase.COMPLETE,
    ]
    assert progress[1].message == "Found 1 recent email"
    assert progress[2].message == "Processing opportunity 1 of 1"
    assert progress[2].current == 1
    assert progress[2].total == 1
    assert progress[3].message == "Processed opportunity 1 of 1"
    assert progress[-1].message == "Complete"


def test_technical_failure_does_not_mark_email_processed(
    tmp_path: Path,
    monkeypatch,
):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    _seed_evidence(db_path)

    email = JobAlertEmail(
        message_id="m2",
        source="TEST_ALERT",
        sender="jobs@example.com",
        subject="Jobs",
        snippet="AI Engineer",
        body="AI Engineer",
    )
    monkeypatch.setattr(service, "is_job_related_email", lambda **kwargs: True)
    monkeypatch.setattr(
        service,
        "extract_job_candidates_from_email",
        lambda **kwargs: [
            JobCandidate(
                source="TEST_ALERT",
                source_message_id="m2",
                title="AI Engineer",
                company="Example",
            )
        ],
    )
    monkeypatch.setattr(
        service,
        "process_job_candidate",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("technical failure")),
    )

    try:
        service.run_agent(emails=[email], db_path=db_path)
    except RuntimeError as exc:
        assert "technical failure" in str(exc)
    else:
        raise AssertionError("Expected technical failure")

    assert is_email_processed("m2", db_path=db_path) is False


def test_email_source_fetches_body_only_after_metadata_triage(
    tmp_path: Path,
    monkeypatch,
):
    from job_agent.models.email import EmailMetadata, JobAlertEmail

    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    _seed_evidence(db_path)

    metadata = [
        EmailMetadata(
            message_id="not-job",
            thread_id="t1",
            sender="newsletter@example.com",
            subject="Career newsletter",
            sent_at=None,
            snippet="General career advice",
        ),
        EmailMetadata(
            message_id="job",
            thread_id="t2",
            sender="jobs@linkedin.com",
            subject="Jobs for you",
            sent_at=None,
            snippet="AI Engineer at Example",
        ),
    ]

    class FakeEmailSource:
        def __init__(self):
            self.full_fetches = []

        def account_key(self):
            return "gmail:test@example.com"

        def list_message_metadata(self):
            return metadata

        def get_message(self, message_id: str):
            self.full_fetches.append(message_id)
            return JobAlertEmail(
                message_id=message_id,
                source="LINKEDIN",
                sender="jobs@linkedin.com",
                subject="Jobs for you",
                snippet="AI Engineer at Example",
                body="AI Engineer at Example",
            )

    email_source = FakeEmailSource()
    monkeypatch.setattr(
        service,
        "is_job_related_email",
        lambda **kwargs: kwargs["subject"] == "Jobs for you",
    )
    monkeypatch.setattr(
        service,
        "extract_job_candidates_from_email",
        lambda **kwargs: [],
    )

    result = service.run_agent(
        email_source=email_source,
        db_path=db_path,
    )

    assert result.discovered_email_count == 2
    assert result.processed_email_count == 2
    assert email_source.full_fetches == ["job"]
    assert is_email_processed(
        "not-job",
        db_path=db_path,
        account_key="gmail:test@example.com",
    ) is True
    assert is_email_processed(
        "job",
        db_path=db_path,
        account_key="gmail:test@example.com",
    ) is True


def test_processed_email_dedupe_is_scoped_to_email_account(
    tmp_path: Path,
    monkeypatch,
):
    from job_agent.models.email import EmailMetadata

    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)
    _seed_evidence(db_path)

    metadata = EmailMetadata(
        message_id="same-message-id",
        thread_id=None,
        sender="jobs@example.com",
        subject="Not a job",
        sent_at=None,
        snippet="Newsletter",
    )

    class FakeEmailSource:
        def __init__(self, account_key):
            self._account_key = account_key

        def account_key(self):
            return self._account_key

        def list_message_metadata(self):
            return [metadata]

        def get_message(self, message_id: str):
            raise AssertionError("Body should not be fetched for non-job email")

    monkeypatch.setattr(service, "is_job_related_email", lambda **kwargs: False)

    first = service.run_agent(
        email_source=FakeEmailSource("gmail:first@example.com"),
        db_path=db_path,
    )
    second = service.run_agent(
        email_source=FakeEmailSource("gmail:second@example.com"),
        db_path=db_path,
    )
    third = service.run_agent(
        email_source=FakeEmailSource("gmail:first@example.com"),
        db_path=db_path,
    )

    assert first.processed_email_count == 1
    assert second.processed_email_count == 1
    assert third.skipped_processed_email_count == 1
    assert third.processed_email_count == 0
