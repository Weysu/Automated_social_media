
import requests
import os
from yt_dlp import YoutubeDL

YOUTUBE_API_KEY = "AIzaSyDig6Ed6UIRe6uKYJ0ckle7VX1PxEZ8ncE"  # Remplace par ta clé API

def get_trending_video_url():
    url = (
        "https://www.googleapis.com/youtube/v3/videos"
        "?part=snippet"
        "&chart=mostPopular"
        "&maxResults=1"
        "&regionCode=FR"
        f"&key={YOUTUBE_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    # gestion d'erreur si mauvais retour
    if "items" not in data or len(data["items"]) == 0:
        raise Exception("Aucune vidéo retournée. Vérifie la clé API et les quotas.")

    video_id = data["items"][0]["id"]
    print (video_id)
    return f"https://www.youtube.com/watch?v={video_id}"


def download_trending_video():
    video_url = get_trending_video_url()
    os.makedirs("downloads", exist_ok=True)
    output_path = os.path.join("downloads", "%(title).50s.%(ext)s")

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
        'quiet': False,
        'noplaylist': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        filename = filename.replace(".webm", ".mp4")  # Juste au cas où
        return filename

