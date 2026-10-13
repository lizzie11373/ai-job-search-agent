from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CandidateSourceType(StrEnum):
    RESUME = "RESUME"
    SUPPORTING = "SUPPORTING"


@dataclass(frozen=True)
class CandidateSource:
    source_id: str
    filename: str
    source_type: CandidateSourceType
    is_active: bool
    stored_path: str | None = None
    uploaded_at: str | None = None


@dataclass
class EvidenceUnit:
    evidence_id: str
    claim: str
    source_document: str
    source_section: str | None
    source_text: str
    evidence_type: str
    grounding_status: str


@dataclass
class CandidateEvidenceBase:
    evidence_units: list[EvidenceUnit]

    def get_evidence(self, evidence_id: str) -> EvidenceUnit | None:
        for evidence in self.evidence_units:
            if evidence.evidence_id == evidence_id:
                return evidence
        return None
