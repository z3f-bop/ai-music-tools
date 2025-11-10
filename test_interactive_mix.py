#!/usr/bin/env python3
"""
Test interactive mixing workflow
"""

from tools.interactive_mixer import InteractiveMixer
from pathlib import Path

def test_interactive_session():
    """Test full interactive mixing session"""

    # Pick 3 tracks for a mini-set
    tracks = [
        "music/Geoff-Bremner-Audio_Synthwave Instrumental Track_676438.mp3",
        "music/LolaMoore_Lo-Fi Chill for Reflective Moments_767570.mp3",
        "music/SondreDrakensson_Do Robots Get Bored_530217.mp3"
    ]

    # Verify tracks exist
    for track in tracks:
        if not Path(track).exists():
            print(f"❌ Track not found: {track}")
            return

    print("🎵 INTERACTIVE DJ SESSION TEST")
    print("="*60)

    mixer = InteractiveMixer()

    # Start session
    session = mixer.start_session(tracks, session_name="test_mini_set")

    if "error" in session:
        print(f"❌ Session failed: {session['error']}")
        return

    # Transition 1: Track 1 → Track 2
    print("\n" + "="*60)
    print("TRANSITION 1: Building the first blend")
    print("="*60)

    options_1 = mixer.get_transition_options(session, track_a_index=0, track_b_index=1)

    print("\n🤖 Auto-selecting option 2 (4-bar crossfade) for test...")
    result_1 = mixer.execute_transition(session, 0, 1, choice=2)

    if "error" in result_1:
        print(f"❌ Transition failed: {result_1['error']}")
        return

    # Transition 2: Track 2 → Track 3
    print("\n" + "="*60)
    print("TRANSITION 2: Completing the set")
    print("="*60)

    options_2 = mixer.get_transition_options(session, track_a_index=1, track_b_index=2)

    print("\n🤖 Auto-selecting option 1 (first recommended) for test...")
    result_2 = mixer.execute_transition(session, 1, 2, choice=1)

    if "error" in result_2:
        print(f"❌ Transition failed: {result_2['error']}")
        return

    # Save session
    session_file = mixer.save_session(session)

    print("\n" + "="*60)
    print("✅ INTERACTIVE SESSION COMPLETE")
    print("="*60)
    print(f"\n📁 Generated files:")
    print(f"   - {result_1['mix_path']}")
    print(f"   - {result_2['mix_path']}")
    print(f"   - {session_file}")

    print(f"\n📊 Session summary:")
    print(f"   - Tracks mixed: {len(tracks)}")
    print(f"   - Transitions made: {len(session['mix_decisions'])}")
    print(f"   - Decisions logged: {len(mixer.session_log)}")

    print("\n💡 In real use:")
    print("   - You'd see transition options")
    print("   - Choose based on spectrograms + analysis")
    print("   - Make artistic decisions at each point")
    print("   - Build the set iteratively")

if __name__ == "__main__":
    test_interactive_session()
