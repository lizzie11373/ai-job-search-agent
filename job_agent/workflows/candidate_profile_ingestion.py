from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from job_agent.agents.evidence_extractor import extract_evidence_from_document
from job_agent.agents.evidence_validator import validate_evidence
from job_agent.ingestion.candidate_source_upload import (
    DEFAULT_CANDIDATE_SOURCE_DIR,
    save_uploaded_candidate_markdown,
)
from job_agent.models.candidate import (
    CandidateSourceType,
    EvidenceUnit,
)
from job_agent.storage.candidate_repository import (
    append_source_with_evidence,
    build_candidate_source_id,
    get_next_evidence_number,
    load_candidate_evidence_base,
    replace_resume_source,
)
from job_agent.storage.database import DEFAULT_DB_PATH


@dataclass(frozen=True)
class CandidateDocumentIngestionResult:
    document_name: str
    source_id: str
    source_type: CandidateSourceType
    extracted_count: int
    validated_count: int
    added_evidence_ids: tuple[str, ...]
    total_active_evidence_count: int
    saved_path: Path | None = None

    @property
    def total_evidence_count(self) -> int:
        """Backward-compatible alias used by older local scripts/tests."""
        return self.total_active_evidence_count


def _grounding_status_value(value) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _copy_with_durable_id(
    evidence: EvidenceUnit,
    evidence_id: str,
    *,
    source_document: str,
) -> EvidenceUnit:
    return EvidenceUnit(
        evidence_id=evidence_id,
        claim=evidence.claim,
        source_document=source_document,
        source_section=evidence.source_section,
        source_text=evidence.source_text,
        evidence_type=evidence.evidence_type,
        grounding_status=evidence.grounding_status,
    )


def _extract_validated_evidence(
    *,
    document_name: str,
    document_text: str,
    db_path: str | Path,
) -> tuple[list[EvidenceUnit], int]:
    extracted_evidence = extract_evidence_from_document(
        document_name=document_name,
        document_text=document_text,
    )
    validated_results = validate_evidence(
        extracted_evidence,
        document_text,
    )
    validated = [
        evidence
        for evidence in validated_results
        if _grounding_status_value(evidence.grounding_status) == "VALIDATED"
    ]

    if not validated:
        raise ValueError(
            "Candidate source produced no validated evidence. "
            "The current background has not been changed."
        )

    next_number = get_next_evidence_number(db_path=db_path)
    durable = [
        _copy_with_durable_id(
            evidence,
            f"E{next_number + offset:03d}",
            source_document=document_name,
        )
        for offset, evidence in enumerate(validated)
    ]
    return durable, len(extracted_evidence)


def _ingest_candidate_document(
    *,
    document_name: str,
    document_text: str,
    source_type: CandidateSourceType,
    source_id: str,
    stored_path: str | None,
    db_path: str | Path,
) -> CandidateDocumentIngestionResult:
    document_name = document_name.strip()
    if not document_name:
        raise ValueError("Candidate document name cannot be empty.")
    if not document_text.strip():
        raise ValueError("Candidate document text cannot be empty.")

    durable_evidence, extracted_count = _extract_validated_evidence(
        document_name=document_name,
        document_text=document_text,
        db_path=db_path,
    )

    if source_type == CandidateSourceType.RESUME:
        replace_resume_source(
            source_id=source_id,
            filename=document_name,
            stored_path=stored_path,
            evidence_units=durable_evidence,
            db_path=db_path,
        )
    else:
        append_source_with_evidence(
            source_id=source_id,
            filename=document_name,
            source_type=source_type,
            stored_path=stored_path,
            evidence_units=durable_evidence,
            db_path=db_path,
        )

    active_base = load_candidate_evidence_base(
        db_path=db_path,
        active_only=True,
    )

    return CandidateDocumentIngestionResult(
        document_name=document_name,
        source_id=source_id,
        source_type=source_type,
        extracted_count=extracted_count,
        validated_count=len(durable_evidence),
        added_evidence_ids=tuple(
            evidence.evidence_id for evidence in durable_evidence
        ),
        total_active_evidence_count=len(active_base.evidence_units),
    )


def ingest_candidate_document(
    *,
    document_name: str,
    document_text: str,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> CandidateDocumentIngestionResult:
    """Backward-compatible in-memory SUPPORTING-material ingestion."""

    source_id = build_candidate_source_id()
    return _ingest_candidate_document(
        document_name=document_name,
        document_text=document_text,
        source_type=CandidateSourceType.SUPPORTING,
        source_id=source_id,
        stored_path=None,
        db_path=db_path,
    )


def _ingest_uploaded_markdown(
    *,
    filename: str,
    content: bytes,
    source_type: CandidateSourceType,
    source_dir: str | Path,
    db_path: str | Path,
) -> CandidateDocumentIngestionResult:
    """
    Save/process one upload without exposing a half-completed replacement.

    The new file is written under a source-id-prefixed storage name first.
    Extraction/validation happens while the old resume is still active. Only
    after that succeeds does the DB transaction switch the active resume (or
    append the supporting source). Any failure removes the newly written file.
    """

    source_id = build_candidate_source_id()
    original_name = Path(filename).name.strip()
    storage_name = f"{source_id}__{original_name}"

    document = save_uploaded_candidate_markdown(
        filename=storage_name,
        content=content,
        source_dir=source_dir,
        overwrite=False,
    )

    try:
        result = _ingest_candidate_document(
            document_name=original_name,
            document_text=document.document_text,
            source_type=source_type,
            source_id=source_id,
            stored_path=str(document.saved_path),
            db_path=db_path,
        )
    except Exception:
        document.saved_path.unlink(missing_ok=True)
        raise

    return replace(result, saved_path=document.saved_path)


def ingest_uploaded_resume_markdown(
    *,
    filename: str,
    content: bytes,
    source_dir: str | Path = DEFAULT_CANDIDATE_SOURCE_DIR,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> CandidateDocumentIngestionResult:
    """First resume upload and later Resume Replace use the same safe path."""

    return _ingest_uploaded_markdown(
        filename=filename,
        content=content,
        source_type=CandidateSourceType.RESUME,
        source_dir=source_dir,
        db_path=db_path,
    )


def ingest_uploaded_supporting_markdown(
    *,
    filename: str,
    content: bytes,
    source_dir: str | Path = DEFAULT_CANDIDATE_SOURCE_DIR,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> CandidateDocumentIngestionResult:
    """Append one supporting material; existing support remains active."""

    return _ingest_uploaded_markdown(
        filename=filename,
        content=content,
        source_type=CandidateSourceType.SUPPORTING,
        source_dir=source_dir,
        db_path=db_path,
    )


def ingest_uploaded_candidate_markdown(
    *,
    filename: str,
    content: bytes,
    source_dir: str | Path = DEFAULT_CANDIDATE_SOURCE_DIR,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> CandidateDocumentIngestionResult:
    """Compatibility alias: generic additional documents are SUPPORTING."""

    return ingest_uploaded_supporting_markdown(
        filename=filename,
        content=content,
        source_dir=source_dir,
        db_path=db_path,
    )
