# AI-Powered Email Manager

An intelligent email management application that uses OpenAI to automatically classify, summarize, and draft replies to your Gmail messages.

## Features

- 📋 **AI Summarization** — Instantly summarize any email with key points and action items
- 🏷️ **Smart Classification** — Automatically categorize emails (Work, Finance, Personal, etc.) and assign priority (High / Medium / Low)
- ✏️ **AI Reply Drafting** — Generate context-aware reply drafts in your chosen tone (professional, casual, concise, …)
- 📤 **Send Replies** — Review the AI draft and send directly from the app
- 🗂️ **Inbox Management** — Archive, delete, and search emails; bulk actions across multiple messages
- 🔐 **Google OAuth2** — Secure sign-in with your Google account

## Architecture

```
ai-powered-email-manager/
├── backend/          # Python / FastAPI
│   ├── app/
│   │   ├── main.py           # FastAPI app + middleware
│   │   ├── config.py         # Pydantic settings
│   │   ├── models/           # Pydantic data models
│   │   ├── routers/          # API route handlers (auth, emails)
│   │   └── services/         # Gmail API + OpenAI wrappers
│   ├── tests/                # pytest test suite
│   └── requirements.txt
└── frontend/         # React + TypeScript (Vite)
    └── src/
        ├── components/       # EmailList, EmailDetail
        ├── hooks/            # useEmails, useAI
        ├── pages/            # LoginPage, InboxPage
        └── utils/            # Axios API client
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [Google Cloud project](https://console.cloud.google.com/) with the Gmail API enabled and OAuth2 credentials

## Backend Setup

```bash
cd backend

# Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and fill in OPENAI_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

# Run the development server
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**.  
Interactive docs: **http://localhost:8000/docs**

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if your backend runs on a different port

# Start the dev server
npm run dev
```

The app will be available at **http://localhost:3000** (or the port Vite picks).

## Google OAuth2 Setup

1. Go to [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Create an **OAuth 2.0 Client ID** of type *Web application*
3. Add `http://localhost:8000/auth/callback` as an authorised redirect URI
4. Enable the **Gmail API** under *APIs & Services → Library*
5. Copy the Client ID and Client Secret into `backend/.env`

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/login` | Redirect to Google sign-in |
| GET | `/auth/callback` | OAuth2 callback |
| GET | `/auth/status` | Check authentication status |
| GET | `/emails/` | List emails (supports `query`, `label`, `max_results`) |
| GET | `/emails/{id}` | Get a single email (marks as read) |
| POST | `/emails/{id}/summarize` | AI summary + action items |
| POST | `/emails/{id}/classify` | AI category + priority |
| POST | `/emails/{id}/draft-reply` | AI reply draft |
| POST | `/emails/{id}/send-reply` | Generate draft and send |
| POST | `/emails/bulk-action` | Archive / delete / label multiple emails |
| POST | `/emails/ai/bulk-summarize` | Summarize a filtered set of emails |

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI secret key |
| `GOOGLE_CLIENT_ID` | Google OAuth2 client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth2 client secret |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL (default: `http://localhost:8000/auth/callback`) |
| `SECRET_KEY` | Session signing secret — change this in production! |
| `CORS_ORIGINS` | JSON list of allowed origins (default: `["http://localhost:3000"]`) |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend base URL (default: `http://localhost:8000`) |
