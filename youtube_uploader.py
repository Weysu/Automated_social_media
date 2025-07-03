import os
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
from google.auth.transport.requests import Request

# Scopes required for uploading video
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def authenticate_youtube():
    credentials = None
    token_path = r'credential/token_youtube.pkl'

    # Charger les identifiants déjà existants
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token_file:
            credentials = pickle.load(token_file)

    # Rafraîchir les identifiants si expirés
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    # Sinon, lancer le flow OAuth
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(r'credential/client_secret.json', SCOPES)
        credentials = flow.run_local_server(port=0)
        # Sauvegarder les nouveaux identifiants
        with open(token_path, 'wb') as token_file:
            pickle.dump(credentials, token_file)

    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube


def upload_video(youtube, file_path, title, description, tags, category_id='22', privacy_status='private'):
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
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

# === Example usage ===
if __name__ == '__main__':
    yt = authenticate_youtube()
    upload_video(
        yt,
        file_path=r'C:\Users\MathéoCunchon\Documents\Project\output\video_sub\final_blured_1_with_subs.mp4',
        title='Test Upload from Python',
        description='This video was uploaded using Python and the YouTube API.',
        tags=['python', 'upload', 'youtube']
    )
