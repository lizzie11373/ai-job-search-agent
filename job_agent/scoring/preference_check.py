from job_agent.models.preference import (
    CandidatePreferenceProfile,
    JobAttributeProfile,
    PreferenceCheckResult,
)


def normalize_value(
    value: str | None,
) -> str | None:
    """
    Lightweight normalization only.

    This function does NOT perform semantic inference.

    Example:
        "Hybrid"      -> "HYBRID"
        " full-time " -> "FULL-TIME"

    More complex normalization such as:
        "San Francisco" -> "Bay Area"

    should happen upstream using deterministic metadata
    normalization, not through LLM reasoning here.
    """

    if value is None:
        return None

    normalized = value.strip().upper()

    if not normalized:
        return None

    return normalized


def normalize_set(
    values: set[str],
) -> set[str]:
    """
    Normalize all configured preference values.
    """

    normalized_values = set()

    for value in values:

        normalized = normalize_value(
            value
        )

        if normalized is not None:
            normalized_values.add(
                normalized
            )

    return normalized_values


def check_set_preference(
    accepted_values: set[str],
    job_value: str | None,
) -> PreferenceCheckResult | None:
    """
    Compare one categorical job attribute against
    a user's accepted values.

    Returns:

        PreferenceCheckResult.MATCH
        PreferenceCheckResult.MISMATCH
        PreferenceCheckResult.UNKNOWN
        None

    None means:
        The user did not configure a preference for this
        category, so the category should be skipped entirely.

    Multiple accepted values use OR semantics.
    """

    normalized_preferences = normalize_set(
        accepted_values
    )

    # =========================================================
    # NO USER PREFERENCE
    # =========================================================
    #
    # Empty preference set means this category is flexible.
    #
    # It is not MATCH.
    # It is not UNKNOWN.
    #
    # The category is simply excluded from preference
    # evaluation.
    # =========================================================

    if not normalized_preferences:
        return None

    normalized_job_value = normalize_value(
        job_value
    )

    # =========================================================
    # JOB METADATA UNAVAILABLE
    # =========================================================

    if normalized_job_value is None:
        return PreferenceCheckResult.UNKNOWN

    # =========================================================
    # OR SEMANTICS
    # =========================================================
    #
    # If the job matches ANY of the user's accepted values,
    # this category is considered a MATCH.
    # =========================================================

    if (
        normalized_job_value
        in normalized_preferences
    ):
        return PreferenceCheckResult.MATCH

    return PreferenceCheckResult.MISMATCH


def check_compensation_preference(
    minimum_compensation: int | None,
    job_compensation_min: int | None,
    job_compensation_max: int | None,
) -> PreferenceCheckResult | None:
    """
    Evaluate optional minimum compensation preference.

    Returns:

        PreferenceCheckResult.MATCH
        PreferenceCheckResult.MISMATCH
        PreferenceCheckResult.UNKNOWN
        None

    None:
        Candidate did not configure a compensation preference.

    UNKNOWN:
        The job does not provide enough compensation
        information to make a deterministic decision.

    MATCH:
        The published compensation range includes compensation
        at or above the candidate's minimum.

    MISMATCH:
        The published maximum compensation is below the
        candidate's minimum.

    IMPORTANT:
    This is a posting-level preference check.

    It does NOT predict the candidate's actual offer.
    """

    # =========================================================
    # NO CANDIDATE COMPENSATION PREFERENCE
    # =========================================================

    if minimum_compensation is None:
        return None

    # =========================================================
    # NO USABLE COMPENSATION METADATA
    # =========================================================

    if (
        job_compensation_min is None
        and job_compensation_max is None
    ):
        return PreferenceCheckResult.UNKNOWN

    # =========================================================
    # CLEAR MISMATCH
    # =========================================================
    #
    # Even the highest published compensation is below
    # the candidate's minimum.
    #
    # Example:
    #
    # Candidate minimum = 150k
    # Job range         = 120k–140k
    #
    # Result:
    # MISMATCH
    # =========================================================

    if (
        job_compensation_max is not None
        and job_compensation_max
        < minimum_compensation
    ):
        return PreferenceCheckResult.MISMATCH

    # =========================================================
    # PUBLISHED RANGE REACHES CANDIDATE MINIMUM
    # =========================================================
    #
    # Example:
    #
    # Candidate minimum = 150k
    # Job range         = 140k–180k
    #
    # There is compensation within the published range
    # that satisfies the user's stated minimum.
    # =========================================================

    if (
        job_compensation_max is not None
        and job_compensation_max
        >= minimum_compensation
    ):
        return PreferenceCheckResult.MATCH

    # =========================================================
    # ONLY JOB MINIMUM IS AVAILABLE
    # =========================================================
    #
    # If the published minimum already meets the candidate's
    # minimum, we can confidently return MATCH.
    # =========================================================

    if (
        job_compensation_min is not None
        and job_compensation_min
        >= minimum_compensation
    ):
        return PreferenceCheckResult.MATCH

    # =========================================================
    # INSUFFICIENT INFORMATION
    # =========================================================
    #
    # Example:
    #
    # Candidate minimum = 150k
    # Job minimum       = 130k
    # Job maximum       = unknown
    #
    # We cannot safely infer MISMATCH because the actual
    # published range may still extend above 150k.
    # =========================================================

    return PreferenceCheckResult.UNKNOWN


