from job_agent.models.job import (
    JobRequirement,
)

from job_agent.models.evaluation import (
    RequirementEvidenceMapping,
    RequirementFitBreakdown,
    RequirementFitResult,
)


SUPPORT_SCORES = {
    "STRONG": 1.00,
    "PARTIAL": 0.65,
    "WEAK": 0.30,
    "NOT_CLEARLY_SUPPORTED": 0.00,
}


REQUIREMENT_LEVEL_WEIGHTS = {
    "CORE": 1.30,
    "REQUIRED": 1.10,
    "PREFERRED": 0.70,
}


def calculate_requirement_fit(
    requirements: list[JobRequirement],
    finalized_mappings: list[RequirementEvidenceMapping],
) -> RequirementFitResult:

    # =========================================================
    # 1. USE ONLY VALIDATED REQUIREMENTS
    # =========================================================

    validated_requirements = [
        requirement
        for requirement in requirements
        if requirement.grounding_status
        == "VALIDATED"
    ]

    if not validated_requirements:
        raise ValueError(
            "No validated requirements "
            "available for scoring."
        )

    # =========================================================
    # 2. BUILD LOOKUP TABLES
    # =========================================================

    requirement_by_id = {
        requirement.requirement_id: requirement
        for requirement in validated_requirements
    }

    mapping_by_id = {
        mapping.requirement_id: mapping
        for mapping in finalized_mappings
    }

    # =========================================================
    # 3. REQUIREMENT COVERAGE CHECK
    # =========================================================
    #
    # Every validated requirement must have exactly one
    # finalized mapping before scoring can happen.
    #
    # We do not allow scoring on incomplete matching results.
    # =========================================================

    expected_requirement_ids = set(
        requirement_by_id.keys()
    )

    actual_requirement_ids = set(
        mapping_by_id.keys()
    )

    missing_requirement_ids = (
        expected_requirement_ids
        - actual_requirement_ids
    )

    extra_requirement_ids = (
        actual_requirement_ids
        - expected_requirement_ids
    )

    if missing_requirement_ids:
        raise ValueError(
            "Missing finalized mappings for "
            f"requirements: "
            f"{sorted(missing_requirement_ids)}"
        )

    if extra_requirement_ids:
        raise ValueError(
            "Unexpected finalized mappings for "
            f"requirements: "
            f"{sorted(extra_requirement_ids)}"
        )

    # =========================================================
    # 4. SCORE EACH REQUIREMENT
    # =========================================================

    breakdown = []

    total_weight = 0.0
    total_weighted_score = 0.0

    strong_count = 0
    partial_count = 0
    weak_count = 0
    unsupported_count = 0

    for requirement in validated_requirements:

        mapping = mapping_by_id[
            requirement.requirement_id
        ]

        support_level = (
            mapping.support_level
        )

        requirement_level = (
            requirement.requirement_level
        )

        # -----------------------------------------------------
        # SUPPORT LEVEL VALIDATION
        # -----------------------------------------------------

        if (
            support_level
            not in SUPPORT_SCORES
        ):
            raise ValueError(
                "Unknown support level: "
                f"{support_level}"
            )

        # -----------------------------------------------------
        # REQUIREMENT LEVEL VALIDATION
        # -----------------------------------------------------

        if (
            requirement_level
            not in REQUIREMENT_LEVEL_WEIGHTS
        ):
            raise ValueError(
                "Unknown requirement level: "
                f"{requirement_level}"
            )

        # -----------------------------------------------------
        # NUMERIC VALUES
        # -----------------------------------------------------

        support_score = (
            SUPPORT_SCORES[
                support_level
            ]
        )

        weight = (
            REQUIREMENT_LEVEL_WEIGHTS[
                requirement_level
            ]
        )

        weighted_score = (
            support_score
            * weight
        )

        total_weight += weight

        total_weighted_score += (
            weighted_score
        )

        # -----------------------------------------------------
        # SUPPORT COUNTS
        # -----------------------------------------------------

        if support_level == "STRONG":
            strong_count += 1

        elif support_level == "PARTIAL":
            partial_count += 1

        elif support_level == "WEAK":
            weak_count += 1

        elif (
            support_level
            == "NOT_CLEARLY_SUPPORTED"
        ):
            unsupported_count += 1

        # -----------------------------------------------------
        # TRACEABLE BREAKDOWN
        # -----------------------------------------------------

        breakdown.append(
            RequirementFitBreakdown(
                requirement_id=(
                    requirement.requirement_id
                ),
                support_level=(
                    support_level
                ),
                support_score=(
                    support_score
                ),
                requirement_level=(
                    requirement_level
                ),
                weight=(
                    weight
                ),
                weighted_score=(
                    weighted_score
                ),
            )
        )

    # =========================================================
    # 5. FINAL REQUIREMENT FIT INDEX
    # =========================================================

    if total_weight == 0:
        raise ValueError(
            "Total requirement weight "
            "cannot be zero."
        )

    score = (
        total_weighted_score
        / total_weight
        * 100
    )

    score = round(
        score,
        1,
    )

    # =========================================================
    # 6. RETURN STRUCTURED RESULT
    # =========================================================

    return RequirementFitResult(
        score=score,
        breakdown=breakdown,
        strong_count=strong_count,
        partial_count=partial_count,
        weak_count=weak_count,
        unsupported_count=(
            unsupported_count
        ),
    )