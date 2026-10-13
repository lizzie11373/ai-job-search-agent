from pathlib import Path

from job_agent.models.job_candidate import JobCandidate
from job_agent.storage.database import DEFAULT_DB_PATH, get_connection


def _enum_value_or_none(value):
    return None if value is None else value.value


def save_job_resolution_attempt(
    *,
    job_candidate: JobCandidate,
    resolved_posting_count: int,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> int:
    """
    Append one resolution-attempt observability row.

    The log is not a workflow checkpoint; retry behavior is still controlled
    by the email workflow and technical-failure policy.
    """

    if job_candidate.execution_status is None:
        raise ValueError(
            "Cannot persist resolution attempt before execution_status is known."
        )

    if resolved_posting_count < 0:
        raise ValueError("resolved_posting_count cannot be negative.")

    connection = get_connection(db_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO job_resolution_attempts (
                source_message_id,
                source,
                source_item_id,
                title,
                company,
                location,
                source_url,
                execution_status,
                verification_result,
                verification_level,
                resolution_reason,
                resolution_error,
                resolved_posting_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_candidate.source_message_id,
                job_candidate.source,
                job_candidate.source_item_id,
                job_candidate.title,
                job_candidate.company,
                job_candidate.location,
                job_candidate.source_url,
                _enum_value_or_none(job_candidate.execution_status),
                _enum_value_or_none(job_candidate.verification_result),
                _enum_value_or_none(job_candidate.verification_level),
                _enum_value_or_none(job_candidate.resolution_reason),
                job_candidate.resolution_error,
                resolved_posting_count,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        connection.close()


def load_job_resolution_attempts(
    *,
    source_message_id: str | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
):
    """Load audit rows newest first."""

    connection = get_connection(db_path)
    try:
        if source_message_id is None:
            return connection.execute(
                """
                SELECT *
                FROM job_resolution_attempts
                ORDER BY attempt_id DESC
                """
            ).fetchall()

        return connection.execute(
            """
            SELECT *
            FROM job_resolution_attempts
            WHERE source_message_id = ?
            ORDER BY attempt_id DESC
            """,
            (source_message_id,),
        ).fetchall()
    finally:
        connection.close()
