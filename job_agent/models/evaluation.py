from dataclasses import dataclass


@dataclass
class EvidenceMatch:
    evidence_id: str
    relationship: str
    reason: str


@dataclass
class RequirementEvidenceMapping:
    requirement_id: str
    evidence_matches: list[EvidenceMatch]
    support_level: str
    reason: str

    @property
    def evidence_ids(self) -> list[str]:
        return [
            match.evidence_id
            for match in self.evidence_matches
        ]


@dataclass
class NegativeConclusionVerification:
    requirement_id: str
    status: str
    counter_evidence_matches: list[EvidenceMatch]
    reason: str


@dataclass
class RequirementFitBreakdown:
    requirement_id: str
    support_level: str
    support_score: float
    requirement_level: str
    weight: float
    weighted_score: float


@dataclass
class RequirementFitResult:
    score: float
    breakdown: list[RequirementFitBreakdown]

    strong_count: int
    partial_count: int
    weak_count: int
    unsupported_count: int