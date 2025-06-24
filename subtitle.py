import whisper
import os
import subprocess

# Load the Whisper model (choose "base", "small", "medium", or "large")
model = whisper.load_model("base")

# Your input video file
video_path = r"C:\Users\MathéoCunchon\OneDrive - Genvia SAS\Documents\Project\Transcribe\final_video_1.mp4"

# Step 1: Transcribe
result = model.transcribe(video_path)

# Step 2: Save plain text transcript
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])

# Step 3: Optional - Save SRT file for subtitles
segments = result["segments"]
with open("subtitles.srt", "w", encoding="utf-8") as f:
    for i, seg in enumerate(segments):
        # Format time
        start = seg['start']
        end = seg['end']
        text = seg['text'].strip()

        def format_time(t):
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = t % 60
            return f"{h:02}:{m:02}:{s:06.3f}".replace('.', ',')

        f.write(f"{i+1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")

print("✅ Transcription and subtitles done.")
srt_path = "subtitles.srt"
output_video = "final_video_with_subs.mp4"

# Subtitle style variables (modify as needed)
FONT_SIZE = 12  # Increase for bigger text
MARGIN_V = 60   # Distance from bottom (in pixels)
ALIGN = 'center'  # Options: 'left', 'center', 'right'
BorderColour = '00000000'  # Black border
Coulour = 'FFFFFF00'  # White text
FontName = 'Arial'  # Font name

print("🎥 Gravure des sous-titres dans la vidéo...")

# FFmpeg subtitles filter styling
# See: https://ffmpeg.org/ffmpeg-filters.html#subtitles for more options
sub_filter = f"subtitles={srt_path}:force_style='Fontsize={FONT_SIZE},Alignment=2,MarginV={MARGIN_V},BorderCoulour={BorderColour},BorderStyle=3,Coulour={Coulour},FontName={FontName}'"
subprocess.run([
    "ffmpeg", "-y",
    "-i", video_path,
    "-vf", sub_filter,
    "-c:a", "copy",
    output_video
])

print(f"✅ Vidéo générée : {output_video}")
