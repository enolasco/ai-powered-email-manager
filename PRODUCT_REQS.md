# AI-Powered Outlook Email Manager
## Product Requirements Document (PRD)

---

# 1. Project Overview

## Project Name

**MailPilot** (working title)

## Goal

Build a cross-platform desktop application that helps users manage Outlook emails using Artificial Intelligence.

The application will:

- Connect securely to Microsoft Outlook using Microsoft Graph API.
- Catalog and index emails locally.
- Automatically classify and score emails.
- Suggest cleanup actions.
- Detect newsletters, notifications, duplicates, and low-value emails.
- Provide AI-powered summaries and search.
- Never automatically delete emails without user approval.

Primary focus:

- Inbox organization
- Productivity
- Privacy
- Safe email cleanup

---

# 2. Technology Stack

## Desktop Framework

### Tauri v2

Reasons:

- Lightweight application size
- Lower memory usage than Electron
- Native performance
- Strong security model

---

## Frontend

### SvelteKit

Reasons:

- Simpler development experience
- Reactive state management
- Smaller bundles
- Excellent integration with Tauri

---

## Styling

### TailwindCSS

Requirements:

- Utility-first CSS
- Dark mode support
- Responsive layouts
- Modern dashboard styling

---

## Backend

### Rust

Responsibilities:

- Microsoft Graph integration
- Database operations
- AI service orchestration
- File system access
- Secure token handling

---

## Database

### SQLite

Reasons:

- Local-first architecture
- No external dependency
- Fast indexing
- Supports FTS5 full-text search

---

## AI Providers

### Local AI (Primary)

#### Ollama

Supported Models:

- Qwen
- Llama
- Mistral

Benefits:

- Full privacy
- No cloud costs
- Email content remains local

---

### Cloud AI (Optional)

#### Azure OpenAI

Use Cases:

- Advanced classification
- Summarization
- Semantic search
- Action extraction

---

# 3. High-Level Architecture

```text
Microsoft Outlook
       │
Microsoft Graph API
       │
 ┌───────────────┐
 │ Rust Backend  │
 └───────┬───────┘
         │
 ┌───────▼──────────┐
 │ Email Processor  │
 └───────┬──────────┘
         │
 ┌───────▼────────────┐
 │ AI Classification  │
 └───────┬────────────┘
         │
 ┌───────▼───────────┐
 │ SQLite Database   │
 └───────┬───────────┘
         │
 ┌───────▼─────────┐
 │ Svelte Frontend │
 └─────────────────┘
```

---

# 4. Core Features

## 4.1 Outlook Integration

### Requirements

The application shall:

- Authenticate via Microsoft OAuth
- Access mailbox using Microsoft Graph API
- Read email messages
- Read folders
- Move emails between folders
- Archive messages
- Delete messages after approval

### Graph Endpoints

```http
GET /me/messages

GET /me/mailFolders

POST /me/messages/{id}/move

DELETE /me/messages/{id}
```

---

## 4.2 Email Catalog

All emails shall be stored locally.

### Metadata

Store:

- Message ID
- Subject
- Sender
- Recipients
- Received date
- Folder
- Categories
- Importance score
- AI summary
- Suggested action

### Example

```json
{
  "id": "abc123",
  "subject": "Invoice July",
  "sender": "billing@company.com",
  "category": "Financial",
  "importance": 90,
  "summary": "Invoice for July services",
  "suggested_action": "Keep"
}
```

---

## 4.3 AI Classification

Each email should be analyzed automatically.

### Categories

- Important
- Client Communication
- Financial
- Personal
- Newsletter
- Promotion
- Notification
- Spam-like
- System Alert
- Meeting
- Action Required
- Unknown

---

### Output Schema

```json
{
  "category": "",
  "importance": 0,
  "delete_candidate": false,
  "reason": "",
  "summary": ""
}
```

---

# 5. Email Cleanup System

## Safety Rule

### AI MUST NEVER DELETE EMAILS AUTOMATICALLY

Instead:

1. Analyze email
2. Mark as delete candidate
3. Present to user
4. Require approval
5. Delete only after confirmation

---

## Delete Candidate Logic

Example:

```text
IF:
- category = Newsletter
- importance < 20
- older than 180 days

THEN:
Mark as Delete Candidate
```

---

## Review Workflow

```text
AI Recommendation
        ↓
Review Queue
        ↓
User Decision
        ↓
Archive / Keep / Delete
```

---

# 6. User Interface

## Layout

```text
┌─────────────────────────────┐
│ Sidebar                     │
├─────────────────────────────┤
│ Inbox                       │
│ AI Suggestions              │
│ Delete Candidates           │
│ Newsletters                 │
│ Archive                     │
│ Search                      │
│ Settings                    │
└─────────────────────────────┘
```

