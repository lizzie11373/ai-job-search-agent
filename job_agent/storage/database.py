from __future__ import annotations

from pathlib import Path
import sqlite3


DEFAULT_DB_PATH = Path("data/job_agent.db")


# Any one of these indicates a pre-posting_url opportunity schema.
_LEGACY_OPPORTUNITY_COLUMNS = {
    "canonical_job_url",
    "jd_resolution_status",
    "jd_verification_result",
    "jd_source_url",
    "jd_resolution_error",
    "opportunity_analysis_status",
    "opportunity_analysis_error",
}

_LEGACY_EMAIL_ACCOUNT_KEY = "legacy:default"


_BASE_OPPORTUNITY_COLUMNS = {
    "opportunity_id",
    "title",
    "company",
    "source",
    "location",
    "source_url",
    "source_message_id",
    "source_item_id",
    "posting_url",
    "jd_text",
    "verification_level",
    "requirement_fit_score",
    "pursuit_priority",
    "preference_results_json",
    "strong_matches_json",
    "main_gaps_json",
    "user_decision",
}


def get_connection(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> sqlite3.Connection:
    """Create a SQLite connection with foreign-key enforcement."""

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _table_exists(
    connection: sqlite3.Connection,
    table_name: str,
) -> bool:
    row = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        (table_name,),
    ).fetchone()
    return row is not None


def _table_columns(
    connection: sqlite3.Connection,
    table_name: str,
) -> set[str]:
    if not _table_exists(connection, table_name):
        return set()
    return {
        row["name"]
        for row in connection.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()
    }


def _reset_pre_posting_url_opportunity_schema_if_needed(
    connection: sqlite3.Connection,
) -> bool:
    """
    Keep the existing prototype migration only for genuinely old schemas.

    The current repository already uses posting_url-based durable product
    state. New product-state additions such as created_at and job attributes
    are migrated in place and do NOT trigger an opportunity-data reset.
    """

    columns = _table_columns(connection, "job_opportunities")
    if not columns:
        return False

    incompatible = (
        bool(columns & _LEGACY_OPPORTUNITY_COLUMNS)
        or not _BASE_OPPORTUNITY_COLUMNS.issubset(columns)
    )
    if not incompatible:
        return False

    connection.execute("DROP TABLE IF EXISTS evidence_matches")
    connection.execute("DROP TABLE IF EXISTS requirement_mappings")
    connection.execute("DROP TABLE IF EXISTS job_requirements")
    connection.execute("DROP TABLE IF EXISTS job_opportunities")

    if _table_exists(connection, "processed_emails"):
        connection.execute("DELETE FROM processed_emails")

    return True


def _ensure_column(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    ddl_fragment: str,
) -> None:
    if column_name in _table_columns(connection, table_name):
        return
    connection.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl_fragment}"
    )




def _ensure_processed_email_account_scope(
    connection: sqlite3.Connection,
) -> None:
    """
    Migrate processed-email dedupe from message-only to mailbox+message identity.

    Existing markers came from the pre-account-aware local prototype, so they
    are retained under a legacy account key. New Gmail runs use a stable Gmail
    account key, which lets the user replace the active inbox without one
    mailbox suppressing messages from another.
    """

    columns = _table_columns(connection, "processed_emails")
    if not columns or "account_key" in columns:
        return

    connection.execute("DROP TABLE IF EXISTS processed_emails_new")
    connection.execute(
        """
        CREATE TABLE processed_emails_new (
            account_key TEXT NOT NULL,
            message_id TEXT NOT NULL,
            processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (account_key, message_id)
        )
        """
    )
    connection.execute(
        """
        INSERT INTO processed_emails_new (
            account_key,
            message_id,
            processed_at
        )
        SELECT ?, message_id, processed_at
        FROM processed_emails
        """,
        (_LEGACY_EMAIL_ACCOUNT_KEY,),
    )
    connection.execute("DROP TABLE processed_emails")
    connection.execute(
        "ALTER TABLE processed_emails_new RENAME TO processed_emails"
    )


