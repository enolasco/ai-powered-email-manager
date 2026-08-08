"""Gmail service — fetches and manages emails via the Gmail API."""

from __future__ import annotations

import base64
import email as email_lib
from datetime import datetime
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.models.email import Email


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]


def _decode_body(payload: dict) -> str:
    """Recursively extract plain-text body from a Gmail message payload."""
    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    if mime_type.startswith("multipart/"):
        for part in payload.get("parts", []):
            text = _decode_body(part)
            if text:
                return text
    return ""


def _parse_message(raw: dict) -> Email:
    """Convert a raw Gmail API message dict into an Email model."""
    headers = {h["name"].lower(): h["value"] for h in raw["payload"].get("headers", [])}
    recipients_raw = headers.get("to", "")
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
    date_str = headers.get("date", "")
    try:
        date = email_lib.utils.parsedate_to_datetime(date_str)
    except Exception:
        date = datetime.utcnow()

    label_ids: list[str] = raw.get("labelIds", [])

    return Email(
        id=raw["id"],
        thread_id=raw.get("threadId", raw["id"]),
        subject=headers.get("subject", "(no subject)"),
        sender=headers.get("from", ""),
        recipients=recipients,
        body=_decode_body(raw["payload"]),
        snippet=raw.get("snippet", ""),
        date=date,
        is_read="UNREAD" not in label_ids,
        labels=label_ids,
    )


def _parse_metadata_message(raw: dict) -> Email:
    """Convert a Gmail metadata-format message into a lightweight Email (no body)."""
    headers = {h["name"].lower(): h["value"] for h in raw["payload"].get("headers", [])}
    recipients_raw = headers.get("to", "")
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
    date_str = headers.get("date", "")
    try:
        date = email_lib.utils.parsedate_to_datetime(date_str)
    except Exception:
        date = datetime.utcnow()

    label_ids: list[str] = raw.get("labelIds", [])

    return Email(
        id=raw["id"],
        thread_id=raw.get("threadId", raw["id"]),
        subject=headers.get("subject", "(no subject)"),
        sender=headers.get("from", ""),
        recipients=recipients,
        body="",
        snippet=raw.get("snippet", ""),
        date=date,
        is_read="UNREAD" not in label_ids,
        labels=label_ids,
    )


class GmailService:
    """Thin wrapper around the Gmail API."""

    def __init__(self, credentials: Credentials) -> None:
        self._service = build("gmail", "v1", credentials=credentials, cache_discovery=False)

    def list_emails(
        self,
        query: Optional[str] = None,
        label_ids: Optional[list[str]] = None,
        max_results: int = 20,
    ) -> list[Email]:
        kwargs: dict = {"userId": "me", "maxResults": max_results}
        if query:
            kwargs["q"] = query
        if label_ids:
            kwargs["labelIds"] = label_ids

        result = self._service.users().messages().list(**kwargs).execute()
        messages = result.get("messages", [])
        emails: list[Email] = []
        for msg in messages:
            raw = (
                self._service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="metadata",
                     metadataHeaders=["From", "To", "Subject", "Date"])
                .execute()
            )
            emails.append(_parse_metadata_message(raw))
        return emails

    def get_email(self, email_id: str) -> Email:
        raw = (
            self._service.users()
            .messages()
            .get(userId="me", id=email_id, format="full")
            .execute()
        )
        return _parse_message(raw)

    def mark_as_read(self, email_id: str) -> None:
        self._service.users().messages().modify(
            userId="me", id=email_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()

    def mark_as_unread(self, email_id: str) -> None:
        self._service.users().messages().modify(
            userId="me", id=email_id, body={"addLabelIds": ["UNREAD"]}
        ).execute()

    def archive(self, email_id: str) -> None:
        self._service.users().messages().modify(
            userId="me", id=email_id, body={"removeLabelIds": ["INBOX"]}
        ).execute()

    def delete(self, email_id: str) -> None:
        self._service.users().messages().trash(userId="me", id=email_id).execute()

    def add_label(self, email_id: str, label: str) -> None:
        # Try to find or create the label
        labels_result = self._service.users().labels().list(userId="me").execute()
        existing = {lbl["name"]: lbl["id"] for lbl in labels_result.get("labels", [])}
        label_id = existing.get(label)
        if not label_id:
            new_label = (
                self._service.users()
                .labels()
                .create(userId="me", body={"name": label})
                .execute()
            )
            label_id = new_label["id"]
        self._service.users().messages().modify(
            userId="me", id=email_id, body={"addLabelIds": [label_id]}
        ).execute()

    def send_reply(self, original: Email, body: str) -> None:
        import email.mime.text
        import email.mime.multipart

        msg = email.mime.multipart.MIMEMultipart()
        msg["to"] = original.sender
        msg["subject"] = f"Re: {original.subject}"
        msg["In-Reply-To"] = original.id
        msg["References"] = original.id
        msg.attach(email.mime.text.MIMEText(body, "plain"))
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        self._service.users().messages().send(
            userId="me",
            body={"raw": raw, "threadId": original.thread_id},
        ).execute()