---

## Main Email Table

Columns:

- Sender
- Subject
- Date
- Category
- Importance Score
- Suggested Action

Example:

```text
Sender          Subject            Score    Action
----------------------------------------------------
Microsoft       Security Alert      98       Keep
Newsletter      Weekly Deals        11       Delete
Bank            Invoice             92       Keep
```

---

## Email Detail Panel

Display:

- Full email
- AI summary
- Category
- Importance score
- Delete recommendation
- Reasoning

Example:

```text
Category:
Newsletter

Importance:
12/100

Recommendation:
Delete Candidate

Reason:
Recurring marketing newsletter.
```

---

# 7. AI Features

## 7.1 Email Summarization

Generate short summaries.

Example:

```text
Vendor requests approval of a software renewal
before next Friday.
```

---

## 7.2 Action Item Extraction

Extract:

- Tasks
- Deadlines
- Requests

Example:

```text
Action Required:
Approve Q3 budget

Deadline:
August 15
```

---

## 7.3 Semantic Search

Allow queries like:

```text
Find invoices from last year

Show emails about cloud migration

Find contracts from John
```

instead of keyword search.

---

## 7.4 Duplicate Detection

Detect:

- Duplicate messages
- Mailing-list repeats
- Identical content

Suggested action:

```text
Archive Duplicate
```

---

## 7.5 Newsletter Detection

Identify sources such as:

- Mailchimp
- Substack
- Medium
- Marketing platforms

Automatically group them.

---

# 8. Daily AI Insights

Generate inbox reports.

Example:

```text
Inbox Summary

Important Emails: 5

Action Required: 3

Newsletters: 18

Notifications: 12

Delete Candidates: 42
```

---

# 9. Learning System

The application shall learn from user actions.

Track:

```text
AI Suggested Delete
User Kept

AI Suggested Keep
User Deleted
```

Store decisions locally.

Example Table:

```sql
CREATE TABLE user_feedback (
    email_id TEXT,
    ai_decision TEXT,
    user_decision TEXT,
    created_at DATETIME
);
```

Purpose:

- Improve recommendations
- Personalize scoring

---

# 10. Database Design

## Emails Table

```sql
CREATE TABLE emails (
    id TEXT PRIMARY KEY,
    sender TEXT,
    subject TEXT,
    body TEXT,
    received_at DATETIME,
    folder TEXT,
    category TEXT,
    importance INTEGER,
    delete_candidate BOOLEAN,
    summary TEXT
);
```

---

## Embeddings Table

```sql
CREATE TABLE embeddings (
    email_id TEXT,
    embedding BLOB
);
```

---

## Feedback Table

```sql
CREATE TABLE user_feedback (
    email_id TEXT,
    ai_decision TEXT,
    user_decision TEXT,
    created_at DATETIME
);
```

---

# 11. Security Requirements

## Authentication

Use:

- Microsoft OAuth 2.0
- Microsoft Entra ID

---

## Storage

Store locally:

- Email metadata
- AI results
- User preferences

Encrypt:

- OAuth tokens
- Sensitive configuration

Use OS-native secure key storage.

---

## Privacy

Default mode:

```text
Local AI Only
```

No email content shall leave the machine unless the user explicitly enables cloud AI providers.

---

# 12. Development Roadmap

## Version 1 (MVP)

Features:

- Microsoft Graph authentication
- Inbox synchronization
- SQLite storage
- AI categorization
- Email summaries
- Delete candidate detection
- Manual review queue

---

## Version 2

Features:

- Newsletter management
- Duplicate detection
- Semantic search
- Daily inbox summaries
- Feedback learning

---

## Version 3

Features:

- Personalized AI recommendations
- Natural language inbox commands

Examples:

```text
Archive newsletters older than one year

Show emails related to invoices

Find unanswered customer emails
```

---

# 13. Preferred Stack Summary

```text
Desktop:
  Tauri v2

Frontend:
  SvelteKit
  TypeScript
  TailwindCSS

Backend:
  Rust

Email:
  Microsoft Graph API

Database:
  SQLite
  SQLite FTS5

AI:
  Ollama (Primary)
  Azure OpenAI (Optional)

Authentication:
  Microsoft Entra ID OAuth

Deployment:
  Windows
  macOS
  Linux
```

---

# Success Criteria

The application is considered successful when it can:

- Connect to Outlook securely.
- Catalog and index emails locally.
- Classify emails using AI.
- Generate meaningful summaries.
- Detect low-value emails.
- Suggest cleanup actions.
- Provide semantic search.
- Protect user privacy.
- Require user approval before deletion.
