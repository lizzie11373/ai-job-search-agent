from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from pathlib import Path

from job_agent.agents.evidence_matcher import (
    match_requirements_to_evidence,
)
from job_agent.agents.job_resolution import (
    resolve_job_candidate,
)
from job_agent.agents.job_attribute_extractor import (
    extract_grounded_job_attributes,
)
from job_agent.agents.negative_conclusion_verifier import (
    verify_negative_mappings,
)
from job_agent.agents.reconciler import (
    finalize_mappings,
)
from job_agent.agents.requirement_analyzer import (
    extract_requirements_from_jd,
)
from job_agent.agents.requirement_validator import (
    validate_requirements,
)
from job_agent.models.candidate import (
    CandidateEvidenceBase,
)
from job_agent.models.job_candidate import (
    JobCandidate,
    JobVerificationResult,
)
from job_agent.models.opportunity import (
    JobOpportunity,
)
from job_agent.models.preference import (
    CandidatePreferenceProfile,
    JobAttributeProfile,
)
from job_agent.models.resolved_job_posting import (
    JobDeduplicationResult,
    ResolvedJobPosting,
)
from job_agent.scoring.preference_check import (
    check_preferences,
)
from job_agent.scoring.pursuit_priority import (
    calculate_pursuit_priority,
)
from job_agent.scoring.requirement_fit import (
    calculate_requirement_fit,
)
from job_agent.storage.database import (
    DEFAULT_DB_PATH,
)
from job_agent.storage.opportunity_repository import (
    load_job_opportunity_by_posting_url,
    create_completed_job_opportunity_analysis,
)


class PostingWorkflowOutcome(StrEnum):
    ANALYZED = "ANALYZED"
    DUPLICATE = "DUPLICATE"


@dataclass
class PostingWorkflowResult:
    outcome: PostingWorkflowOutcome
    posting_url: str
    opportunity: JobOpportunity | None = None
    duplicate_of_opportunity_id: str | None = None


@dataclass
class JobCandidateWorkflowResult:
    """
    Product-level result for processing one discovery JobCandidate.

    Technical failures are intentionally not represented as a business
    outcome here. They bubble as exceptions so the caller can retry.
    """

    candidate: JobCandidate
    posting_results: list[PostingWorkflowResult] = field(
        default_factory=list
    )

    @property
    def analyzed_opportunities(self) -> list[JobOpportunity]:
        return [
            result.opportunity
            for result in self.posting_results
            if (
                result.outcome
                == PostingWorkflowOutcome.ANALYZED
                and result.opportunity is not None
            )
        ]

    @property
    def duplicate_opportunity_ids(self) -> list[str]:
        return [
            result.duplicate_of_opportunity_id
            for result in self.posting_results
            if (
                result.outcome
                == PostingWorkflowOutcome.DUPLICATE
                and result.duplicate_of_opportunity_id is not None
            )
        ]


def build_opportunity_id(posting_url: str) -> str:
    """
    Deterministic V1 opportunity ID derived from the resolved posting URL.

    This is an internal durable key, not a claim that posting_url is the
    globally canonical identity of the underlying job.
    """

    cleaned_url = posting_url.strip()

    if not cleaned_url:
        raise ValueError(
            "Cannot build opportunity ID from an empty posting_url."
        )

    digest = sha256(
        cleaned_url.encode("utf-8")
    ).hexdigest()[:24]

    return f"opp_{digest}"


def build_minimal_job_attributes(
    resolved_posting: ResolvedJobPosting,
) -> JobAttributeProfile:
    """Compatibility wrapper around the grounded attribute extractor."""
    return extract_grounded_job_attributes(resolved_posting)


def _build_match_gap_summaries(
    *,
    validated_requirements,
    finalized_mappings,
) -> tuple[list[str], list[str]]:
    """
    Preserve the existing product summary rule:

    STRONG -> strong match
    WEAK / NOT_CLEARLY_SUPPORTED -> main gap

    PARTIAL remains visible in detailed requirement mappings but is not
    promoted into either lightweight summary bucket.
    """

    requirements_by_id = {
        requirement.requirement_id: requirement
        for requirement in validated_requirements
    }

    strong_matches: list[str] = []
    main_gaps: list[str] = []

    for mapping in finalized_mappings:
        requirement = requirements_by_id.get(
            mapping.requirement_id
        )

        if requirement is None:
            continue

        if mapping.support_level == "STRONG":
            strong_matches.append(
                requirement.requirement
            )
        elif mapping.support_level in {
            "WEAK",
            "NOT_CLEARLY_SUPPORTED",
        }:
            main_gaps.append(
                requirement.requirement
            )

    return strong_matches, main_gaps


