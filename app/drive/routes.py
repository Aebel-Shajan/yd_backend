from google.oauth2.credentials import Credentials
from fastapi import APIRouter, Depends, HTTPException, Request, status
from googleapiclient.discovery import build

from app.auth.services import get_current_user_credentials


router = APIRouter()


@router.get("/files")
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