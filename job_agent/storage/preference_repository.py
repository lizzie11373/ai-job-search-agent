from __future__ import annotations

import json
from pathlib import Path

from job_agent.models.preference import CandidatePreferenceProfile
from job_agent.storage.database import DEFAULT_DB_PATH, get_connection


def _dump(values: set[str]) -> str:
    return json.dumps(sorted(values), ensure_ascii=False)


def _load(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {str(item) for item in json.loads(raw)}


def save_candidate_preferences(
    preferences: CandidatePreferenceProfile,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    """Persist the five optional V1 preference categories. No compensation."""

    connection = get_connection(db_path)
    try:
        with connection:
            connection.execute(
                """
                INSERT INTO candidate_preferences (
                    singleton_id,
                    preferred_locations_json,
                    accepted_work_modes_json,
                    accepted_employment_types_json,
                    preferred_industries_json,
                    preferred_company_sizes_json,
                    updated_at
                ) VALUES (1, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(singleton_id)
                DO UPDATE SET
                    preferred_locations_json = excluded.preferred_locations_json,
                    accepted_work_modes_json = excluded.accepted_work_modes_json,
                    accepted_employment_types_json = excluded.accepted_employment_types_json,
                    preferred_industries_json = excluded.preferred_industries_json,
                    preferred_company_sizes_json = excluded.preferred_company_sizes_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    _dump(preferences.preferred_locations),
                    _dump(preferences.accepted_work_modes),
                    _dump(preferences.accepted_employment_types),
                    _dump(preferences.preferred_industries),
                    _dump(preferences.preferred_company_sizes),
                ),
            )
    finally:
        connection.close()


def load_candidate_preferences(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> CandidatePreferenceProfile:
    connection = get_connection(db_path)
    try:
        row = connection.execute(
            "SELECT * FROM candidate_preferences WHERE singleton_id = 1"
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return CandidatePreferenceProfile()

    return CandidatePreferenceProfile(
        preferred_locations=_load(row["preferred_locations_json"]),
        accepted_work_modes=_load(row["accepted_work_modes_json"]),
        accepted_employment_types=_load(
            row["accepted_employment_types_json"]
        ),
        minimum_compensation=None,
        preferred_industries=_load(row["preferred_industries_json"]),
        preferred_company_sizes=_load(
            row["preferred_company_sizes_json"]
        ),
    )


def preference_summary(
    results,
) -> tuple[int, int]:
    """Return (matched_count, configured_count) for persisted analysis results."""

    configured_count = len(results)
    matched_count = sum(
        1 for result in results.values() if getattr(result, "value", result) == "MATCH"
    )
    return matched_count, configured_count
