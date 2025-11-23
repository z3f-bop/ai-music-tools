#!/usr/bin/env python3
"""
Transcript Formatter with Speaker Diarization
Generates readable markdown transcripts from WhisperX JSON with:
- Speaker identification
- Natural pause formatting (line breaks, em dashes)
- Prosody-aware punctuation
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def run_whisperx_with_diarization(audio_file: Path, output_dir: Path) -> Path:
    """Run WhisperX with speaker diarization enabled."""

    print(f"Running WhisperX with diarization on: {audio_file.name}")
    print("This may take several minutes...")

    # Build command as single string for bash execution
    # Use HUGGING_FACE_API_KEY from .zshrc as HF_TOKEN for diarization
    cmd = f"""source /Users/olivier/Projects/bop-os/.venv-skills/bin/activate && \
source ~/.zshrc && \
HF_TOKEN=$HUGGING_FACE_API_KEY whisperx "{audio_file}" \
  --model base \
  --language en \
  --diarize \
  --min_speakers 2 \
  --max_speakers 2 \
  --compute_type int8 \
  --device cpu \
  --output_format json \
  --output_dir "{output_dir}" """

    # Run via bash to handle activation
    result = subprocess.run(
        cmd,
        shell=True,
        executable="/bin/bash",
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error running WhisperX: {result.stderr}")
        sys.exit(1)

    # Find output JSON
    base_name = audio_file.stem
    json_file = output_dir / f"{base_name}.json"

    if not json_file.exists():
        print(f"Error: Expected output file not found: {json_file}")
        sys.exit(1)

    print(f"✓ Transcription complete: {json_file}")
    return json_file

def detect_pause(prev_end: float, curr_start: float, threshold: float = 0.5) -> str:
    """Detect pause type based on gap duration."""
    gap = curr_start - prev_end

    if gap > 2.0:
        return "\n\n"  # Long pause = paragraph break
    elif gap > threshold:
        return ".\n"  # Medium pause = sentence break
    else:
        return " "  # Short gap = normal word spacing

def format_transcript_with_speakers(json_file: Path, output_md: Path):
    """Format JSON transcript into readable markdown with speakers."""

    with open(json_file) as f:
        data = json.load(f)

    segments = data.get("segments", [])

    if not segments:
        print("Error: No segments found in transcript")
        sys.exit(1)

    # Check if diarization worked
    has_speakers = "speaker" in segments[0]

    if not has_speakers:
        print("Warning: No speaker labels found - diarization may have failed")

    # Format transcript
    lines = []
    current_speaker = None
    current_paragraph = []
    prev_word_end = 0

    for segment in segments:
        speaker = segment.get("speaker", "UNKNOWN")
        words = segment.get("words", [])

        # Speaker change = new paragraph
        if speaker != current_speaker:
            if current_paragraph:
                lines.append("".join(current_paragraph))
                current_paragraph = []

            lines.append(f"\n**{speaker}:**\n")
            current_speaker = speaker
            prev_word_end = 0

        # Process words with pause detection
        for word_data in words:
            word = word_data.get("word", "")
            start = word_data.get("start", 0)
            end = word_data.get("end", 0)

            # Add pause formatting if needed
            if prev_word_end > 0:
                pause = detect_pause(prev_word_end, start)
                if pause in ["\n\n", ".\n"]:
                    current_paragraph.append(pause)

            current_paragraph.append(word)
            prev_word_end = end

    # Add final paragraph
    if current_paragraph:
        lines.append("".join(current_paragraph))

    # Write markdown
    transcript = "".join(lines)

    with open(output_md, "w") as f:
        f.write(f"# Transcript: {json_file.stem}\n\n")
        f.write(transcript)

    print(f"✓ Markdown transcript created: {output_md}")

    # Print speaker summary
    speakers = {seg.get("speaker", "UNKNOWN") for seg in segments}
    print(f"\nSpeakers detected: {', '.join(sorted(speakers))}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python transcript_with_speakers.py <audio_file>")
        print("\nGenerates:")
        print("  1. JSON transcript with speaker labels (via WhisperX)")
        print("  2. Readable markdown with pauses and speaker identification")
        sys.exit(1)

    audio_file = Path(sys.argv[1])

    if not audio_file.exists():
        print(f"Error: Audio file not found: {audio_file}")
        sys.exit(1)

    output_dir = audio_file.parent

    # Step 1: Run WhisperX with diarization
    json_file = run_whisperx_with_diarization(audio_file, output_dir)

    # Step 2: Format as readable markdown
    output_md = output_dir / f"{audio_file.stem}-transcript.md"
    format_transcript_with_speakers(json_file, output_md)

    print("\n✓ Done!")
    print(f"\nOutputs:")
    print(f"  JSON: {json_file}")
    print(f"  Markdown: {output_md}")

if __name__ == "__main__":
    main()
