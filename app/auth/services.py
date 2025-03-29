from fastapi import HTTPException, Request, status
from google.oauth2.credentials import Credentials



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