from __future__ import annotations

from datetime import datetime, timezone

from job_agent.models.opportunity import PursuitPriority, UserDecision


_PRIORITY_LABELS = {
    PursuitPriority.TOP_PRIORITY: "Top Priority",
    PursuitPriority.STRONG_OPPORTUNITY: "Strong Opportunity",
    PursuitPriority.WORTH_CONSIDERING: "Worth Considering",
    PursuitPriority.DEPRIORITIZE: "Deprioritize",
}

_DECISION_LABELS = {
    UserDecision.PURSUE_NOW: "Pursuing",
    UserDecision.SAVE_FOR_LATER: "Saved",
    UserDecision.PASS: "Passed",
}

_SUPPORT_LABELS = {
    "STRONG": "Strong Support",
    "PARTIAL": "Partial Support",
    "WEAK": "Partial Support",
    "NOT_CLEARLY_SUPPORTED": "Not Clearly Supported",
}


def priority_label(priority: PursuitPriority | str) -> str:
    try:
        value = PursuitPriority(priority)
    except ValueError:
        return str(priority).replace("_", " ").title()
    return _PRIORITY_LABELS[value]


def priority_tone(priority: PursuitPriority | str) -> str:
    try:
        value = PursuitPriority(priority)
    except ValueError:
        return "neutral"
    if value in {PursuitPriority.TOP_PRIORITY, PursuitPriority.STRONG_OPPORTUNITY}:
        return "positive"
    if value == PursuitPriority.WORTH_CONSIDERING:
        return "caution"
    return "muted"


def decision_label(decision: UserDecision | str | None) -> str:
    if decision is None:
        return "Needs Review"
    try:
        value = UserDecision(decision)
    except ValueError:
        return str(decision).replace("_", " ").title()
    return _DECISION_LABELS[value]


def support_label(value: str) -> str:
    normalized = str(value).strip().upper()
    return _SUPPORT_LABELS.get(
        normalized,
        normalized.replace("_", " ").title(),
    )


def support_tone(value: str) -> str:
    normalized = str(value).strip().upper()
    if normalized == "STRONG":
        return "positive"
    if normalized in {"PARTIAL", "WEAK"}:
        return "caution"
    return "muted"


def preference_label(matched: int, configured: int) -> str:
    return f"{matched} / {configured} matched"


def split_csv_values(raw: str) -> set[str]:
    return {
        value.strip()
        for value in raw.split(",")
        if value.strip()
    }


def join_values(values: set[str]) -> str:
    return ", ".join(sorted(values))


def format_created_at(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return value
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    local = parsed.astimezone()
    return local.strftime("%b %-d, %Y")
