#!/usr/bin/env python3
"""
Quick test of beat-quantized spectrogram generation
"""

from dj_tools import DJToolkit
from pathlib import Path

def test_beat_spectrogram():
    """Test spectrogram generation on a sample track"""

    dj = DJToolkit()

    # Pick a test track - synthwave should have clear beat structure
    test_track = "music/Geoff-Bremner-Audio_Synthwave Instrumental Track_676438.mp3"

    if not Path(test_track).exists():
        print(f"❌ Test track not found: {test_track}")
        return

    print(f"🎵 Testing beat spectrogram on: {Path(test_track).name}")
    print("="*60)

    # Step 1: Analyze track to get BPM
    print("\n1️⃣  Analyzing track...")
    analysis = dj.analyze_tracks([test_track])

    if "error" in analysis:
        print(f"❌ Analysis failed: {analysis['error']}")
        return

    track_analysis = analysis['analyses'][0]
    bpm = track_analysis['tempo']
    duration = track_analysis['duration']

    print(f"   ✅ BPM: {bpm:.1f}")
    print(f"   ✅ Duration: {duration:.1f}s")
    print(f"   ✅ Key: {track_analysis['estimated_key']}")
    print(f"   ✅ Mood: {track_analysis['mood']}")
    print(f"   ✅ Energy: {track_analysis['energy_level']}")

    # Step 2: Generate beat spectrograms at different resolutions
    resolutions = [
        (0.25, "16th notes"),
        (0.5, "8th notes"),
        (1.0, "quarter notes")
    ]

    print(f"\n2️⃣  Generating beat spectrograms...")

    for beats_per_div, name in resolutions:
        print(f"\n   📊 {name} resolution (beats_per_division={beats_per_div})...")

        result = dj.generate_beat_spectrogram(
            file_path=test_track,
            bpm=bpm,
            beats_per_division=beats_per_div,
            output_path=f"temp/test_spec_{name.replace(' ', '_')}"
        )

        if "error" in result:
            print(f"      ❌ Failed: {result['error']}")
            continue

        print(f"      ✅ Generated {result['num_divisions']} divisions")
        print(f"      ✅ Each division = {result['seconds_per_division']:.3f}s")
        print(f"      ✅ Spectrogram shape: {result['spectrogram_shape']}")

        if "image_path" in result:
            print(f"      ✅ Image saved: {result['image_path']}")
        if "data_path" in result:
            print(f"      ✅ Data saved: {result['data_path']}")

    print("\n" + "="*60)
    print("✅ Test complete! Check temp/ directory for spectrograms.")
    print("\nVisualization shows:")
    print("  - X-axis: Musical time (bars)")
    print("  - Y-axis: Frequency spectrum (20Hz-20kHz, logarithmic)")
    print("  - Color: Amplitude in dB (magma colormap)")
    print("  - Each pixel column = one beat division")

if __name__ == "__main__":
    test_beat_spectrogram()
