from pathlib import Path

from job_agent.storage.database import (
    DEFAULT_DB_PATH,
    get_connection,
)


LEGACY_EMAIL_ACCOUNT_KEY = "legacy:default"


def _validated_account_key(account_key: str) -> str:
    normalized = account_key.strip()
    if not normalized:
        raise ValueError("account_key must not be blank")
    return normalized


def is_email_processed(
    message_id: str,
    db_path: str | Path = DEFAULT_DB_PATH,
    *,
    account_key: str = LEGACY_EMAIL_ACCOUNT_KEY,
) -> bool:
    """
    Return True only when this mailbox+message pair previously finished processing.

    Absence means either:
    - the email has never been seen in this mailbox, or
    - a previous attempt did not finish and should be retried.
    """

    connection = get_connection(db_path)
    account_key = _validated_account_key(account_key)

    try:
        row = connection.execute(
            """
            SELECT 1
            FROM processed_emails
            WHERE account_key = ? AND message_id = ?
            """,
            (account_key, message_id),
        ).fetchone()

        return row is not None

    finally:
        connection.close()


def mark_email_processed(
    message_id: str,
    db_path: str | Path = DEFAULT_DB_PATH,
    *,
    account_key: str = LEGACY_EMAIL_ACCOUNT_KEY,
) -> None:
    """
    Mark one mailbox+message pair processed only after all of its JobCandidates
    have reached a terminal business outcome for the current run.

    Do NOT call this when processing stops because of a technical execution
    failure; leaving the pair absent enables retry. The account key keeps two
    Gmail inboxes with the same Gmail message ID from suppressing one another.
    """

    connection = get_connection(db_path)
    account_key = _validated_account_key(account_key)

    try:
        with connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO processed_emails (
                    account_key,
                    message_id
                )
                VALUES (?, ?)
                """,
                (account_key, message_id),
            )

    finally:
        connection.close()
