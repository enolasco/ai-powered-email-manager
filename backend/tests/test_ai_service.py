"""Tests for the AI service (mocked OpenAI calls)."""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.models.email import Email
from app.services.ai_service import AIService


@pytest.fixture()
def sample_email() -> Email:
    return Email(
        id="msg001",
        thread_id="thread001",
        subject="Q3 Budget Review",
        sender="boss@company.com",
        recipients=["me@company.com"],
        body="Please review the attached Q3 budget by Friday and send your comments.",
        snippet="Please review the attached Q3 budget by Friday",
        date=datetime(2024, 1, 15, 9, 0, 0),
        is_read=False,
        labels=["INBOX", "UNREAD"],
    )


def _make_ai_service() -> AIService:
    return AIService(api_key="test-key", model="gpt-4o-mini")


def _mock_openai_response(content: str):
    """Build a minimal mock that mimics the openai ChatCompletion response."""
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


class TestAIServiceSummarize:
    def test_summarize_returns_email_summary(self, sample_email):
        payload = json.dumps({
            "summary": "Budget review request due Friday.",
            "category": "Work",
            "priority": "High",
            "sentiment": "Neutral",
            "action_items": ["Review Q3 budget", "Send comments by Friday"],
        })
        with patch("app.services.ai_service.OpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = _mock_openai_response(payload)
            ai = _make_ai_service()
            result = ai.summarize(sample_email)

        assert result.email_id == "msg001"
        assert result.summary == "Budget review request due Friday."
        assert result.category == "Work"
        assert result.priority == "High"
        assert result.sentiment == "Neutral"
        assert "Review Q3 budget" in result.action_items

    def test_summarize_handles_missing_fields(self, sample_email):
        """Missing fields should fall back to defaults."""
        payload = json.dumps({"summary": "Short summary."})
        with patch("app.services.ai_service.OpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = _mock_openai_response(payload)
            ai = _make_ai_service()
            result = ai.summarize(sample_email)

        assert result.category == "Other"
        assert result.priority == "Medium"
        assert result.sentiment == "Neutral"
        assert result.action_items == []


class TestAIServiceDraftReply:
    def test_draft_reply_returns_draft(self, sample_email):
        draft_text = "Hi,\n\nThank you for reaching out. I will review the Q3 budget by Friday.\n\nBest regards"
        with patch("app.services.ai_service.OpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = _mock_openai_response(draft_text)
            ai = _make_ai_service()
            result = ai.draft_reply(sample_email, tone="professional")

        assert result.email_id == "msg001"
        assert result.tone == "professional"
        assert "Friday" in result.draft

    def test_draft_reply_with_context(self, sample_email):
        draft_text = "Will send by Thursday instead."
        with patch("app.services.ai_service.OpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = _mock_openai_response(draft_text)
            ai = _make_ai_service()
            result = ai.draft_reply(sample_email, tone="casual", context="I am out Thursday")

        assert result.tone == "casual"


class TestAIServiceClassify:
    def test_classify_returns_dict(self, sample_email):
        payload = json.dumps({"category": "Work", "priority": "High"})
        with patch("app.services.ai_service.OpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.chat.completions.create.return_value = _mock_openai_response(payload)
            ai = _make_ai_service()
            result = ai.classify(sample_email)

        assert result["category"] == "Work"
        assert result["priority"] == "High"
