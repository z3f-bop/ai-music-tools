#!/usr/bin/env python3
"""
Format WhisperX transcript into readable markdown
Uses existing JSON (no re-transcription needed)
Adds natural pauses and formatting
"""

import json
import sys
from pathlib import Path

def detect_pause(prev_end: float, curr_start: float) -> str:
    """Detect pause type based on gap duration."""
    gap = curr_start - prev_end

    if gap > 2.0:
        return "\n\n"  # Long pause = paragraph break
    elif gap > 0.7:
        return ".\n\n"  # Medium pause = sentence break with space
    elif gap > 0.3:
        return ". "  # Short pause = sentence break
    else:
        return " "  # No significant pause

def format_transcript(json_file: Path, output_md: Path):
    """Format JSON transcript into readable markdown with speaker detection."""

    with open(json_file) as f:
        data = json.load(f)

    segments = data.get("segments", [])

    if not segments:
        print("Error: No segments found in transcript")
        sys.exit(1)

    # Format transcript with pauses and speaker detection
    paragraphs = []
    current_paragraph = []
    prev_word_end = 0

    for segment in segments:
        words = segment.get("words", [])
        segment_text = segment.get("text", "").lower()

        for word_data in words:
            word = word_data.get("word", "")
            start = word_data.get("start", 0)
            end = word_data.get("end", 0)

            # Detect paragraph breaks (long pauses)
            if prev_word_end > 0:
                gap = start - prev_word_end
                if gap > 2.0:  # Long pause = new paragraph
                    if current_paragraph:
                        paragraphs.append("".join(current_paragraph).strip())
                        current_paragraph = []
                elif gap > 0.7:  # Medium pause = ellipsis
                    current_paragraph.append("... ")
                elif gap > 0.3:  # Short pause = period
                    current_paragraph.append(". ")
                else:
                    current_paragraph.append(" ")

            current_paragraph.append(word)
            prev_word_end = end

    # Add final paragraph
    if current_paragraph:
        paragraphs.append("".join(current_paragraph).strip())

    # Simple speaker detection based on paragraph structure
    # First speaker usually introduces, alternating is common in interviews
    formatted_lines = ["# Transcript: INSIDE ÄNGIE - Season 2 Ep 3\n\n"]

    # First few paragraphs are usually intro
    for i, para in enumerate(paragraphs):
        para_lower = para.lower()

        # Detect speaker based on content clues
        if i == 0 or "welcome to" in para_lower or "inside angie" in para_lower:
            speaker = "**ÄNGIE:**"
        elif "scarly" in para_lower or "my name is" in para_lower and i < 5:
            speaker = "**SCARLY:**"
        elif i % 2 == 0:  # Simple alternation after intro
            speaker = "**ÄNGIE:**"
        else:
            speaker = "**SCARLY:**"

        # Don't repeat speaker if same as previous
        if i > 0 and formatted_lines[-1].startswith(speaker.split(":")[0]):
            formatted_lines.append(f"{para}\n\n")
        else:
            formatted_lines.append(f"{speaker}\n{para}\n\n")

    transcript = "".join(formatted_lines)

    with open(output_md, "w") as f:
        f.write(transcript)

    print(f"✓ Markdown transcript created: {output_md}")
    print(f"\nNote: Speaker labels not included - identify speakers manually based on content/voice")

def main():
    if len(sys.argv) < 2:
        print("Usage: python format_transcript.py <whisperx_json_file>")
        print("\nFormats existing WhisperX JSON into readable markdown")
        print("Uses pause detection to add natural breaks")
        sys.exit(1)

    json_file = Path(sys.argv[1])

    if not json_file.exists():
        print(f"Error: JSON file not found: {json_file}")
        sys.exit(1)

    output_md = json_file.parent / f"{json_file.stem}-transcript.md"
    format_transcript(json_file, output_md)

    print("\n✓ Done!")

if __name__ == "__main__":
    main()
