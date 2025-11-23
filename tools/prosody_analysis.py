#!/usr/bin/env python3
"""
Prosody Analysis Tool for AI DJ Tools

Analyzes vocal delivery patterns from audio files using:
- WhisperX for transcription + word-level timestamps
- Parselmouth (Praat) for pitch, intensity, pauses

Use cases:
- Vocal delivery analysis in music tracks
- Rap flow/timing extraction
- Speech rhythm research
- Spoken word performance analysis

Migrated from bop-os to ai-dj-tools (November 23, 2025)
"""

import sys
import json
import whisperx
import torch
import parselmouth
from parselmouth.praat import call
from pathlib import Path
import numpy as np
from pydub import AudioSegment
import tempfile


def transcribe_audio(audio_path: str, output_path: str = None, language: str = "fr"):
    """
    Transcribe audio file to text with word-level timestamps using WhisperX.

    Args:
        audio_path: Path to audio/video file
        output_path: Path for JSON output (optional, defaults to audio_path + .json)
        language: Language code (default: "fr" for French, use "en" for English)

    Returns:
        dict: Transcription results with word-level timing
    """
    audio_path = Path(audio_path)

    if output_path is None:
        output_path = audio_path.with_suffix('.json')
    else:
        output_path = Path(output_path)

    print(f"🎧 Transcribing: {audio_path.name}")
    print(f"📝 Output: {output_path}")

    # Check device - use CPU for Mac (faster-whisper backend)
    device = "cpu"
    print(f"🖥️  Using device: {device}")

    # Load model - base is fast enough for Mac, large-v3 is too slow on CPU
    print("🔄 Loading Whisper model...")
    model = whisperx.load_model(
        "base",  # Fast model for Mac - use "large-v3" on GPU if needed
        device=device,
        compute_type="int8"  # CPU uses int8 for efficiency
    )

    # Load and transcribe audio
    print("🎵 Loading audio...")
    audio = whisperx.load_audio(str(audio_path))

    print("✍️  Transcribing (this may take a minute)...")
    result = model.transcribe(
        audio,
        language=language,
        batch_size=16
    )

    # Align for word-level timestamps
    print("🎯 Aligning word-level timestamps...")
    align_model, metadata = whisperx.load_align_model(
        language_code=language,
        device="cpu"  # Force CPU for alignment too
    )
    result = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio,
        device
    )

    # Structure output
    output = {
        "metadata": {
            "source_file": str(audio_path),
            "language": language,
            "device_used": device,
            "model": "whisper-large-v3"
        },
        "segments": result["segments"]
    }

    # Save JSON
    print(f"💾 Saving to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("✅ Done!")
    print(f"📊 Transcribed {len(result['segments'])} segments")

    return output


def analyze_prosody(audio_path: str, transcription_path: str = None, output_path: str = None):
    """
    Analyze prosody features from audio file using Parselmouth (Praat).

    Extracts:
    - Pitch contour (fundamental frequency)
    - Intensity (loudness)
    - Speaking rate (if transcription provided)
    - Pause patterns

    Args:
        audio_path: Path to audio/video file
        transcription_path: Path to JSON transcription with timestamps (optional)
        output_path: Path for JSON output (optional, defaults to audio_path + -prosody.json)

    Returns:
        dict: Prosody analysis results
    """
    audio_path = Path(audio_path)

    if output_path is None:
        output_path = audio_path.parent / f"{audio_path.stem}-prosody.json"
    else:
        output_path = Path(output_path)

    print(f"🎵 Analyzing prosody: {audio_path.name}")
    print(f"📝 Output: {output_path}")

    # Convert to WAV if needed (Parselmouth only supports WAV/AIFF natively)
    temp_wav = None
    if audio_path.suffix.lower() not in ['.wav', '.aiff', '.aifc']:
        print(f"🔄 Converting {audio_path.suffix} to WAV for Praat compatibility...")
        audio = AudioSegment.from_file(str(audio_path))
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        audio.export(temp_wav.name, format='wav')
        audio_for_analysis = temp_wav.name
        print(f"   Temporary WAV: {temp_wav.name}")
    else:
        audio_for_analysis = str(audio_path)

    # Load audio with Parselmouth
    print("🔊 Loading audio...")
    sound = parselmouth.Sound(audio_for_analysis)

    # Extract pitch (fundamental frequency)
    print("🎼 Extracting pitch contour...")
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    pitch_times = pitch.xs()

    # Remove unvoiced frames (pitch = 0)
    voiced_mask = pitch_values > 0
    voiced_pitch = pitch_values[voiced_mask]

    pitch_stats = {
        "mean_hz": float(np.mean(voiced_pitch)) if len(voiced_pitch) > 0 else 0,
        "median_hz": float(np.median(voiced_pitch)) if len(voiced_pitch) > 0 else 0,
        "min_hz": float(np.min(voiced_pitch)) if len(voiced_pitch) > 0 else 0,
        "max_hz": float(np.max(voiced_pitch)) if len(voiced_pitch) > 0 else 0,
        "std_hz": float(np.std(voiced_pitch)) if len(voiced_pitch) > 0 else 0,
    }

    # Extract intensity (loudness)
    print("📢 Extracting intensity...")
    intensity = sound.to_intensity()
    intensity_values = intensity.values[0]
    intensity_times = intensity.xs()

    intensity_stats = {
        "mean_db": float(np.mean(intensity_values)),
        "median_db": float(np.median(intensity_values)),
        "min_db": float(np.min(intensity_values)),
        "max_db": float(np.max(intensity_values)),
        "std_db": float(np.std(intensity_values)),
    }

    # Calculate speaking rate (if we have transcription)
    speaking_rate = None
    if transcription_path:
        transcription_path = Path(transcription_path)
        print(f"📄 Loading transcription: {transcription_path.name}")
        with open(transcription_path, 'r', encoding='utf-8') as f:
            transcription = json.load(f)

        # Count words and calculate rate
        total_words = sum(len(seg.get('words', [])) for seg in transcription.get('segments', []))
        duration_seconds = sound.duration
        duration_minutes = duration_seconds / 60

        speaking_rate = {
            "total_words": total_words,
            "duration_seconds": duration_seconds,
            "words_per_minute": total_words / duration_minutes if duration_minutes > 0 else 0,
        }
        print(f"⚡ Speaking rate: {speaking_rate['words_per_minute']:.1f} words/min")

    # Detect pauses (segments with low intensity)
    print("⏸️  Detecting pauses...")
    pause_threshold_db = np.percentile(intensity_values, 25)  # Bottom 25% intensity
    pauses = []
    in_pause = False
    pause_start = None

    for i, (time, db) in enumerate(zip(intensity_times, intensity_values)):
        if db < pause_threshold_db:
            if not in_pause:
                pause_start = time
                in_pause = True
        else:
            if in_pause:
                pause_duration = time - pause_start
                if pause_duration > 0.15:  # Only count pauses > 150ms
                    pauses.append({
                        "start": float(pause_start),
                        "end": float(time),
                        "duration": float(pause_duration)
                    })
                in_pause = False

    pause_stats = {
        "total_pauses": len(pauses),
        "total_pause_time": sum(p['duration'] for p in pauses),
        "avg_pause_duration": np.mean([p['duration'] for p in pauses]) if pauses else 0,
        "pauses": pauses[:20]  # Only include first 20 pauses in output
    }

    # Build output structure
    output = {
        "metadata": {
            "source_file": str(audio_path),
            "duration_seconds": sound.duration,
            "transcription_file": str(transcription_path) if transcription_path else None,
        },
        "pitch": pitch_stats,
        "intensity": intensity_stats,
        "speaking_rate": speaking_rate,
        "pauses": pause_stats,
    }

    # Save JSON
    print(f"💾 Saving to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Cleanup temporary WAV file
    if temp_wav:
        import os
        os.unlink(temp_wav.name)
        print(f"🗑️  Cleaned up temporary WAV")

    print("✅ Prosody analysis complete!")
    print(f"\n📊 Summary:")
    print(f"   Pitch: {pitch_stats['mean_hz']:.1f} Hz (mean), {pitch_stats['std_hz']:.1f} Hz variation")
    print(f"   Intensity: {intensity_stats['mean_db']:.1f} dB (mean)")
    if speaking_rate:
        print(f"   Speaking rate: {speaking_rate['words_per_minute']:.1f} words/min")
    print(f"   Pauses: {pause_stats['total_pauses']} pauses, {pause_stats['total_pause_time']:.1f}s total")

    return output


def analyze_complete(audio_path: str, language: str = "fr"):
    """
    Complete prosody analysis workflow: transcribe + analyze.

    Args:
        audio_path: Path to audio file
        language: Language code for transcription (default: "fr")

    Returns:
        tuple: (transcription_result, prosody_result)
    """
    audio_path = Path(audio_path)

    # Step 1: Transcribe
    transcription_output = audio_path.with_suffix('.json')
    transcription = transcribe_audio(str(audio_path), str(transcription_output), language=language)

    # Step 2: Analyze prosody
    prosody_output = audio_path.parent / f"{audio_path.stem}-prosody.json"
    prosody = analyze_prosody(str(audio_path), str(transcription_output), str(prosody_output))

    print("\n🎉 Complete analysis finished!")
    print(f"   Transcription: {transcription_output}")
    print(f"   Prosody: {prosody_output}")

    return (transcription, prosody)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
Prosody Analysis Tool for AI DJ Tools

Usage:
  # Complete workflow (transcribe + analyze)
  python prosody_analysis.py <audio_file> [language]

  # Just transcribe
  python prosody_analysis.py transcribe <audio_file> [output_file] [language]

  # Just analyze prosody
  python prosody_analysis.py analyze <audio_file> [transcription_json] [output_file]

Examples:
  python prosody_analysis.py angie_interview.mp3
  python prosody_analysis.py angie_interview.mp3 en
  python prosody_analysis.py transcribe vocal_sample.wav output.json en
  python prosody_analysis.py analyze vocal_sample.wav output.json prosody.json
""")
        sys.exit(1)

    command = sys.argv[1]

    if command == "transcribe":
        # Transcribe mode
        audio_path = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        language = sys.argv[4] if len(sys.argv) > 4 else "fr"
        transcribe_audio(audio_path, output_path, language)

    elif command == "analyze":
        # Analyze mode
        audio_path = sys.argv[2]
        transcription_path = sys.argv[3] if len(sys.argv) > 3 else None
        output_path = sys.argv[4] if len(sys.argv) > 4 else None
        analyze_prosody(audio_path, transcription_path, output_path)

    else:
        # Complete workflow mode (command is actually the audio file)
        audio_path = command
        language = sys.argv[2] if len(sys.argv) > 2 else "fr"
        analyze_complete(audio_path, language)
