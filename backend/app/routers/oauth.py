"""
OAuth router for Google Calendar authentication
Allows each teacher to connect their own Google Calendar account
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json
import os

from app.core.database import get_db
from app.models.models import Teacher, AuthUser, AuthUserRole, AuthUserRole
from app.core.config import get_settings

router = APIRouter(prefix="/oauth", tags=["OAuth"])
settings = get_settings()

# OAuth scopes - must match what's configured in Google Cloud Console
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/meetings.space.readonly'
]

# OAuth configuration
CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [f"{settings.backend_url}/api/oauth/callback"]
    }
}


@router.get("/connect")
async def connect_google_calendar(
    teacher_email: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate Google Calendar OAuth flow for a teacher
    Returns authorization URL for frontend to redirect to
    """
    # First check AuthUser table (primary authentication)
    stmt_auth = select(AuthUser).where(AuthUser.email == teacher_email)
    result_auth = await db.execute(stmt_auth)
    auth_user = result_auth.scalars().first()
    
    if not auth_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify user is admin (only admin can connect shared Google Calendar)
    if auth_user.role != AuthUserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can connect Google Calendar for shared use")
    
    # Create OAuth flow
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=f"{settings.backend_url}/api/oauth/callback"
    )
    
    # Generate authorization URL with state
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state=teacher_email  # Pass teacher email as state
    )
    
    return {
        "authorization_url": authorization_url,
        "message": "Redirect user to this URL to authenticate"
    }


@router.get("/callback")
async def oauth_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle OAuth callback from Google
    Exchanges authorization code for access token and stores it
    """
    # Get authorization code and state from query params
    code = request.query_params.get('code')
    teacher_email = request.query_params.get('state')
    error = request.query_params.get('error')
    
    if error:
        # Redirect to frontend settings page with error
        return RedirectResponse(
            url=f"{settings.frontend_url}/dashboard/settings?oauth_error={error}"
        )
    
    if not code or not teacher_email:
        raise HTTPException(status_code=400, detail="Missing code or state")
    
    # Get teacher/tutor from AuthUser database
    stmt = select(AuthUser).where(AuthUser.email == teacher_email)
    result = await db.execute(stmt)
    auth_user = result.scalars().first()
    
    if not auth_user:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    if auth_user.role != AuthUserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can connect Google Calendar for shared use")
    
    try:
        # Exchange code for tokens
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=f"{settings.backend_url}/api/oauth/callback"
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Store credentials in database
        credentials_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Update auth_user with Google credentials
        update_stmt = (
            update(AuthUser)
            .where(AuthUser.email == teacher_email)
            .values(google_credentials=json.dumps(credentials_dict))
        )
        await db.execute(update_stmt)
        await db.commit()
        
        # Redirect to frontend settings page with success
        return RedirectResponse(
            url=f"{settings.frontend_url}/dashboard/settings?oauth_success=true"
        )
        
    except Exception as e:
        print(f"OAuth error: {str(e)}")
        return RedirectResponse(
            url=f"{settings.frontend_url}/dashboard/settings?oauth_error=authentication_failed"
        )


@router.get("/status/{teacher_email}")
async def get_oauth_status(
    teacher_email: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if teacher has connected Google Calendar
    """
    stmt = select(AuthUser).where(AuthUser.email == teacher_email)
    result = await db.execute(stmt)
    auth_user = result.scalars().first()
    
    if not auth_user:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    has_credentials = bool(auth_user.google_credentials)
    
    return {
        "connected": has_credentials,
        "email": teacher_email
    }


@router.post("/disconnect/{teacher_email}")
async def disconnect_google_calendar(
    teacher_email: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Disconnect teacher's Google Calendar
    """
    stmt = select(AuthUser).where(AuthUser.email == teacher_email)
    result = await db.execute(stmt)
    auth_user = result.scalars().first()
    
    if not auth_user:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Remove credentials
    update_stmt = (
        update(AuthUser)
        .where(AuthUser.email == teacher_email)
        .values(google_credentials=None)
    )
    await db.execute(update_stmt)
    await db.commit()
    
    return {"message": "Google Calendar disconnected successfully"}
