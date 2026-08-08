from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Email(BaseModel):
    id: str
    thread_id: str
    subject: str
    sender: str
    recipients: list[str]
    body: str
    snippet: str
    date: datetime
    is_read: bool = False
    labels: list[str] = []


class EmailSummary(BaseModel):
    email_id: str
    summary: str
    category: str
    priority: str
    sentiment: str
    action_items: list[str]


class DraftReply(BaseModel):
    email_id: str
    draft: str
    tone: str


class ClassifyRequest(BaseModel):
    email_id: str


class SummarizeRequest(BaseModel):
    email_id: str


class DraftReplyRequest(BaseModel):
    email_id: str
    tone: str = "professional"
    context: Optional[str] = None


class BulkActionRequest(BaseModel):
    email_ids: list[str]
    action: str  # "archive", "delete", "mark_read", "mark_unread", "label"
    label: Optional[str] = None


class EmailFilter(BaseModel):
    query: Optional[str] = None
    label: Optional[str] = None
    is_read: Optional[bool] = None
    category: Optional[str] = None
    max_results: int = 20
