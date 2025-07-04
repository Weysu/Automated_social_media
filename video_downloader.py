import requests
import os
from yt_dlp import YoutubeDL
import random
from datetime import datetime, timedelta
import configparser


config = configparser.ConfigParser()
config.read('youtube_credential.ini')
YOUTUBE_API_KEY = config.get('youtube', 'api_key')

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

# Génère une date aléatoire dans les X derniers jours
def random_published_after(days_back=90):
    delta_days = random.randint(0, days_back)
    date = datetime.utcnow() - timedelta(days=delta_days)
    return date.strftime("%Y-%m-%dT00:00:00Z")

def get_satisfying_video_url():
    # Attention : les vidéos peuvent varier en qualité
    subjects = [
        "kinetic sand", "slime", "soap cutting", 
        "hydraulic press", "asmr cooking", "shaving foam"
    ]
    styles = [
        "satisfying", "asmr", "relaxing", "compilation"
    ]

    # Construction de la requête dynamique
    subject = random.choice(subjects)
    style = random.choice(styles)
    query = f"{subject} {style}"
    published_after = random_published_after(90)  # 90 derniers jours

    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&maxResults=10&order=viewCount"
        f"&q={requests.utils.quote(query)}"
        f"&regionCode=FR&videoDuration=medium"
        f"&publishedAfter={published_after}"
        f"&key={YOUTUBE_API_KEY}"
    )

    print(f"[INFO] Query utilisée : {query}")
    print(f"[INFO] Date filtre : {published_after}")
    print(f"[INFO] Requête complète : {url}")

    response = requests.get(url)
    data = response.json()

    if "items" not in data or len(data["items"]) == 0:
        raise Exception("Aucune vidéo trouvée. Vérifie les paramètres ou la clé API.")

    # Sélection aléatoire
    video = random.choice(data["items"])
    video_id = video["id"]["videoId"]

    print(f"[INFO] Vidéo sélectionnée : {video_id}")
    return f"https://www.youtube.com/watch?v={video_id}"


def download_video(video_url, outdir="downloads/video"):  # outdir param par défaut
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "%(title).50s.%(ext)s")

    ydl_opts = {
        'format': 'mp4', # for way bettter quality : 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        'outtmpl': output_path,
        'quiet': False,
        'noplaylist': True,
        'merge_output_format': 'mp4'
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        filename = filename.replace(".webm", ".mp4")  # Juste au cas où
        return filename

