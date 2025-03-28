from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.sessions import SessionMiddleware
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from typing import Optional
import os
import secrets
from fastapi.responses import RedirectResponse


# Secure session configuration
SECRET_KEY = secrets.token_hex(32)  # Cryptographically secure random key

# OAuth2 configuration
CLIENT_SECRETS_FILE = "client_secret.json"  # Downloaded from Google Cloud Console
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


app = FastAPI(title="Google OAuth2 Drive API Application")

# Add secure session middleware
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY, 
    # session_cookie=True,
    # max_age=86400,  # 24 hours
    # same_site="lax",
    # https_only=True
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def credentials_to_dict(credentials):
    """Convert Credentials to a dictionary for session storage."""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def dict_to_credentials(token_dict):
    """Convert session dictionary back to Credentials object."""
    if not token_dict:
        return None
    return Credentials(
        token=token_dict['token'],
        refresh_token=token_dict['refresh_token'],
        token_uri=token_dict['token_uri'],
        client_id=token_dict['client_id'],
        client_secret=token_dict['client_secret'],
        scopes=token_dict['scopes']
    )

@app.get("/login")
async def google_login(request: Request):
    """Initiate Google OAuth2 login flow."""
    
    if request.session.get("credentials"):
        return {"message": "already authenticated"}
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost:8000/callback'
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    
    # Store state in session to prevent CSRF
    request.session['oauth_state'] = state
    
    return RedirectResponse(url=authorization_url)

@app.get("/callback")
async def google_callback(request: Request, code: str, state: str):
    """Handle Google OAuth2 callback and store credentials in session."""
    # Validate state to prevent CSRF
    if state != request.session.get('oauth_state'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid state parameter"
        )
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri='http://localhost:8000/callback'
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

def get_current_user_credentials(request:Request):
    """Validate and retrieve user credentials from session."""
    # Retrieve credentials from session
    credentials_dict = request.session.get('credentials')
    
    if not credentials_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        # Convert dictionary back to Credentials object
        credentials = dict_to_credentials(credentials_dict)
        
        # Optional: Add token refresh logic here
        return credentials
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@app.get("/drive/files")
async def list_drive_files(request: Request, credentials: Credentials = Depends(get_current_user_credentials)):
    """List files in Google Drive for the authenticated user."""
    try:
        drive_service = build('drive', 'v3', credentials=credentials)
        results = drive_service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        files = results.get('files', [])
        
        return {"files": files}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error accessing Google Drive: {str(e)}"
        )

@app.get("/logout")
async def logout(request):
    """Logout and clear session."""
    # Clear the session
    request.session.clear()
    return {"message": "Logged out successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)