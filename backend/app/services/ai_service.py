"""AI service — uses OpenAI to classify, summarize and draft email replies."""

from __future__ import annotations

import json
from typing import Optional

from openai import OpenAI

from app.models.email import Email, EmailSummary, DraftReply


_CATEGORIES = ["Work", "Personal", "Finance", "Promotions", "Social", "Updates", "Spam", "Other"]
_PRIORITIES = ["High", "Medium", "Low"]
_SENTIMENTS = ["Positive", "Neutral", "Negative", "Urgent"]


class AIService:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def summarize(self, email: Email) -> EmailSummary:
        prompt = self._build_summarize_prompt(email)
        response = self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert email assistant. Analyze emails and return structured JSON. "
                        "Always respond with valid JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        raw = json.loads(response.choices[0].message.content)
        return EmailSummary(
            email_id=email.id,
            summary=raw.get("summary", ""),
            category=raw.get("category", "Other"),
            priority=raw.get("priority", "Medium"),
            sentiment=raw.get("sentiment", "Neutral"),
            action_items=raw.get("action_items", []),
        )

    def draft_reply(self, email: Email, tone: str = "professional", context: Optional[str] = None) -> DraftReply:
        prompt = self._build_draft_prompt(email, tone, context)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a helpful email assistant. Draft a {tone} reply to the provided email. "
                        "Write only the email body — no subject line, no 'Subject:' prefix."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        draft_text = response.choices[0].message.content.strip()
        return DraftReply(email_id=email.id, draft=draft_text, tone=tone)

    def classify(self, email: Email) -> dict:
        """Return category and priority for a single email."""
        prompt = (
            f"Classify this email.\n\n"
            f"Subject: {email.subject}\n"
            f"From: {email.sender}\n"
            f"Snippet: {email.snippet}\n\n"
            f"Return JSON with keys: category (one of {_CATEGORIES}), priority (one of {_PRIORITIES})."
        )
        response = self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an email classifier. Respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        return json.loads(response.choices[0].message.content)

    def bulk_summarize(self, emails: list[Email]) -> list[EmailSummary]:
        return [self.summarize(e) for e in emails]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_summarize_prompt(self, email: Email) -> str:
        return (
            f"Analyze the following email and return a JSON object with these fields:\n"
            f"- summary: a concise 1-2 sentence summary\n"
            f"- category: one of {_CATEGORIES}\n"
            f"- priority: one of {_PRIORITIES}\n"
            f"- sentiment: one of {_SENTIMENTS}\n"
            f"- action_items: list of specific actions required (empty list if none)\n\n"
            f"Email:\n"
            f"Subject: {email.subject}\n"
            f"From: {email.sender}\n"
            f"Date: {email.date.isoformat()}\n"
            f"Body:\n{email.body[:3000]}"
        )

    def _build_draft_prompt(self, email: Email, tone: str, context: Optional[str]) -> str:
        ctx_section = f"\nAdditional context: {context}" if context else ""
        return (
            f"Draft a {tone} reply to the following email.{ctx_section}\n\n"
            f"Original email:\n"
            f"Subject: {email.subject}\n"
            f"From: {email.sender}\n"
            f"Body:\n{email.body[:3000]}"
        )
