"""Emails router — CRUD + AI operations on emails."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.config import get_settings, Settings
from app.models.email import (
    BulkActionRequest,
    DraftReply,
    DraftReplyRequest,
    EmailFilter,
    EmailSummary,
)
from app.services.ai_service import AIService
from app.services.auth_service import credentials_from_dict
from app.services.gmail_service import GmailService

router = APIRouter(prefix="/emails", tags=["emails"])
logger = logging.getLogger(__name__)


def _get_gmail(request: Request) -> GmailService:
    creds_data = request.session.get("credentials")
    if not creds_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    creds = credentials_from_dict(creds_data)
    return GmailService(creds)


def _get_ai(settings: Settings = Depends(get_settings)) -> AIService:
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return AIService(settings.openai_api_key)


class SendDraftRequest(BaseModel):
    """Send a pre-written (possibly user-edited) draft reply."""
    email_id: str
    draft: str
    tone: str = "professional"
    context: Optional[str] = None


# ------------------------------------------------------------------
# Static routes (must be registered before /{email_id} routes)
# ------------------------------------------------------------------

@router.get("/")
def list_emails(
    query: str | None = None,
    label: str | None = None,
    max_results: int = 20,
    gmail: GmailService = Depends(_get_gmail),
):
    """List emails with optional query/label filters."""
    label_ids = [label] if label else None
    emails = gmail.list_emails(query=query, label_ids=label_ids, max_results=max_results)
    return {"emails": [e.model_dump(mode="json") for e in emails], "total": len(emails)}


@router.post("/bulk-action")
def bulk_action(
    request_body: BulkActionRequest,
    gmail: GmailService = Depends(_get_gmail),
):
    results = []
    for eid in request_body.email_ids:
        try:
            action = request_body.action
            if action == "archive":
                gmail.archive(eid)
            elif action == "delete":
                gmail.delete(eid)
            elif action == "mark_read":
                gmail.mark_as_read(eid)
            elif action == "mark_unread":
                gmail.mark_as_unread(eid)
            elif action == "label" and request_body.label:
                gmail.add_label(eid, request_body.label)
            else:
                results.append({"id": eid, "status": "error", "detail": "Unknown action"})
                continue
            results.append({"id": eid, "status": "success"})
        except Exception as exc:
            logger.exception("Bulk action %r failed for email %s", request_body.action, eid)
            results.append({"id": eid, "status": "error", "detail": "Action failed"})
    return {"results": results}


@router.post("/ai/bulk-summarize")
def bulk_summarize(
    filter_params: EmailFilter,
    gmail: GmailService = Depends(_get_gmail),
    ai: AIService = Depends(_get_ai),
):
    emails = gmail.list_emails(
        query=filter_params.query,
        label_ids=[filter_params.label] if filter_params.label else None,
        max_results=filter_params.max_results,
    )
    summaries = ai.bulk_summarize(emails)
    return {"summaries": [s.model_dump() for s in summaries]}


# ------------------------------------------------------------------
# Parameterised /{email_id} routes
# ------------------------------------------------------------------

@router.get("/{email_id}")
def get_email(email_id: str, gmail: GmailService = Depends(_get_gmail)):
    email = gmail.get_email(email_id)
    gmail.mark_as_read(email_id)
    return email.model_dump(mode="json")


@router.post("/{email_id}/summarize")
def summarize_email(
    email_id: str,
    gmail: GmailService = Depends(_get_gmail),
    ai: AIService = Depends(_get_ai),
) -> EmailSummary:
    email = gmail.get_email(email_id)
    return ai.summarize(email)


@router.post("/{email_id}/classify")
def classify_email(
    email_id: str,
    gmail: GmailService = Depends(_get_gmail),
    ai: AIService = Depends(_get_ai),
):
    email = gmail.get_email(email_id)
    return ai.classify(email)


@router.post("/{email_id}/draft-reply")
def draft_reply(
    email_id: str,
    body: DraftReplyRequest,
    gmail: GmailService = Depends(_get_gmail),
    ai: AIService = Depends(_get_ai),
) -> DraftReply:
    email = gmail.get_email(email_id)
    return ai.draft_reply(email, tone=body.tone, context=body.context)


@router.post("/{email_id}/send-reply")
def send_reply(
    email_id: str,
    body: SendDraftRequest,
    gmail: GmailService = Depends(_get_gmail),
):
    """Send a pre-written (possibly user-edited) draft reply."""
    email = gmail.get_email(email_id)
    gmail.send_reply(email, body.draft)
    return {"message": "Reply sent", "email_id": email_id}
