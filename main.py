# main.py
from video_downloader import download_video, get_trending_video_url, get_satisfying_video_url
from video_editor import edit_video, merge_videos, edit_video_blur_background
from moviepy.editor import VideoFileClip
from subtitle import generate_subtitles, add_subtitles_to_video, get_split_points_from_srt, slice_srt, slice_transcript
import os
import shutil

def split_video():
    print("▶ Téléchargement de la vidéo principale...")
    trending_url = get_trending_video_url()
    video_path = download_video(trending_url, outdir="downloads/video")
    main_clip = VideoFileClip(video_path)
    main_duration = main_clip.duration
    print(f"Durée de la vidéo principale : {main_duration:.2f}s")

    # Télécharger des vidéos satisfaisantes jusqu'à atteindre la durée requise
    satisfying_dir = "downloads/satisfying"
    os.makedirs(satisfying_dir, exist_ok=True)
    satisfying_paths = []
    total_satisfying_duration = 0.0
    while total_satisfying_duration < main_duration:
        satisfying_url = get_satisfying_video_url()
        sat_path = download_video(satisfying_url, outdir=satisfying_dir)
        try:
            sat_clip = VideoFileClip(sat_path)
            satisfying_paths.append(sat_path)
            total_satisfying_duration += sat_clip.duration
            print(f"Ajoutée : {sat_path} ({sat_clip.duration:.2f}s), total = {total_satisfying_duration:.2f}s")
            sat_clip.close()
        except Exception as e:
            print(f"Erreur lors de la lecture de {sat_path} : {e}")
            continue

    # Fusionner toutes les vidéos satisfaisantes
    merged_satisfying = os.path.join(satisfying_dir, "merged_satisfying.mp4")
    merge_videos(satisfying_paths, merged_satisfying)
    print(f"Vidéo satisfaisante fusionnée : {merged_satisfying}")

    # Supprimer les vidéos individuelles
    for p in satisfying_paths:
        if os.path.exists(p):
            os.remove(p)

    # ...suite du pipeline...
    os.makedirs("output/video", exist_ok=True)
    os.makedirs("output/video_sub", exist_ok=True)
    os.makedirs("output/script", exist_ok=True)

    # Step 1: Generate subtitles and transcript for whole video
    print("📝 Génération des sous-titres complets...")
    full_srt = "output/script/full_subtitles.srt"
    full_transcript = "output/script/full_transcript.txt"
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

        # Extract subclips for this segment
        main_clip_segment = VideoFileClip(video_path).subclip(start_time, end_time)
        satisfying_clip_segment = VideoFileClip(merged_satisfying).subclip(start_time, end_time)
        main_clip_segment_path = f"output/video/main_segment_{idx+1}.mp4"
        satisfying_clip_segment_path = f"output/video/satisfying_segment_{idx+1}.mp4"
        main_clip_segment.write_videofile(main_clip_segment_path, codec="libx264", audio_codec="aac")
        satisfying_clip_segment.write_videofile(satisfying_clip_segment_path, codec="libx264", audio_codec="aac")
        main_clip_segment.close()
        satisfying_clip_segment.close()

        # Edit video with the corresponding satisfying segment
        edit_video(
            main_clip_path=main_clip_segment_path,
            satisfying_clip_path=satisfying_clip_segment_path,
            output_path=part_output,
            start=0,
            duration=duration
        )

        # Slice SRT and transcript for this segment
        segment_srt = f"output/script/subtitles_{idx+1}.srt"
        segment_transcript = f"output/script/transcript_{idx+1}.txt"
        slice_srt(full_srt, segment_srt, start_time, end_time)
        slice_transcript(full_transcript, segment_transcript, start_time, end_time, segment_srt)

        # Add subtitles to the edited video clip
        subtitled_output = f"output/video_sub/final_video_{idx+1}_with_subs.mp4"
        add_subtitles_to_video(
            video_path=part_output,
            srt_path=segment_srt,
            output_video=subtitled_output,
            FONT_SIZE=20,
            MARGIN_V=130,
            ALIGN='5',
            BorderColour='00000000',
            Coulour='&H0000FFFF',
            FontName='Arial'
        )
        start_time = end_time

    print("✅ Tous les clips ont été traités !")

def split_blured_video():
    """
    Découpe la vidéo principale en segments selon les sous-titres, applique l'effet flou + 1:1 centré à chaque segment,
    et ajoute les sous-titres comme dans split_video, mais sans vidéo de remplissage.
    """
    print("▶ Téléchargement de la vidéo principale...")
    trending_url = get_trending_video_url()
    video_path = download_video(trending_url, outdir="downloads/video")
    main_clip = VideoFileClip(video_path)
    main_duration = main_clip.duration
    print(f"Durée de la vidéo principale : {main_duration:.2f}s")

    os.makedirs("output/video", exist_ok=True)
    os.makedirs("output/video_sub", exist_ok=True)
    os.makedirs("output/script", exist_ok=True)

    # Générer sous-titres et transcript
    print("📝 Génération des sous-titres complets...")
    full_srt = "output/script/full_subtitles.srt"
    full_transcript = "output/script/full_transcript.txt"
    generate_subtitles(
        video_path=video_path,
        transcript_path=full_transcript,
        srt_path=full_srt
    )

    # Points de découpe
    print("🔍 Analyse des sous-titres pour déterminer les points de découpe...")
    split_points = get_split_points_from_srt(full_srt, min_duration=60.0)
    if not split_points:
        raise ValueError("❌ Aucun point de découpe trouvé avec des phrases de plus de 60s.")
    print(f"📌 Points de découpe trouvés: {[round(p, 2) for p in split_points]}")

    # Découpage et édition
    start_time = 0.0
    for idx, end_time in enumerate(split_points):
        duration = end_time - start_time
        part_output = f"output/video/final_blured_{idx+1}.mp4"
        print(f"✂️ Clip {idx+1} : {round(start_time, 2)}s -> {round(end_time, 2)}s")

        # Extraire le segment principal
        main_clip_segment = VideoFileClip(video_path).subclip(start_time, end_time)
        main_clip_segment_path = f"output/video/main_blured_segment_{idx+1}.mp4"
        main_clip_segment.write_videofile(main_clip_segment_path, codec="libx264", audio_codec="aac")
        main_clip_segment.close()

        # Appliquer l'effet flou + 1:1
        edit_video_blur_background(main_clip_segment_path, part_output, duration=duration)

        # Découper SRT et transcript
        segment_srt = f"output/script/subtitles_blured_{idx+1}.srt"
        segment_transcript = f"output/script/transcript_blured_{idx+1}.txt"
        slice_srt(full_srt, segment_srt, start_time, end_time)
        slice_transcript(full_transcript, segment_transcript, start_time, end_time, segment_srt)

        # Ajouter les sous-titres
        subtitled_output = f"output/video_sub/final_blured_{idx+1}_with_subs.mp4"
        add_subtitles_to_video(
            video_path=part_output,
            srt_path=segment_srt,
            output_video=subtitled_output,
            FONT_SIZE=20,
            MARGIN_V=60,
            ALIGN='5',
            BorderColour='00000000',
            Coulour='&H0000FFFF',
            FontName='Arial'
        )
        start_time = end_time

    print("✅ Tous les clips floutés ont été traités !")

if __name__ == "__main__":
    # split_video()  # Pour la version avec vidéos satisfaisantes
    split_blured_video()  # Pour la version floutée sans vidéos satisfaisantes