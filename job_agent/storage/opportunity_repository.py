from __future__ import annotations

import json
from pathlib import Path

from job_agent.models.evaluation import (
    EvidenceMatch,
    RequirementEvidenceMapping,
)
from job_agent.models.job import JobRequirement
from job_agent.models.job_candidate import JobVerificationLevel
from job_agent.models.opportunity import (
    JobOpportunity,
    PursuitPriority,
    UserDecision,
)
from job_agent.models.preference import (
    JobAttributeProfile,
    PreferenceCheckResult,
)
from job_agent.storage.database import DEFAULT_DB_PATH, get_connection


def _enum_value_or_none(value):
    if value is None:
        return None
    return getattr(value, "value", value)


def _serialize_preference_results(
    preference_results: dict[str, PreferenceCheckResult],
) -> str:
    return json.dumps(
        {
            category: _enum_value_or_none(result)
            for category, result in preference_results.items()
        },
        sort_keys=True,
    )


def _deserialize_preference_results(
    preference_results_json: str | None,
) -> dict[str, PreferenceCheckResult]:
    if not preference_results_json:
        return {}
    raw = json.loads(preference_results_json)
    return {
        category: PreferenceCheckResult(value)
        for category, value in raw.items()
    }


def _serialize_string_list(values: list[str]) -> str:
    return json.dumps(list(values), ensure_ascii=False)


def _deserialize_string_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [str(item) for item in json.loads(value)]


