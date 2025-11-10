#!/usr/bin/env python3
"""
Test DJ deck monitor visualization (A/Mix/B vertical stack)
"""

from dj_tools import DJToolkit
from pathlib import Path

def test_deck_monitor():
    """Test deck monitor with two tracks at different crossfader positions"""

    dj = DJToolkit()

    # Pick two tracks with different vibes
    track_a = "music/Geoff-Bremner-Audio_Synthwave Instrumental Track_676438.mp3"
    track_b = "music/LolaMoore_Lo-Fi Chill for Reflective Moments_767570.mp3"

    for track in [track_a, track_b]:
        if not Path(track).exists():
            print(f"❌ Track not found: {track}")
            return

    print("🎵 Testing DJ Deck Monitor Visualization")
    print("="*60)

    # Analyze both tracks
    print("\n1️⃣  Analyzing tracks...")
    analyses = dj.analyze_tracks([track_a, track_b])

    if "error" in analyses:
        print(f"❌ Analysis failed: {analyses['error']}")
        return

    analysis_a = analyses['analyses'][0]
    analysis_b = analyses['analyses'][1]

    print(f"\n   DECK A: {Path(track_a).name}")
    print(f"   BPM: {analysis_a['tempo']:.1f}")
    print(f"   Key: {analysis_a['estimated_key']}")
    print(f"   Mood: {analysis_a['mood']}")

    print(f"\n   DECK B: {Path(track_b).name}")
    print(f"   BPM: {analysis_b['tempo']:.1f}")
    print(f"   Key: {analysis_b['estimated_key']}")
    print(f"   Mood: {analysis_b['mood']}")

    # Test different crossfader positions
    crossfader_positions = [
        (0.0, "Full A"),
        (0.35, "Mostly A"),
        (0.5, "50/50 Mix"),
        (0.65, "Mostly B"),
        (1.0, "Full B")
    ]

    print(f"\n2️⃣  Generating deck monitor visualizations...")

    for crossfader, label in crossfader_positions:
        print(f"\n   📊 {label} (crossfader={crossfader})...")

        # Set playheads to midpoint of each track for visualization
        playhead_a = analysis_a['duration'] / 2
        playhead_b = analysis_b['duration'] / 2

        result = dj.create_deck_monitor(
            track_a_path=track_a,
            track_b_path=track_b,
            bpm_a=analysis_a['tempo'],
            bpm_b=analysis_b['tempo'],
            crossfader=crossfader,
            playhead_a_seconds=playhead_a,
            playhead_b_seconds=playhead_b,
            output_path=f"temp/deck_monitor_{label.lower().replace(' ', '_').replace('/', '-')}.png"
        )

        if "output_path" in result:
            print(f"      ✅ Saved: {result['output_path']}")
        else:
            print(f"      ❌ Failed to generate")

    print("\n" + "="*60)
    print("✅ Test complete! Check temp/ directory for deck monitor views.")
    print("\nEach visualization shows:")
    print("  - Top row: Deck A spectrogram (red tint)")
    print("  - Middle row: Mix output (green tint) with crossfader overlay")
    print("  - Bottom row: Deck B spectrogram (blue tint)")
    print("  - White dashed line: Current playhead position")
    print("  - Yellow line on mix: Crossfader position")

if __name__ == "__main__":
    test_deck_monitor()
