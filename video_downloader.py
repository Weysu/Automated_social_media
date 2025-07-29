"""
video_downloader.py
Video download utilities for YouTube and satisfying background videos.
- Download trending YouTube videos
- Download random satisfying videos
- Utility for random date generation
"""

import requests
import os
from yt_dlp import YoutubeDL
import random
from datetime import datetime, timedelta
import configparser

config = configparser.ConfigParser()
config.read('credential/youtube_credential.ini')
YOUTUBE_API_KEY = config.get('youtube', 'api_key')

def get_trending_video_url():
    '''Get the URL of a trending YouTube video.'''
    url = (
        "https://www.googleapis.com/youtube/v3/videos"
        "?part=snippet"
        "&chart=mostPopular"
        "&maxResults=1"
        "&regionCode=US" #Région du monde pas langue
        f"&key={YOUTUBE_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    if "items" not in data or len(data["items"]) == 0:
        raise Exception("Aucune vidéo retournée. Vérifie la clé API et les quotas.")
    video_id = data["items"][0]["id"]
    return f"https://www.youtube.com/watch?v={video_id}"

def random_published_after(days_back=90):
    '''Generate a random publishedAfter date string for YouTube API.'''
    delta_days = random.randint(0, days_back)
    date = datetime.utcnow() - timedelta(days=delta_days)
    return date.strftime("%Y-%m-%dT00:00:00Z")

def get_satisfying_video_url():
    '''Get a random satisfying video URL from YouTube.'''
    subjects = [
        "kinetic sand", "slime", "soap cutting", 
        "hydraulic press", "asmr cooking", "shaving foam"
    ]
    styles = [
        "satisfying", "asmr", "relaxing", "compilation"
    ]
    subject = random.choice(subjects)
    style = random.choice(styles)
    query = f"{subject} {style}"
    published_after = random_published_after(90)
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&maxResults=10&order=viewCount"
        f"&q={requests.utils.quote(query)}"
        f"&regionCode=FR&videoDuration=medium"
        f"&publishedAfter={published_after}"
        f"&key={YOUTUBE_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    if "items" not in data or len(data["items"]) == 0:
        raise Exception("Aucune vidéo trouvée. Vérifie les paramètres ou la clé API.")
    video = random.choice(data["items"])
    video_id = video["id"]["videoId"]
    return f"https://www.youtube.com/watch?v={video_id}"

def download_video(video_url, outdir="downloads/video"):
    '''Download a video from YouTube using yt_dlp.'''
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, "%(title).50s.%(ext)s")
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
        'quiet': False,
        'noplaylist': True,
        'merge_output_format': 'mp4'
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info_dict)
        filename = filename.replace(".webm", ".mp4")
        return filename

