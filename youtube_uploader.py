"""
youtube_uploader.py
YouTube video uploader using the YouTube Data API v3.
- Authenticate with OAuth2
- Upload videos with metadata
- Save and refresh credentials
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
from google.auth.transport.requests import Request
from configparser import ConfigParser
import json
import tempfile

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def get_youtube_config():
    '''Read YouTube API credentials from config file.'''
    config = ConfigParser()
    config.read(r'credential/youtube_credential.ini')
    return config['youtube']


def authenticate_youtube():
    '''
    Authenticate and return a YouTube API client.
    Handles token refresh and OAuth2 flow.
    '''
    credentials = None
    token_path = r'credential/token_youtube.pkl'
    config = get_youtube_config()
    client_secret_dict = {
        "installed": {
            "client_id": config.get('client_id'),
            "project_id": config.get('project_id'),
            "auth_uri": config.get('auth_uri'),
            "token_uri": config.get('token_uri'),
            "auth_provider_x509_cert_url": config.get('auth_provider_x509_cert_url'),
            "client_secret": config.get('client_secret'),
            "redirect_uris": [config.get('redirect_uris')]
        }
    }
    with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.json') as tmp:
        json.dump(client_secret_dict, tmp)
        tmp.flush()
        client_secret_path = tmp.name

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token_file:
            credentials = pickle.load(token_file)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
        credentials = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token_file:
            pickle.dump(credentials, token_file)

    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube


def upload_video(youtube, file_path, title, description, tags=None, category_id='22', privacy_status='private'):
    '''
    Upload a video to YouTube with metadata.
    '''
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or [],
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/*')
    request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading: {int(status.progress() * 100)}%")

    print(f"Upload complete! Video ID: {response['id']}")
    return response['id']

if __name__ == '__main__':
    yt = authenticate_youtube()
    upload_video(
        yt,
        file_path=r'C:\Users\MathéoCunchon\Documents\Project\output\video_sub\final_blured_1_with_subs.mp4',
        title='Test Upload from Python',
        description='This video was uploaded using Python and the YouTube API.',
        tags=['python', 'upload', 'youtube']
    )