def _serialize_job_attributes(attributes: JobAttributeProfile) -> str:
    return json.dumps(
        {
            "location": attributes.location,
            "work_mode": attributes.work_mode,
            "employment_type": attributes.employment_type,
            "compensation_min": attributes.compensation_min,
            "compensation_max": attributes.compensation_max,
            "industry": attributes.industry,
            "company_size": attributes.company_size,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _deserialize_job_attributes(raw_json: str | None) -> JobAttributeProfile:
    if not raw_json:
        return JobAttributeProfile()
    raw = json.loads(raw_json)
    return JobAttributeProfile(
        location=raw.get("location"),
        work_mode=raw.get("work_mode"),
        employment_type=raw.get("employment_type"),
        compensation_min=raw.get("compensation_min"),
        compensation_max=raw.get("compensation_max"),
        industry=raw.get("industry"),
        company_size=raw.get("company_size"),
    )


def _row_to_job_opportunity(row) -> JobOpportunity:
    row_keys = set(row.keys())
    return JobOpportunity(
        opportunity_id=row["opportunity_id"],
        title=row["title"],
        company=row["company"],
        source=row["source"],
        location=row["location"],
        source_url=row["source_url"],
        source_message_id=row["source_message_id"],
        source_item_id=row["source_item_id"],
        posting_url=row["posting_url"],
        jd_text=row["jd_text"],
        verification_level=JobVerificationLevel(
            row["verification_level"]
        ),
        job_attributes=_deserialize_job_attributes(
            row["job_attributes_json"]
            if "job_attributes_json" in row_keys
            else None
        ),
        requirement_fit_score=row["requirement_fit_score"],
        pursuit_priority=PursuitPriority(row["pursuit_priority"]),
        preference_results=_deserialize_preference_results(
            row["preference_results_json"]
        ),
        strong_matches=_deserialize_string_list(
            row["strong_matches_json"]
        ),
        main_gaps=_deserialize_string_list(row["main_gaps_json"]),
        created_at=(
            row["created_at"] if "created_at" in row_keys else None
        ),
        user_decision=(
            UserDecision(row["user_decision"])
            if row["user_decision"] is not None
            else None
        ),
    )


def load_job_opportunity(
    opportunity_id: str,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> JobOpportunity | None:
    connection = get_connection(db_path)
    try:
        row = connection.execute(
            "SELECT * FROM job_opportunities WHERE opportunity_id = ?",
            (opportunity_id,),
        ).fetchone()
    finally:
        connection.close()
    return None if row is None else _row_to_job_opportunity(row)


def load_job_opportunity_by_posting_url(
    posting_url: str,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> JobOpportunity | None:
    connection = get_connection(db_path)
    try:
        row = connection.execute(
            "SELECT * FROM job_opportunities WHERE posting_url = ?",
            (posting_url.strip(),),
        ).fetchone()
    finally:
        connection.close()
    return None if row is None else _row_to_job_opportunity(row)


def load_job_opportunity_by_canonical_url(
    canonical_job_url: str,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> JobOpportunity | None:
    """Compatibility wrapper for older local scripts."""
    return load_job_opportunity_by_posting_url(
        canonical_job_url,
        db_path=db_path,
    )


def _validate_completed_analysis(opportunity: JobOpportunity) -> None:
    if opportunity.requirement_fit_score is None:
        raise ValueError(
            "Cannot persist completed opportunity analysis without "
            "requirement_fit_score."
        )
    if opportunity.pursuit_priority is None:
        raise ValueError(
            "Cannot persist completed opportunity analysis without "
            "pursuit_priority."
        )
    if opportunity.user_decision is not None:
        raise ValueError(
            "Completed analysis must be created before a human decision. "
            "Use set_user_decision() after creation."
        )


def create_completed_job_opportunity_analysis(
    *,
    opportunity: JobOpportunity,
    requirements: list[JobRequirement],
    mappings: list[RequirementEvidenceMapping],
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    """
    Atomically CREATE one completed analysis snapshot.

    There is deliberately no UPSERT. If opportunity_id or posting_url already
    exists SQLite raises IntegrityError instead of overwriting historical
    analysis. Human decisions are changed only through set_user_decision().
    """

    _validate_completed_analysis(opportunity)

    requirements_by_id = {
        requirement.requirement_id: requirement
        for requirement in requirements
    }
    for mapping in mappings:
        if mapping.requirement_id not in requirements_by_id:
            raise ValueError(
                "Mapping references requirement_id not present in "
                f"requirements: {mapping.requirement_id}"
            )

    connection = get_connection(db_path)
    try:
        with connection:
            connection.execute(
                """
                INSERT INTO job_opportunities (
                    opportunity_id,
                    title,
                    company,
                    source,
                    location,
                    source_url,
                    source_message_id,
                    source_item_id,
                    posting_url,
                    jd_text,
                    verification_level,
                    requirement_fit_score,
                    pursuit_priority,
                    preference_results_json,
                    strong_matches_json,
                    main_gaps_json,
                    job_attributes_json,
                    created_at,
                    user_decision
                )
                VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, COALESCE(?, CURRENT_TIMESTAMP), NULL
                )
                """,
                (
                    opportunity.opportunity_id,
                    opportunity.title,
                    opportunity.company,
                    opportunity.source,
                    opportunity.location,
                    opportunity.source_url,
                    opportunity.source_message_id,
                    opportunity.source_item_id,
                    opportunity.posting_url,
                    opportunity.jd_text,
                    opportunity.verification_level.value,
                    opportunity.requirement_fit_score,
                    opportunity.pursuit_priority.value,
                    _serialize_preference_results(
                        opportunity.preference_results
                    ),
                    _serialize_string_list(opportunity.strong_matches),
                    _serialize_string_list(opportunity.main_gaps),
                    _serialize_job_attributes(opportunity.job_attributes),
                    opportunity.created_at,
                ),
            )

            for requirement in requirements:
                connection.execute(
                    """
                    INSERT INTO job_requirements (
                        opportunity_id,
                        requirement_id,
                        requirement,
                        category,
                        requirement_level,
                        jd_source_text,
                        jd_section,
                        grounding_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        opportunity.opportunity_id,
                        requirement.requirement_id,
                        requirement.requirement,
                        requirement.category,
                        requirement.requirement_level,
                        requirement.jd_source_text,
                        requirement.jd_section,
                        requirement.grounding_status,
                    ),
                )

            for mapping in mappings:
                connection.execute(
                    """
                    INSERT INTO requirement_mappings (
                        opportunity_id,
                        requirement_id,
                        support_level,
                        reason
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        opportunity.opportunity_id,
                        mapping.requirement_id,
                        mapping.support_level,
                        mapping.reason,
                    ),
                )

                for evidence_match in mapping.evidence_matches:
                    connection.execute(
                        """
                        INSERT INTO evidence_matches (
                            opportunity_id,
                            requirement_id,
                            evidence_id,
                            relationship,
                            reason
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            opportunity.opportunity_id,
                            mapping.requirement_id,
                            evidence_match.evidence_id,
                            evidence_match.relationship,
                            evidence_match.reason,
                        ),
                    )
    finally:
        connection.close()


def save_complete_job_opportunity_analysis(
    *,
    opportunity: JobOpportunity,
    requirements: list[JobRequirement],
    mappings: list[RequirementEvidenceMapping],
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    """
    Compatibility name retained for existing call sites.

    Semantics are now create-only; this function cannot overwrite analysis.
    """
    create_completed_job_opportunity_analysis(
        opportunity=opportunity,
        requirements=requirements,
        mappings=mappings,
        db_path=db_path,
    )


def set_user_decision(
    opportunity_id: str,
    decision: UserDecision | str | None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> JobOpportunity:
    """Update only the mutable human-decision field."""

    if decision is None:
        decision_value = None
    else:
        decision_value = UserDecision(decision).value

    connection = get_connection(db_path)
    try:
        with connection:
            cursor = connection.execute(
                """
                UPDATE job_opportunities
                SET user_decision = ?
                WHERE opportunity_id = ?
                """,
                (decision_value, opportunity_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(
                    f"Unknown opportunity_id: {opportunity_id}"
                )
    finally:
        connection.close()

    loaded = load_job_opportunity(opportunity_id, db_path=db_path)
    assert loaded is not None
    return loaded


def load_job_requirements(
    opportunity_id: str,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[JobRequirement]:
    connection = get_connection(db_path)
    try:
        rows = connection.execute(
            """
            SELECT
                requirement_id,
                requirement,
                category,
                requirement_level,
                jd_source_text,
                jd_section,
                grounding_status
            FROM job_requirements
            WHERE opportunity_id = ?
            ORDER BY requirement_id
            """,
            (opportunity_id,),
        ).fetchall()
    finally:
        connection.close()

    return [
        JobRequirement(
            requirement_id=row["requirement_id"],
            requirement=row["requirement"],
            category=row["category"],
            requirement_level=row["requirement_level"],
            jd_source_text=row["jd_source_text"],
            jd_section=row["jd_section"],
            grounding_status=row["grounding_status"],
        )
        for row in rows
    ]


def load_requirement_mappings(
    opportunity_id: str,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[RequirementEvidenceMapping]:
    connection = get_connection(db_path)
    try:
        rows = connection.execute(
            """
            SELECT
                rm.requirement_id,
                rm.support_level,
                rm.reason AS mapping_reason,
                em.evidence_id,
                em.relationship,
                em.reason AS evidence_reason
            FROM requirement_mappings AS rm
            LEFT JOIN evidence_matches AS em
                ON rm.opportunity_id = em.opportunity_id
               AND rm.requirement_id = em.requirement_id
            WHERE rm.opportunity_id = ?
            ORDER BY rm.requirement_id, em.evidence_id
            """,
            (opportunity_id,),
        ).fetchall()
    finally:
        connection.close()

    mappings_by_requirement: dict[str, RequirementEvidenceMapping] = {}
    for row in rows:
        requirement_id = row["requirement_id"]
        if requirement_id not in mappings_by_requirement:
            mappings_by_requirement[requirement_id] = RequirementEvidenceMapping(
                requirement_id=requirement_id,
                evidence_matches=[],
                support_level=row["support_level"],
                reason=row["mapping_reason"],
            )
        if row["evidence_id"] is not None:
            mappings_by_requirement[requirement_id].evidence_matches.append(
                EvidenceMatch(
                    evidence_id=row["evidence_id"],
                    relationship=row["relationship"],
                    reason=row["evidence_reason"],
                )
            )
    return list(mappings_by_requirement.values())


def load_all_job_opportunities(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[JobOpportunity]:
    connection = get_connection(db_path)
    try:
        rows = connection.execute(
            "SELECT * FROM job_opportunities"
        ).fetchall()
    finally:
        connection.close()
    return [_row_to_job_opportunity(row) for row in rows]
