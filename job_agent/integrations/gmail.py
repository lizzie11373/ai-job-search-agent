from __future__ import annotations

import base64
import os
import time
from collections.abc import Callable
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from job_agent.models.email import EmailLink, EmailMetadata, JobAlertEmail


GMAIL_SCOPES = ("https://www.googleapis.com/auth/gmail.readonly",)
DEFAULT_PRIVATE_DIR = Path("data/private")
DEFAULT_CREDENTIALS_PATH = DEFAULT_PRIVATE_DIR / "google_credentials.json"
DEFAULT_TOKEN_PATH = DEFAULT_PRIVATE_DIR / "gmail_token.json"
DEFAULT_LOOKBACK_HOURS = 1
DEFAULT_LOOKBACK_DAYS = 1  # Backward-compatible explicit day override.
DEFAULT_MAX_MESSAGES = 200

ENV_CREDENTIALS_PATH = "JOB_AGENT_GMAIL_CREDENTIALS_PATH"
ENV_TOKEN_PATH = "JOB_AGENT_GMAIL_TOKEN_PATH"
ENV_LOOKBACK_HOURS = "JOB_AGENT_GMAIL_LOOKBACK_HOURS"
ENV_LOOKBACK_DAYS = "JOB_AGENT_GMAIL_LOOKBACK_DAYS"
ENV_MAX_MESSAGES = "JOB_AGENT_GMAIL_MAX_MESSAGES"


class GmailIntegrationError(RuntimeError):
    """Base class for Gmail integration failures surfaced to the UI."""


class GmailConfigurationError(GmailIntegrationError):
    """The local app is missing OAuth client configuration or dependencies."""


class GmailAuthorizationRequiredError(GmailIntegrationError):
    """The user must connect or reconnect Gmail interactively."""


class GmailApiError(GmailIntegrationError):
    """A Gmail API request failed for a non-authorization reason."""


def _configured_path(env_name: str, default: Path) -> Path:
    raw = os.getenv(env_name, "").strip()
    return Path(raw).expanduser() if raw else default


def get_credentials_path() -> Path:
    return _configured_path(ENV_CREDENTIALS_PATH, DEFAULT_CREDENTIALS_PATH)


def get_token_path() -> Path:
    return _configured_path(ENV_TOKEN_PATH, DEFAULT_TOKEN_PATH)


