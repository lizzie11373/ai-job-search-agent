from job_agent.models.opportunity import PursuitPriority, UserDecision
from job_agent.ui.presenters import (
    decision_label,
    preference_label,
    priority_label,
    split_csv_values,
    support_label,
)


def test_priority_labels_are_user_facing():
    assert priority_label(PursuitPriority.TOP_PRIORITY) == "Top Priority"
    assert priority_label(PursuitPriority.WORTH_CONSIDERING) == "Worth Considering"


def test_decision_labels_match_review_filters():
    assert decision_label(UserDecision.PURSUE_NOW) == "Pursuing"
    assert decision_label(UserDecision.SAVE_FOR_LATER) == "Saved"
    assert decision_label(UserDecision.PASS) == "Passed"


def test_support_labels_hide_internal_taxonomy():
    assert support_label("STRONG") == "Strong Support"
    assert support_label("WEAK") == "Partial Support"
    assert support_label("NOT_CLEARLY_SUPPORTED") == "Not Clearly Supported"


def test_preference_label_keeps_zero_denominator_visible():
    assert preference_label(0, 0) == "0 / 0 matched"
    assert preference_label(3, 5) == "3 / 5 matched"


def test_csv_preferences_ignore_blank_values():
    assert split_csv_values("Remote, San Francisco, ,") == {
        "Remote",
        "San Francisco",
    }
