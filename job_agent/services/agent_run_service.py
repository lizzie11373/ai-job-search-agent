from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Callable, Iterable

from job_agent.integrations.email_source import EmailSource
from job_agent.models.email import EmailMetadata, JobAlertEmail

from job_agent.agents.email_classifier import is_job_related_email
from job_agent.agents.job_candidate_extractor import extract_job_candidates_from_email
from job_agent.models.opportunity import JobOpportunity
from job_agent.storage.candidate_repository import load_candidate_evidence_base
from job_agent.storage.database import DEFAULT_DB_PATH, initialize_database
from job_agent.storage.email_repository import (
    LEGACY_EMAIL_ACCOUNT_KEY,
    is_email_processed,
    mark_email_processed,
)
from job_agent.storage.preference_repository import load_candidate_preferences
from job_agent.workflows.core_workflow import process_job_candidate


class AgentRunPhase(StrEnum):
    FINDING_JOB_ALERTS = "FINDING_JOB_ALERTS"
    VERIFYING_JOB_POSTINGS = "VERIFYING_JOB_POSTINGS"
    ANALYZING_OPPORTUNITIES = "ANALYZING_OPPORTUNITIES"
    SAVING_RESULTS = "SAVING_RESULTS"
    COMPLETE = "COMPLETE"


@dataclass(frozen=True)
class AgentRunProgress:
    phase: AgentRunPhase
    message: str
    current: int | None = None
    total: int | None = None


@dataclass
class AgentRunResult:
    run_timestamp: str
    discovered_email_count: int = 0
    skipped_processed_email_count: int = 0
    processed_email_count: int = 0
    extracted_candidate_count: int = 0
    new_opportunities: list[JobOpportunity] = field(default_factory=list)
    duplicate_opportunity_ids: list[str] = field(default_factory=list)


_PHASE_MESSAGES = {
    AgentRunPhase.FINDING_JOB_ALERTS: "Finding job alerts",
    AgentRunPhase.VERIFYING_JOB_POSTINGS: "Verifying job postings",
    AgentRunPhase.ANALYZING_OPPORTUNITIES: "Analyzing new opportunities",
    AgentRunPhase.SAVING_RESULTS: "Saving results",
    AgentRunPhase.COMPLETE: "Agent run complete",
}


def _emit(
    progress_callback,
    phase: AgentRunPhase,
    *,
    message: str | None = None,
    current: int | None = None,
    total: int | None = None,
) -> None:
    if progress_callback is not None:
        progress_callback(
            AgentRunProgress(
                phase=phase,
                message=message or _PHASE_MESSAGES[phase],
                current=current,
                total=total,
            )
        )


def _legacy_email_source(
    email_items: Iterable[JobAlertEmail],
) -> EmailSource:
    items = list(email_items)
    by_id = {item.message_id: item for item in items}

    class _LegacyEmailSource:
        def account_key(self) -> str:
            return LEGACY_EMAIL_ACCOUNT_KEY

        def list_message_metadata(self) -> list[EmailMetadata]:
            return [item.as_metadata() for item in items]

        def get_message(self, message_id: str) -> JobAlertEmail:
            try:
                return by_id[message_id]
            except KeyError as error:
                raise KeyError(f"Unknown legacy email message_id: {message_id}") from error

    return _LegacyEmailSource()


