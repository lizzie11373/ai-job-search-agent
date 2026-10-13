from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from job_agent.models.candidate import CandidateSource, CandidateSourceType
from job_agent.ingestion.candidate_source_upload import DEFAULT_CANDIDATE_SOURCE_DIR
from job_agent.models.opportunity import (
    JobOpportunity,
    PursuitPriority,
    UserDecision,
)
from job_agent.models.preference import CandidatePreferenceProfile
from job_agent.scoring.pursuit_priority import PRIORITY_ORDER
from job_agent.storage.app_state_repository import (
    is_setup_completed,
    set_setup_completed,
)
from job_agent.storage.candidate_repository import (
    get_active_resume_source,
    list_candidate_sources,
    load_evidence_by_id,
)
from job_agent.storage.database import DEFAULT_DB_PATH, initialize_database
from job_agent.storage.opportunity_repository import (
    load_all_job_opportunities,
    load_job_opportunity,
    load_job_requirements,
    load_requirement_mappings,
    set_user_decision as _set_user_decision,
)
from job_agent.storage.preference_repository import (
    load_candidate_preferences,
    preference_summary,
    save_candidate_preferences,
)
from job_agent.workflows.candidate_profile_ingestion import (
    CandidateDocumentIngestionResult,
    ingest_uploaded_resume_markdown,
    ingest_uploaded_supporting_markdown,
)


@dataclass(frozen=True)
class OpportunityListItem:
    opportunity_id: str
    title: str
    company: str
    location: str | None
    pursuit_priority: PursuitPriority
    requirement_fit_score: float
    preference_matched_count: int
    preference_configured_count: int
    user_decision: UserDecision | None
    created_at: str | None


@dataclass(frozen=True)
class EvidenceDetail:
    evidence_id: str
    claim: str
    source_document: str
    source_text: str


@dataclass(frozen=True)
class RequirementDetail:
    requirement_id: str
    requirement: str
    category: str
    requirement_level: str
    support_level: str
    match_reason: str
    evidence: tuple[EvidenceDetail, ...]


@dataclass(frozen=True)
class OpportunityDetail:
    opportunity: JobOpportunity
    preference_matched_count: int
    preference_configured_count: int
    requirements: tuple[RequirementDetail, ...]


@dataclass(frozen=True)
class BackgroundState:
    current_resume: CandidateSource | None
    supporting_materials: tuple[CandidateSource, ...]


def _as_list_item(opportunity: JobOpportunity) -> OpportunityListItem:
    matched, configured = preference_summary(opportunity.preference_results)
    assert opportunity.pursuit_priority is not None
    assert opportunity.requirement_fit_score is not None
    return OpportunityListItem(
        opportunity_id=opportunity.opportunity_id,
        title=opportunity.title,
        company=opportunity.company,
        location=opportunity.location,
        pursuit_priority=opportunity.pursuit_priority,
        requirement_fit_score=opportunity.requirement_fit_score,
        preference_matched_count=matched,
        preference_configured_count=configured,
        user_decision=opportunity.user_decision,
        created_at=opportunity.created_at,
    )


def _created_timestamp(value: str | None) -> float:
    if not value:
        return 0.0
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return 0.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def _priority_rank(priority: PursuitPriority) -> int:
    return PRIORITY_ORDER.index(priority)


def _preference_rate(item: OpportunityListItem) -> float:
    if item.preference_configured_count == 0:
        return 0.0
    return item.preference_matched_count / item.preference_configured_count


