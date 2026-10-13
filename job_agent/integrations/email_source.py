from __future__ import annotations

import importlib
import os
from collections.abc import Callable, Iterable
from typing import Protocol

from job_agent.models.email import EmailMetadata, JobAlertEmail


ENV_EMAIL_LOADER = "JOB_AGENT_EMAIL_LOADER"


class EmailSource(Protocol):
    """Provider-neutral contract used by the Agent Run orchestration."""

    def account_key(self) -> str:
        """Return a stable key for the currently active mailbox/account."""

    def list_message_metadata(self) -> Iterable[EmailMetadata]:
        """Return lightweight message metadata for the discovery window."""

    def get_message(self, message_id: str) -> JobAlertEmail:
        """Fetch one full message only after metadata triage says it is relevant."""


def get_configured_email_loader() -> Callable[[], Iterable[JobAlertEmail]] | None:
    """
    Resolve the legacy optional local email loader from an environment variable.

    Format:
        JOB_AGENT_EMAIL_LOADER="my_package.gmail_adapter:load_job_alert_emails"

    This remains available for tests/custom local adapters. The product UI now
    uses the built-in GmailEmailSource instead.
    """

    spec = os.getenv(ENV_EMAIL_LOADER, "").strip()
    if not spec:
        return None

    module_name, separator, function_name = spec.partition(":")
    if not separator or not module_name.strip() or not function_name.strip():
        raise RuntimeError(
            f"{ENV_EMAIL_LOADER} must use 'module:function' format."
        )

    try:
        module = importlib.import_module(module_name.strip())
    except Exception as error:
        raise RuntimeError(
            f"Could not import configured email loader module '{module_name}'."
        ) from error

    loader = getattr(module, function_name.strip(), None)
    if loader is None or not callable(loader):
        raise RuntimeError(
            f"Configured email loader '{spec}' is not callable."
        )
    return loader