def _positive_int_from_env(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as error:
        raise GmailConfigurationError(f"{name} must be an integer.") from error
    if value <= 0:
        raise GmailConfigurationError(f"{name} must be greater than zero.")
    return value


def _import_google_auth():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ModuleNotFoundError as error:
        raise GmailConfigurationError(
            "Google Gmail dependencies are not installed. Run "
            "'python -m pip install -r requirements.txt'."
        ) from error
    return Request, Credentials, InstalledAppFlow


def _import_google_api():
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except ModuleNotFoundError as error:
        raise GmailConfigurationError(
            "Google Gmail dependencies are not installed. Run "
            "'python -m pip install -r requirements.txt'."
        ) from error
    return build, HttpError


def _save_credentials(creds: Any, token_path: Path) -> None:
    token_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = token_path.with_name(f".{token_path.name}.tmp")
    try:
        temporary_path.write_text(creds.to_json(), encoding="utf-8")
        try:
            temporary_path.chmod(0o600)
        except OSError:
            pass
        os.replace(temporary_path, token_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()
    try:
        token_path.chmod(0o600)
    except OSError:
        pass


def _load_valid_credentials(*, token_path: Path | None = None):
    Request, Credentials, _ = _import_google_auth()
    resolved_token = token_path or get_token_path()

    if not resolved_token.exists():
        raise GmailAuthorizationRequiredError(
            "Gmail is not connected yet. Connect Gmail to continue."
        )

    try:
        creds = Credentials.from_authorized_user_file(
            str(resolved_token),
            list(GMAIL_SCOPES),
        )
    except Exception as error:
        raise GmailAuthorizationRequiredError(
            "The saved Gmail authorization could not be read. Reconnect Gmail."
        ) from error

    if creds.valid:
        return creds

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as error:
            raise GmailAuthorizationRequiredError(
                "Gmail authorization expired or was revoked. Reconnect Gmail."
            ) from error
        _save_credentials(creds, resolved_token)
        return creds

    raise GmailAuthorizationRequiredError(
        "Gmail authorization is no longer valid. Reconnect Gmail."
    )


def _service_for_credentials(creds: Any):
    build, _ = _import_google_api()
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _gmail_email_for_credentials(creds: Any) -> str:
    service = _service_for_credentials(creds)
    try:
        profile = service.users().getProfile(userId="me").execute()
    except Exception as error:
        raise _translate_api_error(error) from error

    email_address = str(profile.get("emailAddress", "")).strip()
    if not email_address:
        raise GmailApiError(
            "Gmail authorization succeeded, but the account email address "
            "could not be identified."
        )
    return email_address


def connect_gmail(
    *,
    credentials_path: Path | None = None,
    token_path: Path | None = None,
    force_account_selection: bool = False,
) -> str:
    """
    Run Google's installed-app OAuth flow and atomically replace the active token.

    The existing token is not touched until the new authorization has completed
    and the Gmail account identity has been verified. This keeps a failed account
    change from disconnecting the currently active mailbox.
    """

    _, _, InstalledAppFlow = _import_google_auth()
    resolved_credentials = credentials_path or get_credentials_path()
    resolved_token = token_path or get_token_path()

    if not resolved_credentials.exists():
        raise GmailConfigurationError(
            "Google OAuth client credentials are missing. Add the Desktop app "
            f"credentials file at '{resolved_credentials}'."
        )

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(resolved_credentials),
            list(GMAIL_SCOPES),
        )
        oauth_kwargs = {}
        if force_account_selection:
            # Force Google's account chooser for an explicit Change Gmail account
            # action. `consent` also ensures a refresh token can be returned.
            oauth_kwargs["prompt"] = "select_account consent"
        creds = flow.run_local_server(port=0, **oauth_kwargs)
        email_address = _gmail_email_for_credentials(creds)
    except GmailIntegrationError:
        raise
    except Exception as error:
        raise GmailAuthorizationRequiredError(
            "Gmail authorization did not complete. Try connecting again."
        ) from error

    try:
        _save_credentials(creds, resolved_token)
    except OSError as error:
        raise GmailConfigurationError(
            f"Could not save Gmail authorization at '{resolved_token}'."
        ) from error
    return email_address


def switch_gmail_account(
    *,
    credentials_path: Path | None = None,
    token_path: Path | None = None,
) -> str:
    """Replace the one active Gmail account after explicit user confirmation."""

    return connect_gmail(
        credentials_path=credentials_path,
        token_path=token_path,
        force_account_selection=True,
    )


def get_connected_gmail_email(*, token_path: Path | None = None) -> str:
    """Return the email address represented by the current local Gmail token."""

    creds = _load_valid_credentials(token_path=token_path)
    return _gmail_email_for_credentials(creds)


def gmail_account_key(email_address: str) -> str:
    normalized = email_address.strip().casefold()
    if not normalized:
        raise ValueError("email_address must not be blank")
    return f"gmail:{normalized}"


def is_gmail_connected(*, token_path: Path | None = None) -> bool:
    """Check local authorization, silently refreshing an expired access token."""

    try:
        _load_valid_credentials(token_path=token_path)
    except GmailAuthorizationRequiredError:
        return False
    return True


def has_saved_gmail_token(*, token_path: Path | None = None) -> bool:
    return (token_path or get_token_path()).exists()


def _gmail_service():
    creds = _load_valid_credentials()
    return _service_for_credentials(creds)


def _http_status(error: Exception) -> int | None:
    response = getattr(error, "resp", None)
    status = getattr(response, "status", None)
    try:
        return int(status) if status is not None else None
    except (TypeError, ValueError):
        return None


def _translate_api_error(error: Exception) -> GmailIntegrationError:
    status = _http_status(error)
    if status == 401:
        return GmailAuthorizationRequiredError(
            "We couldn’t access Gmail. Reconnect Gmail to continue."
        )
    return GmailApiError(f"Gmail API request failed: {error}")


def _header_value(payload: dict[str, Any], name: str) -> str:
    target = name.casefold()
    for header in payload.get("headers", []) or []:
        if str(header.get("name", "")).casefold() == target:
            return str(header.get("value", "")).strip()
    return ""


def _decode_base64url(value: str) -> bytes:
    encoded = value.encode("ascii")
    padding = b"=" * (-len(encoded) % 4)
    return base64.urlsafe_b64decode(encoded + padding)


def _part_bytes(service: Any, message_id: str, part: dict[str, Any]) -> bytes:
    body = part.get("body") or {}
    data = body.get("data")
    if data:
        return _decode_base64url(str(data))

    attachment_id = body.get("attachmentId")
    if not attachment_id:
        return b""

    attachment = (
        service.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()
    )
    attachment_data = attachment.get("data")
    return _decode_base64url(str(attachment_data)) if attachment_data else b""


def _iter_mime_parts(part: dict[str, Any]):
    children = part.get("parts") or []
    if children:
        for child in children:
            yield from _iter_mime_parts(child)
    else:
        yield part


class _HTMLBodyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._text_parts: list[str] = []
        self._links: list[EmailLink] = []
        self._current_href: str | None = None
        self._current_link_text: list[str] = []
        self._suppressed_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        lowered = tag.casefold()
        if lowered in {"script", "style"}:
            self._suppressed_depth += 1
            return
        if self._suppressed_depth:
            return
        if lowered in {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4"}:
            self._text_parts.append("\n")
        if lowered == "a":
            attrs_dict = {str(k).casefold(): str(v) for k, v in attrs if v is not None}
            href = attrs_dict.get("href", "").strip()
            self._current_href = href or None
            self._current_link_text = []

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered in {"script", "style"}:
            if self._suppressed_depth:
                self._suppressed_depth -= 1
            return
        if self._suppressed_depth:
            return
        if lowered == "a" and self._current_href:
            label = " ".join("".join(self._current_link_text).split())
            href = unescape(self._current_href)
            if href.startswith(("http://", "https://")):
                self._links.append(EmailLink(text=label, url=href))
            self._current_href = None
            self._current_link_text = []
        if lowered in {"p", "div", "li", "tr"}:
            self._text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._suppressed_depth:
            return
        self._text_parts.append(data)
        if self._current_href is not None:
            self._current_link_text.append(data)

    @property
    def text(self) -> str:
        lines = [" ".join(line.split()) for line in "".join(self._text_parts).splitlines()]
        return "\n".join(line for line in lines if line).strip()

    @property
    def links(self) -> tuple[EmailLink, ...]:
        seen: set[tuple[str, str]] = set()
        unique: list[EmailLink] = []
        for link in self._links:
            key = (link.text, link.url)
            if key not in seen:
                unique.append(link)
                seen.add(key)
        return tuple(unique)


def _extract_message_content(
    service: Any,
    message_id: str,
    payload: dict[str, Any],
) -> tuple[str, tuple[EmailLink, ...]]:
    plain_parts: list[str] = []
    html_parts: list[str] = []

    for part in _iter_mime_parts(payload):
        mime_type = str(part.get("mimeType", "")).casefold()
        if mime_type not in {"text/plain", "text/html"}:
            continue
        raw = _part_bytes(service, message_id, part)
        if not raw:
            continue
        text = raw.decode("utf-8", errors="replace")
        if mime_type == "text/plain":
            plain_parts.append(text.strip())
        else:
            html_parts.append(text)

    links: list[EmailLink] = []
    html_text: list[str] = []
    for html_body in html_parts:
        parser = _HTMLBodyParser()
        parser.feed(html_body)
        parser.close()
        if parser.text:
            html_text.append(parser.text)
        links.extend(parser.links)

    body = "\n\n".join(part for part in plain_parts if part).strip()
    if not body:
        body = "\n\n".join(part for part in html_text if part).strip()

    seen_urls: set[tuple[str, str]] = set()
    unique_links: list[EmailLink] = []
    for link in links:
        key = (link.text, link.url)
        if key not in seen_urls:
            unique_links.append(link)
            seen_urls.add(key)

    return body, tuple(unique_links)


def _infer_source(sender: str) -> str:
    normalized = sender.casefold()
    if "linkedin" in normalized:
        return "LINKEDIN"
    if "indeed" in normalized:
        return "INDEED"
    if "ziprecruiter" in normalized:
        return "ZIPRECRUITER"
    return "EMAIL"


class GmailEmailSource:
    """
    Gmail adapter implementing metadata-first discovery and body-on-demand.

    `service_factory` exists for deterministic unit tests; production uses the
    authenticated Gmail API client built from the locally persisted OAuth token.
    """

    def __init__(
        self,
        *,
        lookback_hours: int | None = None,
        lookback_days: int | None = None,
        max_messages: int | None = None,
        service_factory: Callable[[], Any] | None = None,
    ) -> None:
        if lookback_hours is not None and lookback_days is not None:
            raise ValueError(
                "Specify only one of lookback_hours or lookback_days."
            )

        configured_hours = os.getenv(ENV_LOOKBACK_HOURS, "").strip()
        configured_days = os.getenv(ENV_LOOKBACK_DAYS, "").strip()

        if lookback_hours is not None:
            self.lookback_hours = lookback_hours
            self.lookback_days = None
        elif lookback_days is not None:
            self.lookback_hours = None
            self.lookback_days = lookback_days
        elif configured_hours:
            self.lookback_hours = _positive_int_from_env(
                ENV_LOOKBACK_HOURS,
                DEFAULT_LOOKBACK_HOURS,
            )
            self.lookback_days = None
        elif configured_days:
            # Keep the old day-based environment variable working if it
            # is already present in a local .env file.
            self.lookback_hours = None
            self.lookback_days = _positive_int_from_env(
                ENV_LOOKBACK_DAYS,
                DEFAULT_LOOKBACK_DAYS,
            )
        else:
            # Current low-quota testing default: a rolling 60-minute window.
            self.lookback_hours = DEFAULT_LOOKBACK_HOURS
            self.lookback_days = None

        if self.lookback_hours is not None and self.lookback_hours <= 0:
            raise ValueError("lookback_hours must be greater than zero.")
        if self.lookback_days is not None and self.lookback_days <= 0:
            raise ValueError("lookback_days must be greater than zero.")

        self.max_messages = max_messages or _positive_int_from_env(
            ENV_MAX_MESSAGES,
            DEFAULT_MAX_MESSAGES,
        )
        if self.max_messages <= 0:
            raise ValueError("max_messages must be greater than zero.")
        self._service_factory = service_factory or _gmail_service
        self._account_key: str | None = None

    def _service(self):
        return self._service_factory()

    def account_key(self) -> str:
        if self._account_key is not None:
            return self._account_key

        service = self._service()
        try:
            profile = service.users().getProfile(userId="me").execute()
        except Exception as error:
            raise _translate_api_error(error) from error

        email_address = str(profile.get("emailAddress", "")).strip()
        if not email_address:
            raise GmailApiError(
                "The connected Gmail account email address could not be identified."
            )
        self._account_key = gmail_account_key(email_address)
        return self._account_key

    def list_message_metadata(self) -> list[EmailMetadata]:
        service = self._service()
        message_refs: list[dict[str, Any]] = []
        page_token: str | None = None
        if self.lookback_hours is not None:
            # Gmail's newer_than: operator supports d/m/y, not hours.
            # The API accepts epoch seconds with after:, which gives us a
            # precise rolling-hour window regardless of local timezone.
            cutoff_epoch_seconds = int(time.time()) - (
                self.lookback_hours * 60 * 60
            )
            query = f"after:{cutoff_epoch_seconds}"
        else:
            query = f"newer_than:{self.lookback_days}d"

        try:
            while len(message_refs) < self.max_messages:
                remaining = self.max_messages - len(message_refs)
                response = (
                    service.users()
                    .messages()
                    .list(
                        userId="me",
                        q=query,
                        maxResults=min(remaining, 500),
                        pageToken=page_token,
                    )
                    .execute()
                )
                message_refs.extend(response.get("messages", []) or [])
                page_token = response.get("nextPageToken")
                if not page_token:
                    break
        except Exception as error:
            raise _translate_api_error(error) from error

        metadata: list[EmailMetadata] = []
        for ref in message_refs[: self.max_messages]:
            message_id = str(ref.get("id", "")).strip()
            if not message_id:
                continue
            try:
                message = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=message_id,
                        format="metadata",
                        metadataHeaders=["From", "Subject", "Date"],
                    )
                    .execute()
                )
            except Exception as error:
                raise _translate_api_error(error) from error

            payload = message.get("payload") or {}
            metadata.append(
                EmailMetadata(
                    message_id=message_id,
                    thread_id=(str(message.get("threadId", "")).strip() or None),
                    sender=_header_value(payload, "From"),
                    subject=_header_value(payload, "Subject"),
                    sent_at=(_header_value(payload, "Date") or None),
                    snippet=str(message.get("snippet", "")).strip(),
                )
            )

        return metadata

    def get_message(self, message_id: str) -> JobAlertEmail:
        service = self._service()
        try:
            message = (
                service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
            payload = message.get("payload") or {}
            body, links = _extract_message_content(service, message_id, payload)
        except Exception as error:
            raise _translate_api_error(error) from error

        sender = _header_value(payload, "From")
        return JobAlertEmail(
            message_id=message_id,
            source=_infer_source(sender),
            sender=sender,
            subject=_header_value(payload, "Subject"),
            snippet=str(message.get("snippet", "")).strip(),
            body=body,
            thread_id=(str(message.get("threadId", "")).strip() or None),
            sent_at=(_header_value(payload, "Date") or None),
            links=links,
        )