def list_needs_review(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[OpportunityListItem]:
    """
    Needs Review = persisted analysis with no human decision.

    Sort: priority -> requirement fit -> preference match rate -> newer first.
    For 0/0 preferences the tie-break contributes no positive advantage.
    """

    initialize_database(db_path)
    items = [
        _as_list_item(opp)
        for opp in load_all_job_opportunities(db_path=db_path)
        if opp.user_decision is None
    ]
    return sorted(
        items,
        key=lambda item: (
            _priority_rank(item.pursuit_priority),
            -item.requirement_fit_score,
            -_preference_rate(item),
            -_created_timestamp(item.created_at),
        ),
    )


def list_reviewed(
    *,
    decision: UserDecision | str | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[OpportunityListItem]:
    initialize_database(db_path)
    selected = UserDecision(decision) if decision is not None else None
    items = [
        _as_list_item(opp)
        for opp in load_all_job_opportunities(db_path=db_path)
        if opp.user_decision is not None
        and (selected is None or opp.user_decision == selected)
    ]
    return sorted(
        items,
        key=lambda item: (
            -_created_timestamp(item.created_at),
            _priority_rank(item.pursuit_priority),
        ),
    )


def get_opportunity_detail(
    opportunity_id: str,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> OpportunityDetail:
    """
    Hydrate the UI Job Detail in one backend call.

    Historical evidence lookup deliberately ignores source activeness. UI does
    not receive source_section or DIRECT/ADJACENT taxonomy; the requirement's
    match_reason carries the direct-vs-adjacent/gap explanation.
    """

    initialize_database(db_path)
    opportunity = load_job_opportunity(opportunity_id, db_path=db_path)
    if opportunity is None:
        raise KeyError(f"Unknown opportunity_id: {opportunity_id}")

    requirements = {
        requirement.requirement_id: requirement
        for requirement in load_job_requirements(
            opportunity_id,
            db_path=db_path,
        )
    }
    mappings = {
        mapping.requirement_id: mapping
        for mapping in load_requirement_mappings(
            opportunity_id,
            db_path=db_path,
        )
    }

    details: list[RequirementDetail] = []
    for requirement_id, requirement in requirements.items():
        mapping = mappings.get(requirement_id)
        evidence_details: list[EvidenceDetail] = []
        if mapping is not None:
            for evidence_match in mapping.evidence_matches:
                evidence = load_evidence_by_id(
                    evidence_match.evidence_id,
                    db_path=db_path,
                )
                if evidence is None:
                    raise RuntimeError(
                        "Historical analysis references missing evidence: "
                        f"{evidence_match.evidence_id}"
                    )
                evidence_details.append(
                    EvidenceDetail(
                        evidence_id=evidence.evidence_id,
                        claim=evidence.claim,
                        source_document=evidence.source_document,
                        source_text=evidence.source_text,
                    )
                )

        details.append(
            RequirementDetail(
                requirement_id=requirement_id,
                requirement=requirement.requirement,
                category=requirement.category,
                requirement_level=requirement.requirement_level,
                support_level=(
                    mapping.support_level
                    if mapping is not None
                    else "NOT_CLEARLY_SUPPORTED"
                ),
                match_reason=(
                    mapping.reason
                    if mapping is not None
                    else "No finalized requirement mapping was persisted."
                ),
                evidence=tuple(evidence_details),
            )
        )

    matched, configured = preference_summary(opportunity.preference_results)
    return OpportunityDetail(
        opportunity=opportunity,
        preference_matched_count=matched,
        preference_configured_count=configured,
        requirements=tuple(details),
    )


def set_user_decision(
    opportunity_id: str,
    decision: UserDecision | str | None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> JobOpportunity:
    initialize_database(db_path)
    return _set_user_decision(
        opportunity_id,
        decision,
        db_path=db_path,
    )


def get_background_state(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> BackgroundState:
    initialize_database(db_path)
    sources = list_candidate_sources(db_path=db_path, active_only=True)
    return BackgroundState(
        current_resume=get_active_resume_source(db_path=db_path),
        supporting_materials=tuple(
            source
            for source in sources
            if source.source_type == CandidateSourceType.SUPPORTING
        ),
    )


def replace_resume(
    *,
    filename: str,
    content: bytes,
    source_dir=DEFAULT_CANDIDATE_SOURCE_DIR,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> CandidateDocumentIngestionResult:
    initialize_database(db_path)
    return ingest_uploaded_resume_markdown(
        filename=filename,
        content=content,
        source_dir=source_dir,
        db_path=db_path,
    )


def add_supporting_material(
    *,
    filename: str,
    content: bytes,
    source_dir=DEFAULT_CANDIDATE_SOURCE_DIR,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> CandidateDocumentIngestionResult:
    initialize_database(db_path)
    return ingest_uploaded_supporting_markdown(
        filename=filename,
        content=content,
        source_dir=source_dir,
        db_path=db_path,
    )


def get_preferences(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> CandidatePreferenceProfile:
    initialize_database(db_path)
    return load_candidate_preferences(db_path=db_path)


def save_preferences(
    preferences: CandidatePreferenceProfile,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    initialize_database(db_path)
    save_candidate_preferences(preferences, db_path=db_path)


def get_setup_completed(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> bool:
    initialize_database(db_path)
    return is_setup_completed(db_path=db_path)


def mark_setup_completed(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    initialize_database(db_path)
    set_setup_completed(True, db_path=db_path)


def finish_setup_and_run_agent(
    *,
    email_source=None,
    email_loader=None,
    emails=None,
    progress_callback=None,
    db_path: str | Path = DEFAULT_DB_PATH,
):
    """
    Final onboarding action.

    setup_completed is committed first, then the first Agent Run starts. If the
    app closes or the run fails afterward, onboarding is not repeated; the user
    returns to Opportunities and can run the agent again.
    """
    from job_agent.services.agent_run_service import run_agent

    initialize_database(db_path)
    set_setup_completed(True, db_path=db_path)
    return run_agent(
        email_source=email_source,
        email_loader=email_loader,
        emails=emails,
        progress_callback=progress_callback,
        db_path=db_path,
    )