def check_preferences(
    candidate_preferences: CandidatePreferenceProfile,
    job_attributes: JobAttributeProfile,
) -> dict[str, PreferenceCheckResult]:
    """
    Run the complete lightweight preference safety check.

    Only categories explicitly configured by the user
    are included in the result.

    Preference results do NOT modify Requirement Fit.

    Policy:

        MATCH
            Neutral.
            No priority change.
            No user warning required.

        UNKNOWN
            Neutral.
            No priority change.
            User may be informed that information
            was unavailable.

        MISMATCH
            Does not change Requirement Fit.
            May later trigger a bounded Pursuit Priority
            downgrade.

    This function does NOT calculate a score.
    """

    results: dict[
        str,
        PreferenceCheckResult,
    ] = {}

    # =========================================================
    # LOCATION
    # =========================================================

    location_result = check_set_preference(
        accepted_values=(
            candidate_preferences
            .preferred_locations
        ),
        job_value=(
            job_attributes.location
        ),
    )

    if location_result is not None:
        results["location"] = (
            location_result
        )

    # =========================================================
    # WORK MODE
    # =========================================================

    work_mode_result = check_set_preference(
        accepted_values=(
            candidate_preferences
            .accepted_work_modes
        ),
        job_value=(
            job_attributes.work_mode
        ),
    )

    if work_mode_result is not None:
        results["work_mode"] = (
            work_mode_result
        )

    # =========================================================
    # EMPLOYMENT TYPE
    # =========================================================

    employment_type_result = (
        check_set_preference(
            accepted_values=(
                candidate_preferences
                .accepted_employment_types
            ),
            job_value=(
                job_attributes
                .employment_type
            ),
        )
    )

    if employment_type_result is not None:
        results[
            "employment_type"
        ] = employment_type_result

    # =========================================================
    # COMPENSATION
    # =========================================================
    # V1 product scope intentionally excludes compensation preferences.
    # The legacy domain helper remains in this module for compatibility,
    # but check_preferences() does not evaluate or return compensation.

    # =========================================================
    # INDUSTRY
    # =========================================================
    #
    # Industry is checked ONLY when:
    #
    # 1. the user configured an industry preference, and
    # 2. industry metadata is directly available.
    #
    # If metadata is unavailable:
    #
    #     UNKNOWN
    #
    # We do NOT ask an LLM to infer the company's industry.
    # =========================================================

    industry_result = check_set_preference(
        accepted_values=(
            candidate_preferences
            .preferred_industries
        ),
        job_value=(
            job_attributes.industry
        ),
    )

    if industry_result is not None:
        results["industry"] = (
            industry_result
        )

    # =========================================================
    # COMPANY SIZE
    # =========================================================
    #
    # Same principle as industry:
    #
    # Direct structured metadata only.
    # No semantic company research.
    # =========================================================

    company_size_result = (
        check_set_preference(
            accepted_values=(
                candidate_preferences
                .preferred_company_sizes
            ),
            job_value=(
                job_attributes.company_size
            ),
        )
    )

    if company_size_result is not None:
        results[
            "company_size"
        ] = company_size_result

    return results