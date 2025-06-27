# subtitle.py
import whisper
import subprocess
import re
from typing import List
from datetime import timedelta

def generate_subtitles(
    video_path,
    transcript_path="transcript.txt",
    srt_path="subtitles.srt"
):
    """
    Generate subtitles from a video file using Whisper.
    
    Args:
        video_path (str): Path to the input video file
        transcript_path (str): Path to save the transcript text file
        srt_path (str): Path to save the SRT subtitle file
        
    Returns:
        tuple: (transcript_path, srt_path) - paths to the generated files
    """
    # Load Whisper model and transcribe
    model = whisper.load_model("base")
    result = model.transcribe(video_path, word_timestamps=True)

    # Save transcript
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    # Generate SRT file
    segments = result["segments"]
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

            # Split text into chunks by punctuation
            chunks = re.split(r'(?<=[,.!?]) +', text)
            smart_chunks = []
            for chunk in chunks:
                words = chunk.strip().split()
                if len(words) > 6:
                    # Further split into sub-chunks of 3-4 words, but avoid chunks <2 words except last
                    i = 0
                    while i < len(words):
                        # If last chunk and less than 2 words, merge with previous
                        if i + 4 >= len(words) and len(words) - i < 2 and smart_chunks:
                            smart_chunks[-1] += ' ' + ' '.join(words[i:])
                            break
                        smart_chunks.append(' '.join(words[i:i+4]))
                        i += 4
                else:
                    smart_chunks.append(chunk.strip())
            # Remove empty and 1-word chunks except if it's the only chunk
            smart_chunks = [c for c in smart_chunks if len(c.split()) > 1 or len(smart_chunks) == 1]
            n = len(smart_chunks)
            if n == 0:
                continue
            seg_duration = end - start
            chunk_duration = seg_duration / n
            for i, chunk in enumerate(smart_chunks):
                chunk = chunk.strip()
                if not chunk:
                    continue
                chunk_start = start + i * chunk_duration
                chunk_end = min(start + (i + 1) * chunk_duration, end)
                f.write(f"{idx}\n{format_time(chunk_start)} --> {format_time(chunk_end)}\n{chunk}\n\n")
                idx += 1

    print("✅ Transcription and subtitles generated.")
    return transcript_path, srt_path


def add_subtitles_to_video(
    video_path,
    srt_path,
    output_video="final_video_with_subs.mp4",
    FONT_SIZE=8,
    MARGIN_V=90,
    ALIGN='center',
    BorderColour='00000000',
    Coulour='FFFFFF00',
    FontName='Arial'
):
    """
    Add existing subtitles to a video file using FFmpeg.
    
    Args:
        video_path (str): Path to the input video file
        srt_path (str): Path to the SRT subtitle file
        output_video (str): Path for the output video with subtitles
        FONT_SIZE (int): Font size for subtitles
        MARGIN_V (int): Vertical margin for subtitles
        ALIGN (str): Text alignment ('center', 'left', 'right')
        BorderColour (str): Border color in hex format
        Coulour (str): Text color in hex format
        FontName (str): Font name for subtitles
        
    Returns:
        str: Path to the output video file
    """
    sub_filter = f"subtitles={srt_path}:force_style='Fontsize={FONT_SIZE},MarginV={MARGIN_V},BorderColour={BorderColour},BorderStyle=0,Coulour={Coulour},FontName={FontName},align={ALIGN},BackColour=None'"
    
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", sub_filter,
        "-c:a", "copy",
        output_video
    ])
    
    print(f"✅ Video with subtitles generated: {output_video}")
    return output_video

def parse_srt_time(srt_time: str) -> float:
    # srt_time: "HH:MM:SS,mmm"
    h, m, rest = srt_time.split(':')
    s, ms = rest.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def get_split_points_from_srt(srt_path: str, min_duration: float = 60.0) -> List[float]:
    split_points = []
    last_split = 0.0

    with open(srt_path, encoding="utf-8") as f:
        entries = f.read().split('\n\n')

    for entry in entries:
        lines = entry.strip().split('\n')
        if len(lines) < 3:
            continue

        time_range = lines[1]
        text = " ".join(lines[2:]).strip()

        if not re.search(r'[.!?]\s*$', text):
            continue  # Not a sentence end

        _, end_str = time_range.split(' --> ')
        end_sec = parse_srt_time(end_str)

        if end_sec - last_split >= min_duration:
            split_points.append(end_sec)
            last_split = end_sec

    return split_points

def slice_srt(srt_path, out_path, start_time, end_time):
    """Extract only the SRT entries within [start_time, end_time] and write to out_path."""
    with open(srt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    entries = []
    entry = []
    for line in lines:
        if line.strip() == '':
            if entry:
                entries.append(entry)
                entry = []
        else:
            entry.append(line)
    if entry:
        entries.append(entry)
    def parse_srt_time(srt_time):
        h, m, rest = srt_time.split(':')
        s, ms = rest.split(',')
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    filtered = []
    idx = 1
    for entry in entries:
        if len(entry) < 2:
            continue
        time_line = entry[1].strip()
        if '-->' not in time_line:
            continue
        start_str, end_str = [x.strip() for x in time_line.split('-->')]
        s = parse_srt_time(start_str)
        e = parse_srt_time(end_str)
        if e > start_time and s < end_time:
            # Adjust times to segment
            new_s = max(s, start_time) - start_time
            new_e = min(e, end_time) - start_time
            def fmt(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = t % 60
                return f"{h:02}:{m:02}:{s:06.3f}".replace('.', ',')
            filtered.append([
                f"{idx}\n",
                f"{fmt(new_s)} --> {fmt(new_e)}\n"
            ] + entry[2:])
            idx += 1
    with open(out_path, 'w', encoding='utf-8') as f:
        for entry in filtered:
            for line in entry:
                f.write(line)
            f.write('\n')

def slice_transcript(transcript_path, out_path, start_time, end_time, srt_path):
    """Extract only the transcript lines for the segment using the SRT as reference."""
    # This is a simple approach: for each SRT entry in the segment, collect its text.
    with open(srt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    texts = []
    for i, line in enumerate(lines):
        if i > 1 and lines[i-2].strip().isdigit() and '-->' in lines[i-1]:
            texts.append(line.strip())
    with open(out_path, 'w', encoding='utf-8') as f:
        for t in texts:
            if t:
                f.write(t + '\n')
