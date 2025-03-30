from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from app.auth.services import credentials_to_dict
from app.config import Config


router = APIRouter()

@router.get("/login")
async def google_login(request: Request):
    """Initiate Google OAuth2 login flow."""
    
    if request.session.get("credentials"):
        return {"message": "already authenticated"}
    flow = Flow.from_client_secrets_file(
        Config.CLIENT_SECRETS_FILE,
        scopes=Config.SCOPES,
        redirect_uri='http://localhost:8000/auth/callback'
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    
    # Store state in session to prevent CSRF
    request.session['oauth_state'] = state
    
    return RedirectResponse(url=authorization_url)

@router.get("/logout")
async def logout(request: Request):
    """Logout and clear session."""
    # Clear the session
    request.session.clear()
    return {"message": "Logged out successfully"}

@router.get("/callback")
async def google_callback(request: Request, code: str, state: str):
    """Handle Google OAuth2 callback and store credentials in session."""
    # Validate state to prevent CSRF
    if state != request.session.get('oauth_state'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid state parameter"
        )
    
    flow = Flow.from_client_secrets_file(
        Config.CLIENT_SECRETS_FILE,
        scopes=Config.SCOPES,
        state=state,
        redirect_uri='http://localhost:8000/auth/callback'
    )
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Get user info
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    
    # Store credentials in session
    request.session['credentials'] = credentials_to_dict(credentials)
    request.session['user_email'] = user_info['email']
    
    return {"message": "Authentication successful", "user_email": user_info['email']}
