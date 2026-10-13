import base64
from pathlib import Path

import pytest

from job_agent.integrations import gmail
from job_agent.integrations.gmail import (
    GmailAuthorizationRequiredError,
    GmailEmailSource,
    gmail_account_key,
    switch_gmail_account,
)


def _b64(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii").rstrip("=")


class _Request:
    def __init__(self, response):
        self.response = response

    def execute(self):
        return self.response


class _Messages:
    def __init__(self):
        self.list_calls = []
        self.get_calls = []

    def list(self, **kwargs):
        self.list_calls.append(kwargs)
        return _Request({"messages": [{"id": "m1", "threadId": "t1"}]})

    def get(self, **kwargs):
        self.get_calls.append(kwargs)
        if kwargs["format"] == "metadata":
            return _Request(
                {
                    "id": "m1",
                    "threadId": "t1",
                    "snippet": "AI Product Manager at Example",
                    "payload": {
                        "headers": [
                            {"name": "From", "value": "LinkedIn Jobs <jobs@linkedin.com>"},
                            {"name": "Subject", "value": "New jobs for you"},
                            {"name": "Date", "value": "Tue, 22 Sep 2026 10:00:00 -0700"},
                        ]
                    },
                }
            )

        html = (
            '<html><body><h2>AI Product Manager</h2>'
            '<a href="https://www.linkedin.com/jobs/view/123">View job</a>'
            '</body></html>'
        )
        return _Request(
            {
                "id": "m1",
                "threadId": "t1",
                "snippet": "AI Product Manager at Example",
                "payload": {
                    "mimeType": "multipart/alternative",
                    "headers": [
                        {"name": "From", "value": "LinkedIn Jobs <jobs@linkedin.com>"},
                        {"name": "Subject", "value": "New jobs for you"},
                        {"name": "Date", "value": "Tue, 22 Sep 2026 10:00:00 -0700"},
                    ],
                    "parts": [
                        {
                            "mimeType": "text/plain",
                            "body": {"data": _b64("AI Product Manager at Example")},
                        },
                        {
                            "mimeType": "text/html",
                            "body": {"data": _b64(html)},
                        },
                    ],
                },
            }
        )

    def attachments(self):
        raise AssertionError("No attachment fetch expected")


class _Users:
    def __init__(self, messages, email_address="you@example.com"):
        self._messages = messages
        self.email_address = email_address
        self.profile_calls = []

    def messages(self):
        return self._messages

    def getProfile(self, **kwargs):
        self.profile_calls.append(kwargs)
        return _Request({"emailAddress": self.email_address})


class _Service:
    def __init__(self, email_address="you@example.com"):
        self.messages_api = _Messages()
        self._users = _Users(self.messages_api, email_address=email_address)

    def users(self):
        return self._users


def test_gmail_source_lists_metadata_then_fetches_full_message_on_demand():
    service = _Service()
    source = GmailEmailSource(
        lookback_days=7,
        max_messages=25,
        service_factory=lambda: service,
    )

    metadata = source.list_message_metadata()
    assert len(metadata) == 1
    assert metadata[0].message_id == "m1"
    assert metadata[0].sender.startswith("LinkedIn Jobs")
    assert service.messages_api.list_calls[0]["q"] == "newer_than:7d"
    assert service.messages_api.get_calls == [
        {
            "userId": "me",
            "id": "m1",
            "format": "metadata",
            "metadataHeaders": ["From", "Subject", "Date"],
        }
    ]

    message = source.get_message("m1")
    assert message.source == "LINKEDIN"
    assert message.body == "AI Product Manager at Example"
    assert len(message.links) == 1
    assert message.links[0].text == "View job"
    assert message.links[0].url == "https://www.linkedin.com/jobs/view/123"
    assert service.messages_api.get_calls[-1]["format"] == "full"


def test_gmail_source_account_key_is_stable_and_account_scoped():
    service = _Service(email_address="Job.Search@Example.com")
    source = GmailEmailSource(service_factory=lambda: service)

    assert source.account_key() == "gmail:job.search@example.com"
    assert source.account_key() == "gmail:job.search@example.com"
    assert service._users.profile_calls == [{"userId": "me"}]
    assert gmail_account_key(" Job.Search@Example.com ") == "gmail:job.search@example.com"


def test_switch_gmail_account_preserves_existing_token_when_oauth_fails(
    tmp_path: Path,
    monkeypatch,
):
    credentials_path = tmp_path / "google_credentials.json"
    token_path = tmp_path / "gmail_token.json"
    credentials_path.write_text("{}", encoding="utf-8")
    token_path.write_text("old-token", encoding="utf-8")

    class FakeFlow:
        @classmethod
        def from_client_secrets_file(cls, *args, **kwargs):
            return cls()

        def run_local_server(self, **kwargs):
            raise RuntimeError("cancelled")

    monkeypatch.setattr(
        gmail,
        "_import_google_auth",
        lambda: (object, object, FakeFlow),
    )

    with pytest.raises(GmailAuthorizationRequiredError):
        switch_gmail_account(
            credentials_path=credentials_path,
            token_path=token_path,
        )

    assert token_path.read_text(encoding="utf-8") == "old-token"


def test_switch_gmail_account_saves_new_token_after_verified_profile(
    tmp_path: Path,
    monkeypatch,
):
    credentials_path = tmp_path / "google_credentials.json"
    token_path = tmp_path / "gmail_token.json"
    credentials_path.write_text("{}", encoding="utf-8")
    token_path.write_text("old-token", encoding="utf-8")

    captured = {}

    class FakeCredentials:
        def to_json(self):
            return '{"token":"new-token"}'

    class FakeFlow:
        @classmethod
        def from_client_secrets_file(cls, *args, **kwargs):
            return cls()

        def run_local_server(self, **kwargs):
            captured.update(kwargs)
            return FakeCredentials()

    monkeypatch.setattr(
        gmail,
        "_import_google_auth",
        lambda: (object, object, FakeFlow),
    )
    monkeypatch.setattr(
        gmail,
        "_gmail_email_for_credentials",
        lambda creds: "new.job@example.com",
    )

    email_address = switch_gmail_account(
        credentials_path=credentials_path,
        token_path=token_path,
    )

    assert email_address == "new.job@example.com"
    assert captured["port"] == 0
    assert "select_account" in captured["prompt"]
    assert "consent" in captured["prompt"]
    assert token_path.read_text(encoding="utf-8") == '{"token":"new-token"}'
