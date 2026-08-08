"""Tests for the FastAPI endpoints (no real Gmail/OpenAI calls)."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.email import Email, EmailSummary, DraftReply


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


SAMPLE_EMAIL = Email(
    id="msg001",
    thread_id="thread001",
    subject="Test Subject",
    sender="sender@example.com",
    recipients=["me@example.com"],
    body="Hello, this is a test email.",
    snippet="Hello, this is a test email.",
    date=datetime(2024, 1, 15, 9, 0, 0),
    is_read=False,
    labels=["INBOX"],
)


class TestHealthAndRoot:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["version"] == "1.0.0"

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestAuthStatus:
    def test_status_unauthenticated(self, client):
        r = client.get("/auth/status")
        assert r.status_code == 200
        assert r.json()["authenticated"] is False


class TestEmailsUnauthenticated:
    def test_list_emails_requires_auth(self, client):
        r = client.get("/emails/")
        assert r.status_code == 401

    def test_get_email_requires_auth(self, client):
        r = client.get("/emails/msg001")
        assert r.status_code == 401


class TestListEmails:
    def test_list_emails_success(self, client):
        mock_gmail = MagicMock()
        mock_gmail.list_emails.return_value = [SAMPLE_EMAIL]

        from app.routers import emails as emails_router
        app.dependency_overrides[emails_router._get_gmail] = lambda: mock_gmail
        try:
            r = client.get("/emails/")
            assert r.status_code == 200
            data = r.json()
            assert data["total"] == 1
            assert data["emails"][0]["id"] == "msg001"
        finally:
            app.dependency_overrides.clear()


class TestSummarizeEmail:
    def test_summarize_email_success(self, client):
        summary = EmailSummary(
            email_id="msg001",
            summary="Test summary.",
            category="Work",
            priority="High",
            sentiment="Neutral",
            action_items=["Do something"],
        )
        mock_gmail = MagicMock()
        mock_gmail.get_email.return_value = SAMPLE_EMAIL
        mock_ai = MagicMock()
        mock_ai.summarize.return_value = summary

        from app.routers import emails as emails_router
        app.dependency_overrides[emails_router._get_gmail] = lambda: mock_gmail
        app.dependency_overrides[emails_router._get_ai] = lambda: mock_ai
        try:
            r = client.post("/emails/msg001/summarize")
            assert r.status_code == 200
            data = r.json()
            assert data["category"] == "Work"
            assert data["priority"] == "High"
        finally:
            app.dependency_overrides.clear()


class TestDraftReply:
    def test_draft_reply_success(self, client):
        draft = DraftReply(email_id="msg001", draft="Thanks for your email.", tone="professional")
        mock_gmail = MagicMock()
        mock_gmail.get_email.return_value = SAMPLE_EMAIL
        mock_ai = MagicMock()
        mock_ai.draft_reply.return_value = draft

        from app.routers import emails as emails_router
        app.dependency_overrides[emails_router._get_gmail] = lambda: mock_gmail
        app.dependency_overrides[emails_router._get_ai] = lambda: mock_ai
        try:
            r = client.post(
                "/emails/msg001/draft-reply",
                json={"email_id": "msg001", "tone": "professional"},
            )
            assert r.status_code == 200
            data = r.json()
            assert data["tone"] == "professional"
            assert "Thanks" in data["draft"]
        finally:
            app.dependency_overrides.clear()
