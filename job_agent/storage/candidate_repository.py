from __future__ import annotations

from enum import Enum
from pathlib import Path
from uuid import uuid4

from job_agent.models.candidate import (
    CandidateEvidenceBase,
    CandidateSource,
    CandidateSourceType,
    EvidenceUnit,
)
from job_agent.storage.database import DEFAULT_DB_PATH, get_connection


def _to_db_value(value):
    if isinstance(value, Enum):
        return value.value
    return value


def _row_to_evidence(row) -> EvidenceUnit:
    return EvidenceUnit(
        evidence_id=row["evidence_id"],
        claim=row["claim"],
        source_document=row["source_document"],
        source_section=row["source_section"],
        source_text=row["source_text"],
        evidence_type=row["evidence_type"],
        grounding_status=row["grounding_status"],
    )


def _row_to_source(row) -> CandidateSource:
    return CandidateSource(
        source_id=row["source_id"],
        filename=row["filename"],
        source_type=CandidateSourceType(row["source_type"]),
        is_active=bool(row["is_active"]),
        stored_path=row["stored_path"],
        uploaded_at=row["uploaded_at"],
    )


def build_candidate_source_id() -> str:
    return f"src_{uuid4().hex}"


def get_next_evidence_number(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> int:
    """Return the next durable E### number across active and inactive rows."""

    connection = get_connection(db_path)
    try:
        rows = connection.execute(
            "SELECT evidence_id FROM candidate_evidence"
        ).fetchall()
    finally:
        connection.close()

    highest = 0
    for row in rows:
        evidence_id = row["evidence_id"]
        if (
            isinstance(evidence_id, str)
            and evidence_id.startswith("E")
            and evidence_id[1:].isdigit()
        ):
            highest = max(highest, int(evidence_id[1:]))
    return highest + 1


def save_candidate_evidence_base(
    evidence_base: CandidateEvidenceBase,
    db_path: str | Path = DEFAULT_DB_PATH,
    *,
    source_id: str | None = None,
) -> None:
    """
    Persist evidence rows.

    This compatibility function remains for tests/legacy local scripts. New
    upload flows should create a CandidateSource and insert evidence through
    append_source_with_evidence() or replace_resume_source().
    """

    connection = get_connection(db_path)
    try:
        with connection:
            for evidence in evidence_base.evidence_units:
                connection.execute(
                    """
                    INSERT INTO candidate_evidence (
                        evidence_id,
                        claim,
                        source_document,
                        source_section,
                        source_text,
                        evidence_type,
                        grounding_status,
                        source_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(evidence_id)
                    DO UPDATE SET
                        claim = excluded.claim,
                        source_document = excluded.source_document,
                        source_section = excluded.source_section,
                        source_text = excluded.source_text,
                        evidence_type = excluded.evidence_type,
                        grounding_status = excluded.grounding_status,
                        source_id = COALESCE(
                            excluded.source_id,
                            candidate_evidence.source_id
                        )
                    """,
                    (
                        evidence.evidence_id,
                        evidence.claim,
                        evidence.source_document,
                        evidence.source_section,
                        evidence.source_text,
                        _to_db_value(evidence.evidence_type),
                        _to_db_value(evidence.grounding_status),
                        source_id,
                    ),
                )
    finally:
        connection.close()


def load_candidate_evidence_base(
    db_path: str | Path = DEFAULT_DB_PATH,
    *,
    active_only: bool = True,
) -> CandidateEvidenceBase:
    """
    Load candidate evidence.

    Future matching uses active_only=True. Legacy rows from the uploaded repo
    may have no source_id. They remain active only until the first managed
    Resume exists. After that, future matching uses the active Resume plus
    active Supporting sources, while legacy source-less evidence remains stored
    solely so historical analyses can still hydrate it.
    """

    connection = get_connection(db_path)
    try:
        if active_only:
            rows = connection.execute(
                """
                SELECT ce.*
                FROM candidate_evidence AS ce
                LEFT JOIN candidate_sources AS cs
                    ON cs.source_id = ce.source_id
                WHERE cs.is_active = 1
                   OR (
                        ce.source_id IS NULL
                        AND NOT EXISTS (
                            SELECT 1
                            FROM candidate_sources AS active_resume
                            WHERE active_resume.source_type = 'RESUME'
                              AND active_resume.is_active = 1
                        )
                   )
                ORDER BY ce.evidence_id
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM candidate_evidence
                ORDER BY evidence_id
                """
            ).fetchall()
    finally:
        connection.close()

    return CandidateEvidenceBase(
        evidence_units=[_row_to_evidence(row) for row in rows]
    )


def load_all_candidate_evidence(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> CandidateEvidenceBase:
    return load_candidate_evidence_base(
        db_path=db_path,
        active_only=False,
    )


def load_evidence_by_id(
    evidence_id: str,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> EvidenceUnit | None:
    """Historical lookup deliberately ignores source activeness."""

    connection = get_connection(db_path)
    try:
        row = connection.execute(
            """
            SELECT *
            FROM candidate_evidence
            WHERE evidence_id = ?
            """,
            (evidence_id,),
        ).fetchone()
    finally:
        connection.close()

    return None if row is None else _row_to_evidence(row)


def list_candidate_sources(
    db_path: str | Path = DEFAULT_DB_PATH,
    *,
    active_only: bool = False,
) -> list[CandidateSource]:
    connection = get_connection(db_path)
    try:
        sql = "SELECT * FROM candidate_sources"
        params: tuple = ()
        if active_only:
            sql += " WHERE is_active = 1"
        sql += " ORDER BY uploaded_at, source_id"
        rows = connection.execute(sql, params).fetchall()
    finally:
        connection.close()
    return [_row_to_source(row) for row in rows]


def get_active_resume_source(
    db_path: str | Path = DEFAULT_DB_PATH,
) -> CandidateSource | None:
    connection = get_connection(db_path)
    try:
        row = connection.execute(
            """
            SELECT *
            FROM candidate_sources
            WHERE source_type = 'RESUME'
              AND is_active = 1
            ORDER BY uploaded_at DESC, source_id DESC
            LIMIT 1
            """
        ).fetchone()
    finally:
        connection.close()
    return None if row is None else _row_to_source(row)


def append_source_with_evidence(
    *,
    source_id: str,
    filename: str,
    source_type: CandidateSourceType,
    stored_path: str | None,
    evidence_units: list[EvidenceUnit],
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    """
    Insert one new candidate source and its evidence atomically.

    This is used for SUPPORTING materials. RESUME replacement should use the
    dedicated replacement function so the old active resume remains safe until
    the new source/evidence is ready to commit.
    """

    if source_type == CandidateSourceType.RESUME:
        raise ValueError(
            "Use replace_resume_source() for RESUME sources."
        )

    connection = get_connection(db_path)
    try:
        with connection:
            connection.execute(
                """
                INSERT INTO candidate_sources (
                    source_id,
                    filename,
                    source_type,
                    is_active,
                    stored_path
                ) VALUES (?, ?, ?, 1, ?)
                """,
                (
                    source_id,
                    filename,
                    source_type.value,
                    stored_path,
                ),
            )
            _insert_evidence_rows(
                connection,
                source_id=source_id,
                evidence_units=evidence_units,
            )
    finally:
        connection.close()


def replace_resume_source(
    *,
    source_id: str,
    filename: str,
    stored_path: str | None,
    evidence_units: list[EvidenceUnit],
    db_path: str | Path = DEFAULT_DB_PATH,
) -> None:
    """
    Atomically switch the active resume after new evidence is ready.

    Callers must finish file decoding, evidence extraction and validation
    before entering this function. If any DB write fails the transaction rolls
    back and the prior resume remains active.
    """

    connection = get_connection(db_path)
    try:
        with connection:
            connection.execute(
                """
                UPDATE candidate_sources
                SET is_active = 0
                WHERE source_type = 'RESUME'
                  AND is_active = 1
                """
            )
            connection.execute(
                """
                INSERT INTO candidate_sources (
                    source_id,
                    filename,
                    source_type,
                    is_active,
                    stored_path
                ) VALUES (?, ?, 'RESUME', 1, ?)
                """,
                (source_id, filename, stored_path),
            )
            _insert_evidence_rows(
                connection,
                source_id=source_id,
                evidence_units=evidence_units,
            )
    finally:
        connection.close()


def _insert_evidence_rows(
    connection,
    *,
    source_id: str,
    evidence_units: list[EvidenceUnit],
) -> None:
    for evidence in evidence_units:
        connection.execute(
            """
            INSERT INTO candidate_evidence (
                evidence_id,
                claim,
                source_document,
                source_section,
                source_text,
                evidence_type,
                grounding_status,
                source_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence.evidence_id,
                evidence.claim,
                evidence.source_document,
                evidence.source_section,
                evidence.source_text,
                _to_db_value(evidence.evidence_type),
                _to_db_value(evidence.grounding_status),
                source_id,
            ),
        )