def analyze_and_persist_resolved_posting(
    *,
    resolved_posting: ResolvedJobPosting,
    candidate_evidence_base: CandidateEvidenceBase,
    candidate_preferences: CandidatePreferenceProfile | None = None,
    job_attributes: JobAttributeProfile | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
    created_at: str | None = None,
    progress_callback=None,
) -> JobOpportunity:
    """
    Run the candidate-background <-> job matching core for one VERIFIED + NEW
    resolved posting, then atomically persist the completed analysis.

    Pipeline:

        verified full JD
            -> requirement extraction
            -> requirement grounding validation
            -> first-pass requirement/evidence matching
            -> negative-conclusion verification
            -> reconciliation
            -> deterministic requirement-fit calculation
            -> optional preference safety check
            -> pursuit priority
            -> match/gap summaries
            -> atomic persistence
    """

    if (
        resolved_posting.deduplication_result
        != JobDeduplicationResult.NEW
    ):
        raise ValueError(
            "Resolved posting must be NEW before analysis."
        )

    opportunity_id = build_opportunity_id(
        resolved_posting.posting_url
    )

    job_opportunity = (
        resolved_posting.promote_to_job_opportunity(
            opportunity_id=opportunity_id
        )
    )
    job_opportunity.created_at = created_at

    if progress_callback is not None:
        progress_callback("ANALYZING_OPPORTUNITIES")

    extracted_requirements = extract_requirements_from_jd(
        jd_text=job_opportunity.jd_text
    )

    all_validated_requirements = validate_requirements(
        requirements=extracted_requirements,
        original_jd_text=job_opportunity.jd_text,
    )

    validated_requirements = [
        requirement
        for requirement in all_validated_requirements
        if requirement.grounding_status == "VALIDATED"
    ]

    if not validated_requirements:
        raise ValueError(
            "Opportunity Analysis produced zero validated job requirements."
        )

    first_pass_mappings = match_requirements_to_evidence(
        requirements=validated_requirements,
        evidence_base=candidate_evidence_base,
    )

    negative_verifications = verify_negative_mappings(
        mappings=first_pass_mappings,
        requirements=validated_requirements,
        evidence_base=candidate_evidence_base,
    )

    finalized_mappings = finalize_mappings(
        mappings=first_pass_mappings,
        verifications=negative_verifications,
        requirements=validated_requirements,
        evidence_base=candidate_evidence_base,
    )

    requirement_fit = calculate_requirement_fit(
        requirements=validated_requirements,
        finalized_mappings=finalized_mappings,
    )

    # Preference is intentionally separate from requirement fit.
    if candidate_preferences is None:
        preference_results = {}
    else:
        effective_job_attributes = (
            job_attributes
            if job_attributes is not None
            else extract_grounded_job_attributes(resolved_posting)
        )

        preference_results = check_preferences(
            candidate_preferences=candidate_preferences,
            job_attributes=effective_job_attributes,
        )

    if candidate_preferences is None:
        effective_job_attributes = extract_grounded_job_attributes(resolved_posting)

    job_opportunity.job_attributes = effective_job_attributes

    pursuit_priority = calculate_pursuit_priority(
        requirement_fit_score=requirement_fit.score,
        preference_results=preference_results,
    )

    strong_matches, main_gaps = (
        _build_match_gap_summaries(
            validated_requirements=validated_requirements,
            finalized_mappings=finalized_mappings,
        )
    )

    job_opportunity.requirement_fit_score = (
        requirement_fit.score
    )
    job_opportunity.preference_results = (
        preference_results
    )
    job_opportunity.pursuit_priority = (
        pursuit_priority
    )
    job_opportunity.strong_matches = (
        strong_matches
    )
    job_opportunity.main_gaps = (
        main_gaps
    )

    if progress_callback is not None:
        progress_callback("SAVING_RESULTS")

    create_completed_job_opportunity_analysis(
        opportunity=job_opportunity,
        requirements=validated_requirements,
        mappings=finalized_mappings,
        db_path=db_path,
    )

    return job_opportunity


def process_job_candidate(
    *,
    job_candidate: JobCandidate,
    candidate_evidence_base: CandidateEvidenceBase,
    candidate_preferences: CandidatePreferenceProfile | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
    created_at: str | None = None,
    progress_callback=None,
) -> JobCandidateWorkflowResult:
    """
    Run the complete V1 core workflow for one discovery lead:

        JobCandidate
            -> real JD Resolution / Verification
            -> exact posting-URL dedupe
            -> candidate/job Opportunity Analysis
            -> persistence

    Normal UNVERIFIED is a valid terminal business result.

    Technical failures from Search / Fetch semantic verification / downstream
    analysis bubble upward and therefore remain retryable.
    """

    if not candidate_evidence_base.evidence_units:
        raise ValueError(
            "Candidate evidence base is empty. "
            "Build or load grounded candidate evidence before "
            "running Opportunity Analysis."
        )

    result = JobCandidateWorkflowResult(
        candidate=job_candidate
    )

    if progress_callback is not None:
        progress_callback("VERIFYING_JOB_POSTINGS")

    resolved_postings = resolve_job_candidate(
        job_candidate
    )

    if (
        job_candidate.verification_result
        == JobVerificationResult.UNVERIFIED
    ):
        return result

    if (
        job_candidate.verification_result
        != JobVerificationResult.VERIFIED
    ):
        raise RuntimeError(
            "JD Resolution returned without a terminal VERIFIED/"
            "UNVERIFIED business result."
        )

    for resolved_posting in resolved_postings:
        existing_opportunity = (
            load_job_opportunity_by_posting_url(
                resolved_posting.posting_url,
                db_path=db_path,
            )
        )

        if existing_opportunity is not None:
            resolved_posting.deduplication_result = (
                JobDeduplicationResult.DUPLICATE
            )

            result.posting_results.append(
                PostingWorkflowResult(
                    outcome=(
                        PostingWorkflowOutcome.DUPLICATE
                    ),
                    posting_url=(
                        resolved_posting.posting_url
                    ),
                    duplicate_of_opportunity_id=(
                        existing_opportunity.opportunity_id
                    ),
                )
            )
            continue

        resolved_posting.deduplication_result = (
            JobDeduplicationResult.NEW
        )

        opportunity = (
            analyze_and_persist_resolved_posting(
                resolved_posting=resolved_posting,
                candidate_evidence_base=(
                    candidate_evidence_base
                ),
                candidate_preferences=(
                    candidate_preferences
                ),
                db_path=db_path,
                created_at=created_at,
                progress_callback=progress_callback,
            )
        )

        result.posting_results.append(
            PostingWorkflowResult(
                outcome=(
                    PostingWorkflowOutcome.ANALYZED
                ),
                posting_url=(
                    resolved_posting.posting_url
                ),
                opportunity=opportunity,
            )
        )

    return result
