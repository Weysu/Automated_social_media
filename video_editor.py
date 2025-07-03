# youtube_to_tiktok_bot/video_editor.py
import subprocess
from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips
import os

def split_video(path):
    clip = VideoFileClip(path)
    clips = []
    for i in range(0, int(clip.duration), 60):
        subclip = clip.subclip(i, min(i+60, clip.duration))
        out_name = f"clips/clip_{i//60}.mp4"
        subclip.write_videofile(out_name, codec="libx264", audio_codec="aac")
        clips.append(out_name)
    return clips


def edit_video(main_clip_path, satisfying_clip_path, output_path, start=0, duration=60):
    # Charger les clips
    main_clip = VideoFileClip(main_clip_path).subclip(start, start + duration)
    satisfying_clip = VideoFileClip(satisfying_clip_path).subclip(0, 60)  # 1 min max

    # Paramètres du format vertical (téléphone)
    width = 1080
    height = 1920
    half_height = height // 2

    # Redimensionner les clips pour tenir chacun dans la moitié verticale
    main_clip_resized = main_clip.resize(width=width, height=half_height)
    satisfying_clip_resized = satisfying_clip.resize(width=width, height=half_height)

    # Positionner clips : main en haut, satisfying en bas
    main_clip_pos = main_clip_resized.set_position(("center", "top"))
    satisfying_clip_pos = satisfying_clip_resized.set_position(("center", half_height))

    # Création du composite final
    final_clip = CompositeVideoClip(
        [main_clip_pos, satisfying_clip_pos],
        size=(width, height)
    )

    # Exporter la vidéo
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")


def merge_videos(video_paths, output_path):
    """Assemble une liste de vidéos en une seule vidéo continue."""
    clips = [VideoFileClip(p) for p in video_paths]
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    for c in clips:
        c.close()
    final_clip.close()
    return output_path

def edit_video_blur_background(input_path, output_path, duration=60):
    """
    Crée une vidéo verticale (9:16) avec un vrai flou de fond (via ffmpeg)
    et un crop carré centré en premier plan.
    Ajoute ending.mp4 à la fin de la vidéo finale.
    """
    width = 1080
    height = 1920
    square_size = width
    blurred_path = "temp_blurred.mp4"
    temp_final_path = "temp_final_with_blur.mp4"

    # Générer le fond flouté avec ffmpeg
    ffmpeg_blur_command = [
        "ffmpeg",
        "-y",  # overwrite
        "-i", input_path,
        "-t", str(duration),
        "-vf", "gblur=sigma=20,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-an",  # no audio
        blurred_path
    ]
    subprocess.run(ffmpeg_blur_command, check=True)

    # Charger les clips
    base_clip = VideoFileClip(input_path).subclip(0, duration)
    blurred_clip = VideoFileClip(blurred_path)

    # Crop 1:1 centré
    min_side = min(base_clip.w, base_clip.h)
    x_center = base_clip.w // 2
    y_center = base_clip.h // 2
    x1 = x_center - square_size // 2
    y1 = y_center - square_size // 2
    x2 = x1 + square_size
    y2 = y1 + square_size

    square_clip = (
        base_clip.crop(x1=max(0, x1), y1=max(0, y1), x2=min(base_clip.w, x2), y2=min(base_clip.h, y2))
        .resize((square_size, square_size))
        .set_position(("center", (height - square_size) // 2))
    )

    # Composer final
    final_clip = CompositeVideoClip([blurred_clip.set_position((0, 0)), square_clip], size=(width, height))
    final_clip.write_videofile(temp_final_path, codec="libx264", audio_codec="aac")

    # Ajouter ending.mp4 à la fin
    ending_path = r"downloads\video\ending.mp4"
    merge_videos([temp_final_path, ending_path], output_path)

    # Cleanup
    base_clip.close()
    blurred_clip.close()
    square_clip.close()
    final_clip.close()
    os.remove(blurred_path)
    os.remove(temp_final_path)

    return output_path