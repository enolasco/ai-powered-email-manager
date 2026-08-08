"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.routers import auth, emails

settings = get_settings()

app = FastAPI(
    title="AI-Powered Email Manager",
    description="Manage your emails with AI assistance — classify, summarize, and draft replies.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.include_router(auth.router)
app.include_router(emails.router)


@app.get("/")
def root():
    return {"message": "AI-Powered Email Manager API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