def _ensure_evidence_match_delete_guard(
    connection: sqlite3.Connection,
) -> None:
    """
    Ensure historical evidence references cannot disappear through a
    candidate-evidence delete.

    Earlier versions used ON DELETE CASCADE from evidence_matches to
    candidate_evidence. That could silently erase historical analysis when a
    resume was replaced. Rebuild this one child table with ON DELETE RESTRICT.
    """

    if not _table_exists(connection, "evidence_matches"):
        return

    foreign_keys = connection.execute(
        "PRAGMA foreign_key_list(evidence_matches)"
    ).fetchall()

    evidence_fk = next(
        (
            row
            for row in foreign_keys
            if row["table"] == "candidate_evidence"
            and row["from"] == "evidence_id"
        ),
        None,
    )

    if evidence_fk is not None and evidence_fk["on_delete"].upper() == "RESTRICT":
        return

    connection.execute(
        """
        CREATE TABLE evidence_matches_new (
            opportunity_id TEXT NOT NULL,
            requirement_id TEXT NOT NULL,
            evidence_id TEXT NOT NULL,
            relationship TEXT NOT NULL,
            reason TEXT NOT NULL,
            PRIMARY KEY (
                opportunity_id,
                requirement_id,
                evidence_id
            ),
            FOREIGN KEY (
                opportunity_id,
                requirement_id
            ) REFERENCES requirement_mappings(
                opportunity_id,
                requirement_id
            ) ON DELETE CASCADE,
            FOREIGN KEY (evidence_id)
                REFERENCES candidate_evidence(evidence_id)
                ON DELETE RESTRICT
        )
        """
    )
    connection.execute(
        """
        INSERT INTO evidence_matches_new (
            opportunity_id,
            requirement_id,
            evidence_id,
            relationship,
            reason
        )
        SELECT
            opportunity_id,
            requirement_id,
            evidence_id,
            relationship,
            reason
        FROM evidence_matches
        """
    )
    connection.execute("DROP TABLE evidence_matches")
    connection.execute(
        "ALTER TABLE evidence_matches_new RENAME TO evidence_matches"
    )


