import io
from typing import Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe

def get_user_info(credentials: Credentials):
    service = build("oauth2", "v2", credentials=credentials)
    user_info = service.userinfo().get().execute()
    return user_info


def query_or_create_nested_folder(credentials: Credentials, folder_path:str):
    service = build("drive", "v3", credentials=credentials)
    folder_names = folder_path.strip("/").split("/")
    parent_id = None

    for folder_name in folder_names:
        # Build the query
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        # Search for the folder
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        items = results.get('files', [])

        if items:
            # Folder exists
            parent_id = items[0]['id']
        else:
            # Create the folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id] if parent_id else []
            }
            folder = service.files().create(body=file_metadata, fields='id').execute()
            parent_id = folder['id']

    return parent_id


def get_file_name_from_id(credentials: Credentials, file_id: str):
    # Get file metadata first to get the name
    drive_service = build("drive", "v3", credentials=credentials)
    file_metadata = drive_service.files().get(fileId=file_id).execute()
    filename = file_metadata["name"]
    return filename


def query_drive_file(
    credentials: Credentials, 
    name:str, 
    parent_id:Optional[str]=None
) -> Optional[str]:
    service = build("drive", "v3", credentials=credentials)
    query = f"name = '{name}' and trashed = false"
    if parent_id:
        query += f"and '{parent_id}' in parents"
        
    results = service.files().list(
        q=query,
        spaces='drive',
        fields="files(id)",
    ).execute()

    files = results.get('files', [])
    file_ids = [file["id"] for file in files]
    
    if len(file_ids) > 0:
        return file_ids[0]
    return None


def upload_or_overwrite(credentials: Credentials, file_path, file_name, parent_id):    
    service = build("drive", "v3", credentials=credentials)
    
    # Step 1: Check if file already exists
    existing_file_id = query_drive_file(credentials, file_name, parent_id)

    # Step 2: Prepare media and metadata
    media = MediaFileUpload(file_path, resumable=True) 
    file_metadata = {
        'name': file_name,
        'parents': [parent_id]
    }

    if existing_file_id:
        # Step 3A: Overwrite existing file
        updated = (
            service
            .files()
            .update(
                fileId=existing_file_id,
                media_body=media,
            )
            .execute()
        )
        print(f"✅ Overwritten file ID: {updated['id']}")
        return updated['id']
    else:
        # Step 3B: Upload new file
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"🆕 Uploaded new file ID: {uploaded['id']}")
        return uploaded['id']
    

def download_file(credentials: Credentials, file_id:str) -> io.BytesIO:
    drive_service = build("drive", "v3", credentials=credentials)
    # Download file
    request = drive_service.files().get_media(fileId=file_id)
    file_io = io.BytesIO()
    downloader = MediaIoBaseDownload(file_io, request)
    
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    file_io.seek(0)
    
    return file_io


def get_data_from_csv(
    credentials: Credentials, 
    csv_name: str, 
    year: int,
    date_col: str="date"
) -> Optional[dict]:
    """Returns a json response from a csv file on google drive.

    Args:
        credentials (Credentials): Google oauth2 credentials
        csv_name (str): Name of csv file in 'year-in-data/outputs' folder in google 
            drive.
        year (int): Year to filter on
        date_col (str, optional): Name of date column. Used because of errors when
            converting pandas date column to dict. Defaults to "date".

    Returns:
        Optional[dict]: Output json dict or None if csv file not found in drive.
    """
    output_folder_id = query_or_create_nested_folder(
        credentials, 
        "year-in-data/outputs"
    )
    data_file_id = query_drive_file(
        credentials, 
        name=csv_name, 
        parent_id=output_folder_id
    )
    data = None
    metadata = None
    if data_file_id:    
        file = download_file(credentials, data_file_id)
        df = pd.read_csv(file)
        # Ensure the date column is in datetime format 
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df[df['date'].dt.year == year]
        # Replace nan values
        df = df.fillna("")
        data  = df.to_dict(orient='records')
        metadata = df.dtypes.apply(lambda x: x.name).to_dict()
        print(metadata)

    return data, metadata

def create_or_update_sheet(
    credentials: Credentials,
    df: pd.DataFrame,
    worksheet_name: str,
    file_name: str,
    parent_id: str
):
    service = build("drive", "v3", credentials=credentials)
    existing_file_id = query_drive_file(credentials, file_name, parent_id)
    
    file_metadata = {
        'name': file_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [parent_id]
    }
    file_id = existing_file_id
    if not existing_file_id:
        uploaded = service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        print(f"🆕 Uploaded new sheet ID: {uploaded['id']}")
        file_id = uploaded['id']
    else:
        print(f"✅ Updating existing sheet ID: {existing_file_id}")

    write_df_to_sheet(
        credentials,
        df,
        spreadsheet_id=file_id,
        worksheet_name=worksheet_name
    )


def write_df_to_sheet(
    credentials: Credentials,
    df: pd.DataFrame, 
    spreadsheet_id: str, 
    worksheet_name: str, 
):
    """
    Creates a new Google Spreadsheet using Drive API and writes a DataFrame to it.

    Parameters:
        df (pd.DataFrame): Data to write.
        new_title (str): Title of the new Google Sheet.
        worksheet_name (str): Name of the worksheet/tab.
        creds_path (str): Path to service account credentials JSON.
    """

    # --- Step 2: Open and Write to It with gspread ---
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(spreadsheet_id)

    try:
        worksheet = sh.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sh.add_worksheet(title=worksheet_name, rows="100", cols="20")

    worksheet.clear()
    set_with_dataframe(worksheet, df)


def get_data_from_sheet(
    credentials: Credentials,
    worksheet_name: str,
    file_name: str,
    parent_id: str,
    year: Optional[int] = None
) -> tuple[dict, dict]:
    existing_file_id = query_drive_file(credentials, file_name, parent_id)
    if existing_file_id is None:
        raise ValueError(f"Sheet with file_name={file_name} could not be found in drive!")
    
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(existing_file_id)
    worksheet = sh.worksheet(worksheet_name)

    # Get all data
    data = worksheet.get_all_records()
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if year:
        df = df[df['date'].dt.year == year]
    
    # Replace nan values
    df = df.fillna("")
    data  = df.to_dict(orient='records')
    metadata = df.dtypes.apply(lambda x: x.name).to_dict()
    return data, metadata
