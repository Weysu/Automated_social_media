# youtube_to_tiktok_bot/main.py

from video_downloader import download_trending_video
from video_editor import edit_video
# from tiktok_uploader import upload_to_tiktok
from moviepy.editor import VideoFileClip
from subtitle import add_subtitles_to_video
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

        part_output = f"output/video/final_video_{i+1}.mp4"
        print(f"🧩 Génération clip {i+1} ({start_time}s à {end_time}s)...")

        edit_video(
            main_clip_path=video_path,
            satisfying_clip_path=satisfying_path,
            output_path=part_output,
            start=start_time,
            duration=60
        )

        # Add subtitles to the generated video
        subtitled_output = f"output/video_sub/final_video_{i+1}_with_subs.mp4"
        transcript_path = f"output/script/transcript_{i+1}.txt"
        srt_path = f"output/script/subtitles_{i+1}.srt"
        add_subtitles_to_video(
            video_path=part_output,
            output_video=subtitled_output,
            transcript_path=transcript_path,
            srt_path=srt_path,
            FONT_SIZE=12  # Example: bigger text
        )

    print("✅ Tous les clips ont été postés !")

if __name__ == "__main__":
    main()