def initialize_database(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    """
    Initialize and migrate durable local product state.

    Key persistence rules:
    - completed opportunity analysis is historical snapshot data;
    - human decision is independently mutable;
    - old resume evidence is retained for historical hydration;
    - future matching uses only active candidate sources;
    - supporting materials accumulate;
    - setup/preferences are durable local singleton state.
    """

    connection = get_connection(db_path)

    try:
        with connection:
            reset_occurred = (
                _reset_pre_posting_url_opportunity_schema_if_needed(
                    connection
                )
            )

            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS candidate_sources (
                    source_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    source_type TEXT NOT NULL
                        CHECK (source_type IN ('RESUME', 'SUPPORTING')),
                    is_active INTEGER NOT NULL DEFAULT 1
                        CHECK (is_active IN (0, 1)),
                    stored_path TEXT,
                    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE UNIQUE INDEX IF NOT EXISTS
                    one_active_resume_source
                ON candidate_sources(source_type)
                WHERE source_type = 'RESUME' AND is_active = 1;

                CREATE TABLE IF NOT EXISTS candidate_evidence (
                    evidence_id TEXT PRIMARY KEY,
                    claim TEXT NOT NULL,
                    source_document TEXT NOT NULL,
                    source_section TEXT,
                    source_text TEXT NOT NULL,
                    evidence_type TEXT NOT NULL,
                    grounding_status TEXT NOT NULL,
                    source_id TEXT,
                    FOREIGN KEY (source_id)
                        REFERENCES candidate_sources(source_id)
                        ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS app_state (
                    singleton_id INTEGER PRIMARY KEY
                        CHECK (singleton_id = 1),
                    setup_completed INTEGER NOT NULL DEFAULT 0
                        CHECK (setup_completed IN (0, 1))
                );

                INSERT OR IGNORE INTO app_state (
                    singleton_id,
                    setup_completed
                ) VALUES (1, 0);

                CREATE TABLE IF NOT EXISTS candidate_preferences (
                    singleton_id INTEGER PRIMARY KEY
                        CHECK (singleton_id = 1),
                    preferred_locations_json TEXT NOT NULL DEFAULT '[]',
                    accepted_work_modes_json TEXT NOT NULL DEFAULT '[]',
                    accepted_employment_types_json TEXT NOT NULL DEFAULT '[]',
                    preferred_industries_json TEXT NOT NULL DEFAULT '[]',
                    preferred_company_sizes_json TEXT NOT NULL DEFAULT '[]',
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS processed_emails (
                    account_key TEXT NOT NULL,
                    message_id TEXT NOT NULL,
                    processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (account_key, message_id)
                );

                CREATE TABLE IF NOT EXISTS job_opportunities (
                    opportunity_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    source TEXT NOT NULL,
                    location TEXT,
                    source_url TEXT,
                    source_message_id TEXT,
                    source_item_id TEXT,
                    posting_url TEXT NOT NULL UNIQUE,
                    jd_text TEXT NOT NULL,
                    verification_level TEXT NOT NULL,
                    requirement_fit_score REAL NOT NULL,
                    pursuit_priority TEXT NOT NULL,
                    preference_results_json TEXT NOT NULL DEFAULT '{}',
                    strong_matches_json TEXT NOT NULL DEFAULT '[]',
                    main_gaps_json TEXT NOT NULL DEFAULT '[]',
                    job_attributes_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    user_decision TEXT
                );

                CREATE TABLE IF NOT EXISTS job_requirements (
                    opportunity_id TEXT NOT NULL,
                    requirement_id TEXT NOT NULL,
                    requirement TEXT NOT NULL,
                    category TEXT NOT NULL,
                    requirement_level TEXT NOT NULL,
                    jd_source_text TEXT NOT NULL,
                    jd_section TEXT,
                    grounding_status TEXT NOT NULL,
                    PRIMARY KEY (
                        opportunity_id,
                        requirement_id
                    ),
                    FOREIGN KEY (opportunity_id)
                        REFERENCES job_opportunities(opportunity_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS requirement_mappings (
                    opportunity_id TEXT NOT NULL,
                    requirement_id TEXT NOT NULL,
                    support_level TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    PRIMARY KEY (
                        opportunity_id,
                        requirement_id
                    ),
                    FOREIGN KEY (
                        opportunity_id,
                        requirement_id
                    ) REFERENCES job_requirements(
                        opportunity_id,
                        requirement_id
                    ) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS evidence_matches (
                    opportunity_id TEXT NOT NULL,
                    requirement_id TEXT NOT NULL,
                    evidence_id TEXT NOT NULL,
                    relationship TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    PRIMARY KEY (
                        opportunity_id,
                        requirement_id,
                        evidence_id
                    ),
                    FOREIGN KEY (
                        opportunity_id,
                        requirement_id
                    ) REFERENCES requirement_mappings(
                        opportunity_id,
                        requirement_id
                    ) ON DELETE CASCADE,
                    FOREIGN KEY (evidence_id)
                        REFERENCES candidate_evidence(evidence_id)
                        ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS job_resolution_attempts (
                    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_message_id TEXT,
                    source TEXT NOT NULL,
                    source_item_id TEXT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    source_url TEXT,
                    execution_status TEXT NOT NULL,
                    verification_result TEXT,
                    verification_level TEXT,
                    resolution_reason TEXT,
                    resolution_error TEXT,
                    resolved_posting_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # In-place additions for the schema in the uploaded source of truth.
            _ensure_column(
                connection,
                "candidate_evidence",
                "source_id",
                "TEXT REFERENCES candidate_sources(source_id) ON DELETE RESTRICT",
            )
            _ensure_column(
                connection,
                "job_opportunities",
                "job_attributes_json",
                "TEXT NOT NULL DEFAULT '{}'",
            )
            if "created_at" not in _table_columns(connection, "job_opportunities"):
                # SQLite cannot ADD COLUMN with CURRENT_TIMESTAMP as a
                # non-constant default. Existing rows get a one-time migration
                # timestamp; newly created schemas keep the NOT NULL default.
                connection.execute(
                    "ALTER TABLE job_opportunities ADD COLUMN created_at TEXT"
                )
                connection.execute(
                    "UPDATE job_opportunities SET created_at = CURRENT_TIMESTAMP "
                    "WHERE created_at IS NULL"
                )

            _ensure_processed_email_account_scope(connection)
            _ensure_evidence_match_delete_guard(connection)

        if reset_occurred:
            print(
                "Legacy pre-posting_url opportunity schema detected. "
                "Opportunity-side prototype data and processed-email markers "
                "were reset; candidate evidence was preserved."
            )

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at: {DEFAULT_DB_PATH}")
