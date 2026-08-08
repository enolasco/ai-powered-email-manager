"""Auth router — handles Google OAuth2 flow."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.config import get_settings, Settings
from app.services.auth_service import build_flow, credentials_to_dict

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
def login(settings: Settings = Depends(get_settings)):
    """Redirect the user to Google's OAuth consent screen."""
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth credentials not configured")
    flow = build_flow(
        settings.google_client_id,
        settings.google_client_secret,
        settings.google_redirect_uri,
    )
    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")
    return RedirectResponse(auth_url)


@router.get("/callback")
def callback(code: str, request: Request, settings: Settings = Depends(get_settings)):
    """Exchange the authorization code for tokens and store them in the session."""
    flow = build_flow(
        settings.google_client_id,
        settings.google_client_secret,
        settings.google_redirect_uri,
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials
    request.session["credentials"] = credentials_to_dict(credentials)
    return RedirectResponse(f"{settings.frontend_url}/inbox")


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}


@router.get("/status")
def status(request: Request):
    authenticated = "credentials" in request.session
    return {"authenticated": authenticated}
