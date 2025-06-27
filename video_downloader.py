import requests
import os
from yt_dlp import YoutubeDL
import random

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
    video_id='LkJpNLIaeVk' # A changer pour tester avec une vidéo spécifique
    print (video_id)
    return f"https://www.youtube.com/watch?v={video_id}"


def get_satisfying_video_url():
    # Liste de requêtes satisfaisantes populaires
    queries = [
        "minecraft parkour satisfying",
        "subway surfers gameplay",
        "asmr soap cutting",
        "satisfying cutting compilation",
        "satisfying cooking short",
        "perfect loop animation",
        "pressure washing satisfying",
        "kinetic sand cutting",
        "slime asmr",
        "hydraulic press satisfying"
    ]

    # Choisir une requête aléatoire
    selected_query = random.choice(queries)

    # Construire l’URL d’appel à l’API YouTube
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&maxResults=1&type=video&order=viewCount"
        f"&q={requests.utils.quote(selected_query)}"
        f"&regionCode=FR&videoDuration=short&key={YOUTUBE_API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    # Gestion d’erreur si aucune vidéo n’est retournée
    if "items" not in data or len(data["items"]) == 0:
        raise Exception("Aucune vidéo retournée. Vérifie la clé API, les quotas ou la requête.")

    video_id = data["items"][0]["id"]["videoId"]
    print(f"[INFO] Query utilisée : {selected_query}")
    print(f"[INFO] Vidéo ID trouvée : {video_id}")
    
    return f"https://www.youtube.com/watch?v={video_id}"

def download_video(video_url, outdir="downloads/video"):  # outdir param par défaut
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "%(title).50s.%(ext)s")

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

