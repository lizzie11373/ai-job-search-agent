from job_agent.models.opportunity import (
    PursuitPriority,
)

from job_agent.models.preference import (
    PreferenceCheckResult,
)


PRIORITY_ORDER = [
    PursuitPriority.TOP_PRIORITY,
    PursuitPriority.STRONG_OPPORTUNITY,
    PursuitPriority.WORTH_CONSIDERING,
    PursuitPriority.DEPRIORITIZE,
]


# ============================================================
# PROTOTYPE THRESHOLDS
# ============================================================
#
# These thresholds are NOT scientific constants.
#
# They are initial product hypotheses for the prototype.
#
# In a production system, they should be calibrated against
# human-labeled job decisions across a representative set of
# real jobs.
# ============================================================

TOP_PRIORITY_THRESHOLD = 85.0
STRONG_OPPORTUNITY_THRESHOLD = 70.0
WORTH_CONSIDERING_THRESHOLD = 55.0


def get_base_priority(
    requirement_fit_score: float,
) -> PursuitPriority:
    """
    Convert Requirement Fit into a base Pursuit Priority.

    This happens BEFORE preference safety checks.

    Requirement Fit remains the only continuous numeric
    ranking signal.
    """

    if not 0 <= requirement_fit_score <= 100:
        raise ValueError(
            "Requirement Fit score must be "
            "between 0 and 100."
        )

    if (
        requirement_fit_score
        >= TOP_PRIORITY_THRESHOLD
    ):
        return PursuitPriority.TOP_PRIORITY

    if (
        requirement_fit_score
        >= STRONG_OPPORTUNITY_THRESHOLD
    ):
        return PursuitPriority.STRONG_OPPORTUNITY

    if (
        requirement_fit_score
        >= WORTH_CONSIDERING_THRESHOLD
    ):
        return PursuitPriority.WORTH_CONSIDERING

    return PursuitPriority.DEPRIORITIZE


def has_preference_mismatch(
    preference_results: dict[
        str,
        PreferenceCheckResult,
    ],
) -> bool:
    """
    Determine whether any configured preference
    clearly conflicts with the job.

    MATCH:
        Neutral.

    UNKNOWN:
        Neutral for priority.

    MISMATCH:
        Triggers the bounded preference policy.
    """

    return any(
        result
        == PreferenceCheckResult.MISMATCH
        for result in preference_results.values()
    )


def downgrade_priority_one_level(
    priority: PursuitPriority,
) -> PursuitPriority:
    """
    Apply a bounded one-level downgrade.

    Preference is a policy modifier,
    not a second scoring system.

    Multiple mismatches do NOT stack into multiple
    automatic downgrades.
    """

    if priority not in PRIORITY_ORDER:
        raise ValueError(
            f"Unknown priority: {priority}"
        )

    current_index = PRIORITY_ORDER.index(
        priority
    )

    # Already at the lowest priority.
    if current_index == len(
        PRIORITY_ORDER
    ) - 1:
        return priority

    return PRIORITY_ORDER[
        current_index + 1
    ]


def calculate_pursuit_priority(
    requirement_fit_score: float,
    preference_results: dict[
        str,
        PreferenceCheckResult,
    ],
) -> PursuitPriority:
    """
    Calculate final Pursuit Priority.

    Policy:

    1. Requirement Fit determines base priority.

    2. MATCH does not change priority.

    3. UNKNOWN does not change priority.

    4. No configured preference does not appear in
       preference_results.

    5. One or more MISMATCH results cause at most
       one priority-level downgrade.

    Requirement Fit itself is never modified.
    """

    base_priority = get_base_priority(
        requirement_fit_score
    )

    if not has_preference_mismatch(
        preference_results
    ):
        return base_priority

    return downgrade_priority_one_level(
        base_priority
    )