# youtube_to_tiktok_bot/main.py

from video_downloader import download_trending_video
from video_editor import edit_video
# from tiktok_uploader import upload_to_tiktok
from moviepy import VideoFileClip
import os

def main():
    print("▶ Téléchargement de la vidéo tendance...")
    video_path = download_trending_video()

    satisfying_path = "assets/satisfying.mp4"
    if not os.path.exists(satisfying_path):
        raise FileNotFoundError("❌ La vidéo satisfaisante est introuvable : assets/satisfying.mp4")

    os.makedirs("output", exist_ok=True)

    # Charger la vidéo principale pour en connaître la durée
    main_clip = VideoFileClip(video_path)
    total_duration = int(main_clip.duration)
    num_parts = total_duration // 60

    print(f"🎞️ Vidéo téléchargée : {total_duration}s (~{num_parts} clips de 1 min)")

    for i in range(num_parts):
        start_time = i * 60
        end_time = start_time + 60

        part_output = f"output/final_video_{i+1}.mp4"
        print(f"🧩 Génération clip {i+1} ({start_time}s à {end_time}s)...")

        edit_video(
            main_clip_path=video_path,
            satisfying_clip_path=satisfying_path,
            output_path=part_output,
            start=start_time,
            duration=60
        )

        caption = f"🎬 Partie {i+1} - Vidéo tendance + satisfying 🤩 #fyp #part{i+1}"
        print("🚀 Publication sur TikTok...")
        # upload_to_tiktok(part_output, caption)

    print("✅ Tous les clips ont été postés !")

if __name__ == "__main__":
    main()
