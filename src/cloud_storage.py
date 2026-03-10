import os
import io
import re
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
_TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "Req_File", "token.json")

def _get_drive_service():
    """Authenticate with Drive API v3 using the user's OAuth token."""
    if not os.path.exists(_TOKEN_PATH):
        raise FileNotFoundError(
            f"{_TOKEN_PATH} not found. Follow the instructions to generate it first."
        )
    creds = Credentials.from_authorized_user_file(_TOKEN_PATH, _SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(_TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def _find_folder(service, name: str, parent_id: str) -> str | None:
    query = (
        f"name = '{name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' "
        f"and trashed = false "
        f"and '{parent_id}' in parents"
    )
    results = service.files().list(
        q=query, spaces="drive", fields="files(id)", pageSize=1,
    ).execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None


def _create_folder(service, name: str, parent_id: str) -> str:
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def _find_or_create_folder(service, name: str, parent_id: str) -> str:
    folder_id = _find_folder(service, name, parent_id)
    if folder_id:
        return folder_id
    return _create_folder(service, name, parent_id)


def upload_file(local_path: str, filename: str, folder_id: str = None) -> str:
    """
    Upload a local file to a specific Google Drive folder.
    Returns the Web View Link of the uploaded file.
    """
    service = _get_drive_service()
    if not service:
        return ""

    # Set mimeType based on extension. Default to generic stream if not .tex or .pdf
    mime_type = "text/plain" if filename.endswith(".tex") else "application/pdf"
    
    file_metadata = {
        "name": filename,
        "mimeType": mime_type,
    }
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)

    try:
        print(f"[cloud_storage] Uploading '{filename}' to folder '{folder_id}'...")
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()

        link = file.get("webViewLink")
        print(f"[cloud_storage] Upload success: {link}")
        return link

    except Exception as e:
        print(f"[cloud_storage] File upload failed: {e}")
        return ""

def upload_to_drive(file_path: str, company_name: str) -> str:
    """
    Creates a 'YYYY-MM/Company' folder structure in Google Drive and uploads the file.
    Returns the Web View Link of the uploaded file.
    """
    root_folder_id = os.environ.get("DRIVE_ROOT_FOLDER_ID")
    if not root_folder_id:
        print("[cloud_storage] DRIVE_ROOT_FOLDER_ID not set. Skipping Drive upload.")
        return ""
    
    service = _get_drive_service()
    if not service:
        return ""

    month_folder_name = datetime.now().strftime("%Y-%m")
    month_folder_id = _find_or_create_folder(service, month_folder_name, root_folder_id)
    company_folder_id = _find_or_create_folder(service, company_name, month_folder_id)
    
    file_name = os.path.basename(file_path)
    return upload_file(file_path, file_name, folder_id=company_folder_id)


def download_pdf_from_drive(web_view_link: str, output_path: str) -> str:
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", web_view_link)
    if not match:
        raise ValueError(f"Could not extract file_id from link: {web_view_link}")
    file_id = match.group(1)
    service = _get_drive_service()
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())
    return output_path
