import os
import pickle
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_credentials(
    client_secret_path: str = "client_secret.json",
    token_path: str = "token.pickle"
):
    creds = None
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secret_path):
                raise FileNotFoundError(f"Client secret not found at {client_secret_path}")
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_path,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return creds


def is_authenticated(
    token_path: str = "token.pickle"
) -> bool:
    if not os.path.exists(token_path):
        return False

    with open(token_path, "rb") as token:
        creds = pickle.load(token)

    return creds is not None and creds.valid


def upload_video_real(
    video_path: str,
    title: str,
    description: str,
    tags: Optional[list[str]] = None,
    category_id: str = "22",
    privacy_status: str = "public",
    publish_at: Optional[str] = None,
    client_secret_path: str = "client_secret.json",
    token_path: str = "token.pickle"
) -> str:
    if not os.path.exists(video_path):
        raise FileNotFoundError("Video file not found!")

    creds = get_credentials(client_secret_path=client_secret_path, token_path=token_path)
    youtube = build("youtube", "v3", credentials=creds)

    status = {"privacyStatus": privacy_status}
    if publish_at:
        status = {"privacyStatus": "private", "publishAt": publish_at}

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or ["AI", "Automation", "YouTube"],
                "categoryId": category_id
            },
            "status": status
        },
        media_body=MediaFileUpload(video_path)
    )

    response = request.execute()
    return f"https://youtube.com/watch?v={response['id']}"