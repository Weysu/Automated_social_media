# youtube_to_tiktok_bot/video_editor.py

from moviepy import VideoFileClip, CompositeVideoClip
import os

def split_video(path):
    clip = VideoFileClip(path)
    clips = []
    for i in range(0, int(clip.duration), 60):
        subclip = clip.subclipped(i, min(i+60, clip.duration))
        out_name = f"clips/clip_{i//60}.mp4"
        subclip.write_videofile(out_name, codec="libx264", audio_codec="aac")
        clips.append(out_name)
    return clips


def edit_video(main_clip_path, satisfying_clip_path, output_path, start=0, duration=60):
    # Charger les clips
    main_clip = VideoFileClip(main_clip_path).subclipped(start, start + duration)
    satisfying_clip = VideoFileClip(satisfying_clip_path).subclipped(0, 60)  # 1 min max

    # Paramètres du format vertical (téléphone)
    width = 1080
    height = 1920
    half_height = height // 2

    # Redimensionner les clips pour tenir chacun dans la moitié verticale
    main_clip_resized = main_clip.resized(width=width, height=half_height)
    satisfying_clip_resized = satisfying_clip.resized(width=width, height=half_height)

    # Positionner clips : main en haut, satisfying en bas
    main_clip_pos = main_clip_resized.with_position(("center", "top"))
    satisfying_clip_pos = satisfying_clip_resized.with_position(("center", half_height))

    # Création du composite final
    final_clip = CompositeVideoClip(
        [main_clip_pos, satisfying_clip_pos],
        size=(width, height)
    )

    # Exporter la vidéo
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")