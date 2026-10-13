from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailLink:
    text: str
    url: str


@dataclass(frozen=True)
class EmailMetadata:
    message_id: str
    thread_id: str | None
    sender: str
    subject: str
    sent_at: str | None
    snippet: str


@dataclass(frozen=True)
class JobAlertEmail:
    message_id: str
    source: str
    sender: str
    subject: str
    snippet: str
    body: str
    thread_id: str | None = None
    sent_at: str | None = None
    links: tuple[EmailLink, ...] = ()

    def as_metadata(self) -> EmailMetadata:
        return EmailMetadata(
            message_id=self.message_id,
            thread_id=self.thread_id,
            sender=self.sender,
            subject=self.subject,
            sent_at=self.sent_at,
            snippet=self.snippet,
        )
