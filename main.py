# main.py
from video_downloader import download_trending_video
from video_editor import edit_video
from moviepy.editor import VideoFileClip
from subtitle import generate_subtitles, add_subtitles_to_video, get_split_points_from_srt, slice_srt, slice_transcript
import os
import shutil

def main():
    print("▶ Téléchargement de la vidéo tendance...")
    video_path = download_trending_video()
    satisfying_path = "assets/satisfying.mp4"
    if not os.path.exists(satisfying_path):
        raise FileNotFoundError("❌ La vidéo satisfaisante est introuvable : assets/satisfying.mp4")

    os.makedirs("output/video", exist_ok=True)
    os.makedirs("output/video_sub", exist_ok=True)
    os.makedirs("output/script", exist_ok=True)

    # Step 1: Generate subtitles and transcript for whole video
    print("📝 Génération des sous-titres complets...")
    full_srt = "output/script/full_subtitles.srt"
    full_transcript = "output/script/full_transcript.txt"
    
    # Use the separated function to generate subtitles only
    generate_subtitles(
        video_path=video_path,
        transcript_path=full_transcript,
        srt_path=full_srt
    )

    # Step 2: Extract split points
    print("🔍 Analyse des sous-titres pour déterminer les points de découpe...")
    split_points = get_split_points_from_srt(full_srt, min_duration=60.0)
    if not split_points:
        raise ValueError("❌ Aucun point de découpe trouvé avec des phrases de plus de 60s.")

    print(f"📌 Points de découpe trouvés: {[round(p, 2) for p in split_points]}")

    # Step 3: Split and edit video based on dynamic points
    start_time = 0.0
    for idx, end_time in enumerate(split_points):
        duration = end_time - start_time
        part_output = f"output/video/final_video_{idx+1}.mp4"
        print(f"✂️ Clip {idx+1} : {round(start_time, 2)}s -> {round(end_time, 2)}s")

        # Edit video without subtitles first
        edit_video(
            main_clip_path=video_path,
            satisfying_clip_path=satisfying_path,
            output_path=part_output,
            start=start_time,
            duration=duration
        )

        # Slice SRT and transcript for this segment
        segment_srt = f"output/script/subtitles_{idx+1}.srt"
        segment_transcript = f"output/script/transcript_{idx+1}.txt"
        slice_srt(full_srt, segment_srt, start_time, end_time)
        slice_transcript(full_transcript, segment_transcript, start_time, end_time, segment_srt)

        # Add subtitles to the edited video clip
        subtitled_output = f"output/video_sub/final_video_{idx+1}_with_subs.mp4"
        add_subtitles_to_video( #Param for subtitles (some are not working)
            video_path=part_output,
            srt_path=segment_srt,
            output_video=subtitled_output,
            FONT_SIZE=16,
            MARGIN_V=120,
            ALIGN='5',
            BorderColour='00000000',
            Coulour='00FFFF00',
            FontName='Arial'
        )
        start_time = end_time

    print("✅ Tous les clips ont été traités !")

if __name__ == "__main__":
    main()