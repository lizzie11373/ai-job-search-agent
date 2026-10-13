from pathlib import Path

from job_agent.storage.database import get_connection, initialize_database
from job_agent.storage.email_repository import (
    LEGACY_EMAIL_ACCOUNT_KEY,
    is_email_processed,
    mark_email_processed,
)


def test_processed_email_is_scoped_by_account(tmp_path: Path):
    db_path = tmp_path / "job_agent.db"
    initialize_database(db_path)

    mark_email_processed(
        "same-message",
        db_path=db_path,
        account_key="gmail:first@example.com",
    )

    assert is_email_processed(
        "same-message",
        db_path=db_path,
        account_key="gmail:first@example.com",
    )
    assert not is_email_processed(
        "same-message",
        db_path=db_path,
        account_key="gmail:second@example.com",
    )


def test_old_message_only_schema_migrates_without_dropping_markers(tmp_path: Path):
    db_path = tmp_path / "job_agent.db"
    connection = get_connection(db_path)
    try:
        with connection:
            connection.execute(
                """
                CREATE TABLE processed_emails (
                    message_id TEXT PRIMARY KEY,
                    processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                "INSERT INTO processed_emails (message_id) VALUES (?)",
                ("legacy-message",),
            )
    finally:
        connection.close()

    initialize_database(db_path)

    connection = get_connection(db_path)
    try:
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(processed_emails)"
            ).fetchall()
        }
        row = connection.execute(
            """
            SELECT account_key, message_id
            FROM processed_emails
            WHERE message_id = ?
            """,
            ("legacy-message",),
        ).fetchone()
    finally:
        connection.close()

    assert columns >= {"account_key", "message_id", "processed_at"}
    assert row["account_key"] == LEGACY_EMAIL_ACCOUNT_KEY
    assert row["message_id"] == "legacy-message"
