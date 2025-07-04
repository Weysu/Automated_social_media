"""
subtitle.py
Subtitle and transcript generation utilities for video processing.
- Generate subtitles using Whisper
- Add subtitles to video using ffmpeg
- Split SRT and transcript files for video segments
- Utility functions for SRT parsing and splitting
"""
import whisper
import subprocess
import re
from typing import List
from datetime import timedelta

def format_time(t):
    '''Format seconds to SRT time string.'''
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:02}:{m:02}:{s:06.3f}".replace('.', ',')

def group_words_func(words):
    '''Group determiners and short words with the next word for better subtitle segmentation.'''
    group_words = {
        "a", "an", "the", "of", "to", "in", "on", "at", "by", "for", "with", "and", "or", "but",
        "my", "your", "his", "her", "its", "our", "their", "this", "that", "these", "those",
        "some", "any", "each", "every", "no", "one", "two"
    }
    grouped = []
    i = 0
    n = len(words)
    while i < n:
        word = words[i]
        if word.lower() in group_words and i + 1 < n:
            grouped.append(f"{word} {words[i+1]}")
            i += 2
        else:
            grouped.append(word)
            i += 1
    return grouped

def generate_subtitles(
    video_path,
    transcript_path="transcript.txt",
    srt_path="subtitles.srt"
):
    '''
    Generate subtitles and transcript from a video file using Whisper.
    Returns: (transcript_path, srt_path)
    '''
    model = whisper.load_model("base")
    result = model.transcribe(video_path, word_timestamps=True)
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(result["text"])
    segments = result["segments"]
    with open(srt_path, "w", encoding="utf-8") as f:
        idx = 1
        for seg in segments:
            start = seg['start']
            end = seg['end']
            text = seg['text'].strip()
            words = text.split()
            n = len(words)
            if n == 0:
                continue
            seg_duration = end - start
            grouped = group_words_func(words)
            group_n = len(grouped)
            group_duration = seg_duration / group_n if group_n else 0
            for j, chunk in enumerate(grouped):
                chunk_start = start + j * group_duration
                chunk_end = min(start + (j + 1) * group_duration, end)
                f.write(f"{idx}\n{format_time(chunk_start)} --> {format_time(chunk_end)}\n{chunk}\n\n")
                idx += 1
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
    '''
    Add SRT subtitles to a video using ffmpeg.
    '''
    sub_filter = f"subtitles={srt_path}:force_style='Fontsize={FONT_SIZE},MarginV={MARGIN_V},OutlineColour={BorderColour},BorderStyle=0,PrimaryColour={Coulour},FontName={FontName},Alignement={ALIGN}'"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", sub_filter,
        "-c:a", "copy",
        output_video
    ])
    return output_video

def parse_srt_time(srt_time: str) -> float:
    '''Parse SRT time string to seconds.'''
    h, m, rest = srt_time.split(':')
    s, ms = rest.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def get_split_points_from_srt(srt_path: str, min_duration: float = 60.0) -> List[float]:
    '''
    Get split points (in seconds) from SRT file based on sentence ends and minimum duration.
    '''
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
            continue
        _, end_str = time_range.split(' --> ')
        end_sec = parse_srt_time(end_str)
        if end_sec - last_split >= min_duration:
            split_points.append(end_sec)
            last_split = end_sec
    return split_points

def slice_srt(srt_path, out_path, start_time, end_time):
    '''Extract SRT entries within [start_time, end_time] and write to out_path.'''
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
    '''Extract transcript lines for the segment using the SRT as reference.'''
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