def run_agent(
    *,
    email_source: EmailSource | None = None,
    email_loader: Callable[[], Iterable[JobAlertEmail]] | None = None,
    emails: Iterable[JobAlertEmail] | None = None,
    progress_callback: Callable[[AgentRunProgress], None] | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> AgentRunResult:
    """
    UI-facing orchestration entry point for one complete Agent Run.

    Production integrations should provide an `EmailSource` so the pipeline can
    classify lightweight metadata before fetching a full message body.
    `email_loader` and `emails` remain as backward-compatible full-email inputs
    for tests and local diagnostics.
    """

    supplied_sources = sum(
        source is not None for source in (email_source, email_loader, emails)
    )
    if supplied_sources > 1:
        raise ValueError(
            "Provide only one of email_source, email_loader, or emails."
        )
    if supplied_sources == 0:
        raise RuntimeError(
            "No job-alert email source is configured."
        )

    if email_source is None:
        if email_loader is not None:
            email_source = _legacy_email_source(email_loader())
        else:
            assert emails is not None
            email_source = _legacy_email_source(emails)

    initialize_database(db_path)

    candidate_evidence_base = load_candidate_evidence_base(
        db_path=db_path,
        active_only=True,
    )
    if not candidate_evidence_base.evidence_units:
        raise ValueError(
            "No active candidate evidence is available. Upload a resume "
            "before running the agent."
        )

    candidate_preferences = load_candidate_preferences(db_path=db_path)
    run_timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result = AgentRunResult(run_timestamp=run_timestamp)

    _emit(
        progress_callback,
        AgentRunPhase.FINDING_JOB_ALERTS,
        message="Checking recent emails",
    )
    account_key = email_source.account_key().strip()
    if not account_key:
        raise RuntimeError("The configured email source returned a blank account key.")
    metadata_items = list(email_source.list_message_metadata())
    result.discovered_email_count = len(metadata_items)
    _emit(
        progress_callback,
        AgentRunPhase.FINDING_JOB_ALERTS,
        message=(
            f"Found {result.discovered_email_count} recent "
            f"email{'s' if result.discovered_email_count != 1 else ''}"
        ),
        current=result.discovered_email_count,
        total=result.discovered_email_count,
    )

    processed_candidate_count = 0
    known_candidate_total = 0

    for metadata in metadata_items:
        if is_email_processed(
            metadata.message_id,
            db_path=db_path,
            account_key=account_key,
        ):
            result.skipped_processed_email_count += 1
            continue

        job_related = is_job_related_email(
            sender=metadata.sender,
            subject=metadata.subject,
            snippet=metadata.snippet,
        )
        if not job_related:
            mark_email_processed(
                metadata.message_id,
                db_path=db_path,
                account_key=account_key,
            )
            result.processed_email_count += 1
            continue

        # The full message is fetched only after metadata triage says the email
        # is job-related. A technical failure here intentionally leaves the
        # message unprocessed so a later Agent Run can retry it.
        email = email_source.get_message(metadata.message_id)
        job_candidates = extract_job_candidates_from_email(
            source=email.source,
            message_id=email.message_id,
            email_body=email.body,
            email_links=email.links,
        )
        result.extracted_candidate_count += len(job_candidates)
        known_candidate_total += len(job_candidates)

        if not job_candidates:
            mark_email_processed(
                email.message_id,
                db_path=db_path,
                account_key=account_key,
            )
            result.processed_email_count += 1
            continue

        # Important: if any technical exception occurs below, this email is
        # intentionally NOT marked processed. A later run retries the email;
        # posting_url dedupe protects opportunities already persisted before
        # the failure.
        for candidate in job_candidates:
            current_candidate_number = processed_candidate_count + 1
            _emit(
                progress_callback,
                AgentRunPhase.ANALYZING_OPPORTUNITIES,
                message=(
                    "Processing opportunity "
                    f"{current_candidate_number} of {known_candidate_total}"
                ),
                current=current_candidate_number,
                total=known_candidate_total,
            )

            candidate_result = process_job_candidate(
                job_candidate=candidate,
                candidate_evidence_base=candidate_evidence_base,
                candidate_preferences=candidate_preferences,
                db_path=db_path,
                created_at=run_timestamp,
                # Internal verification / analysis / save phases are still
                # executed by the core workflow, but the product UI now
                # exposes one simpler opportunity-level progress step.
                progress_callback=None,
            )
            result.new_opportunities.extend(
                candidate_result.analyzed_opportunities
            )
            result.duplicate_opportunity_ids.extend(
                candidate_result.duplicate_opportunity_ids
            )
            processed_candidate_count += 1
            _emit(
                progress_callback,
                AgentRunPhase.ANALYZING_OPPORTUNITIES,
                message=(
                    "Processed opportunity "
                    f"{processed_candidate_count} of {known_candidate_total}"
                ),
                current=processed_candidate_count,
                total=known_candidate_total,
            )

        mark_email_processed(
            email.message_id,
            db_path=db_path,
            account_key=account_key,
        )
        result.processed_email_count += 1

    _emit(
        progress_callback,
        AgentRunPhase.COMPLETE,
        message="Complete",
        current=processed_candidate_count,
        total=known_candidate_total,
    )
    return result
