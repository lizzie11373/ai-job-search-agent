from dataclasses import dataclass, field
from enum import StrEnum


class PreferenceCheckResult(StrEnum):
    """
    Result of evaluating one configured candidate preference
    against the corresponding job attribute.

    MATCH:
        The job satisfies the user's configured preference.

    MISMATCH:
        The job clearly conflicts with the user's configured
        preference.

    UNKNOWN:
        The user configured a preference, but the job does not
        provide enough structured metadata to determine whether
        it matches.

    None is NOT a PreferenceCheckResult.

    None means:
        The user did not configure a preference for that
        category, so the category is skipped entirely.
    """

    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"


@dataclass
class CandidatePreferenceProfile:
    """
    Explicit user preferences used as a lightweight
    safety check after Requirement Fit.

    Important:
    - Preferences are NOT scored.
    - Preferences are NOT ranked by importance.
    - Multiple values inside one category use OR semantics.
    - An empty set means the user has no preference
      for that category, so the category is skipped.
    """

    preferred_locations: set[str] = field(
        default_factory=set
    )

    accepted_work_modes: set[str] = field(
        default_factory=set
    )

    accepted_employment_types: set[str] = field(
        default_factory=set
    )

    # Legacy domain field retained for compatibility. V1 UI/persistence does
    # not expose compensation as a candidate preference.
    minimum_compensation: int | None = None

    preferred_industries: set[str] = field(
        default_factory=set
    )

    preferred_company_sizes: set[str] = field(
        default_factory=set
    )


@dataclass
class JobAttributeProfile:
    """
    Structured job attributes used for preference checks.

    These attributes should come from directly available
    job-posting or provider metadata whenever possible.

    Do NOT use LLM semantic inference merely to populate
    missing preference attributes.

    Missing information is represented as None.

    If the candidate configured a preference for a category
    but the corresponding job attribute is missing, the
    preference checker will return:

        PreferenceCheckResult.UNKNOWN
    """

    location: str | None = None

    work_mode: str | None = None

    employment_type: str | None = None

    compensation_min: int | None = None

    compensation_max: int | None = None

    industry: str | None = None

    company_size: str | None = None