import whisper
import subprocess
import re

def add_subtitles_to_video(
    video_path,
    output_video="final_video_with_subs.mp4",
    transcript_path="transcript.txt",
    srt_path="subtitles.srt",
    FONT_SIZE=12,  # Increase for bigger text
    MARGIN_V=60,   # Distance from bottom (in pixels)
    ALIGN='center',  # Options: 'left', 'center', 'right'
    BorderColour='00000000',  # Black border
    Coulour='FFFFFF00',  # White text
    FontName='Arial'  # Font name
):
    
    # Load the Whisper model (choose "base", "small", "medium", or "large")
    model = whisper.load_model("base")
    # Step 1: Transcribe with word-level timestamps for finer segments
    result = model.transcribe(video_path, word_timestamps=True)
    # Step 2: Save plain text transcript
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(result["text"])
    # Step 3: Optional - Save SRT file for subtitles
    segments = result["segments"]
    # Ensure each subtitle is split by punctuation
    with open(srt_path, "w", encoding="utf-8") as f:
        idx = 1
        for seg in segments:
            start = seg['start']
            end = seg['end']
            text = seg['text'].strip()
            def format_time(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = t % 60
                return f"{h:02}:{m:02}:{s:06.3f}".replace('.', ',')
            # Split text by punctuation (., !, ?)
            chunks = re.split(r'(?<=[.!?]) +', text)
            n = len(chunks)
            if n == 0:
                continue
            seg_duration = end - start
            chunk_duration = seg_duration / n
            for i, chunk in enumerate(chunks):
                chunk = chunk.strip()
                if not chunk:
                    continue
                chunk_start = start + i * chunk_duration
                chunk_end = min(start + (i + 1) * chunk_duration, end)
                f.write(f"{idx}\n{format_time(chunk_start)} --> {format_time(chunk_end)}\n{chunk}\n\n")
                idx += 1

    print("✅ Transcription and subtitles done.")
    # FFmpeg subtitles filter styling
    sub_filter = f"subtitles={srt_path}:force_style='Fontsize={FONT_SIZE},MarginV={MARGIN_V},BorderColour={BorderColour},BorderStyle=0,Coulour={Coulour},FontName={FontName},align={ALIGN},BackColour=None'"
    print("🎥 Gravure des sous-titres dans la vidéo...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", sub_filter,
        "-c:a", "copy",
        output_video
    ])
    print(f"✅ Vidéo générée : {output_video}")
