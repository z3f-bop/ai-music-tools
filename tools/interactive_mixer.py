"""
Interactive DJ Mixing Workflow
Artist makes decisions at each transition point based on analysis data
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
from dj_tools import DJToolkit


class InteractiveMixer:
    """
    Interactive mixing session where DJ makes artistic decisions
    at each transition point based on visual + technical analysis.
    """

    def __init__(self):
        self.dj = DJToolkit()
        self.session_log = []

    def start_session(self, track_paths: List[str], session_name: str = "mix_session") -> Dict:
        """
        Start interactive mixing session.

        Args:
            track_paths: List of audio file paths to mix
            session_name: Name for this session

        Returns:
            Session initialization data
        """
        print(f"🎵 Starting Interactive DJ Session: {session_name}")
        print("="*60)

        # Analyze all tracks
        print(f"\n1️⃣ Analyzing {len(track_paths)} tracks...")
        analyses_result = self.dj.analyze_tracks(track_paths)

        if "error" in analyses_result:
            return {"error": f"Analysis failed: {analyses_result['error']}"}

        analyses = analyses_result['analyses']

        # Show track overview
        print("\n📊 Track Analysis:")
        for i, (path, analysis) in enumerate(zip(track_paths, analyses), 1):
            print(f"\n  [{i}] {Path(path).name}")
            print(f"      BPM: {analysis['tempo']:.1f}")
            print(f"      Key: {analysis['estimated_key']}")
            print(f"      Energy: {analysis['energy_level']}")
            print(f"      Mood: {analysis['mood']}")
            print(f"      Duration: {analysis['duration']:.1f}s")

        # Initialize session state
        session = {
            "name": session_name,
            "tracks": track_paths,
            "analyses": analyses,
            "current_index": 0,
            "mix_decisions": [],
            "output_segments": []
        }

        self.session_log.append({
            "action": "session_start",
            "tracks": [Path(p).name for p in track_paths],
            "track_count": len(track_paths)
        })

        return session

    def get_transition_options(
        self,
        session: Dict,
        track_a_index: int,
        track_b_index: int
    ) -> Dict:
        """
        Present transition options between two tracks.

        Args:
            session: Current session state
            track_a_index: Index of outgoing track
            track_b_index: Index of incoming track

        Returns:
            Dict with transition options and recommendations
        """
        analysis_a = session['analyses'][track_a_index]
        analysis_b = session['analyses'][track_b_index]
        track_a_path = session['tracks'][track_a_index]
        track_b_path = session['tracks'][track_b_index]

        print(f"\n🎚️ Transition: Track {track_a_index+1} → Track {track_b_index+1}")
        print("="*60)

        # Calculate BPM difference
        bpm_diff = abs(analysis_a['tempo'] - analysis_b['tempo'])
        bpm_compatible = bpm_diff < 5.0

        # Check key compatibility (simplified - just exact match for now)
        key_compatible = analysis_a['estimated_key'] == analysis_b['estimated_key']

        # Energy progression
        energy_map = {"low": 1, "medium": 2, "high": 3}
        energy_a = energy_map.get(analysis_a['energy_level'], 2)
        energy_b = energy_map.get(analysis_b['energy_level'], 2)
        energy_change = energy_b - energy_a

        if energy_change > 0:
            energy_flow = f"BUILDING (+{energy_change})"
        elif energy_change < 0:
            energy_flow = f"DESCENDING ({energy_change})"
        else:
            energy_flow = "MAINTAINING"

        print(f"\n📊 Analysis:")
        print(f"  BPM: {analysis_a['tempo']:.1f} → {analysis_b['tempo']:.1f} (Δ {bpm_diff:.1f})")
        print(f"  Key: {analysis_a['estimated_key']} → {analysis_b['estimated_key']}")
        print(f"  Energy: {analysis_a['energy_level']} → {analysis_b['energy_level']} ({energy_flow})")
        print(f"  Mood: {analysis_a['mood']} → {analysis_b['mood']}")

        # Generate options based on compatibility
        options = []

        if bpm_compatible and key_compatible:
            options.append({
                "id": "beatmatch_8bar",
                "name": "8-bar beatmatch crossfade",
                "style": "SAFE & SMOOTH",
                "params": {
                    "transition_type": "beat_match",
                    "fade_duration_ms": 8000,
                    "mix_style": "seamless"
                },
                "description": "Perfect BPM/key match - blend smoothly over 8 bars"
            })

        if bpm_compatible:
            options.append({
                "id": "crossfade_4bar",
                "name": "4-bar crossfade",
                "style": "STANDARD",
                "params": {
                    "transition_type": "crossfade",
                    "fade_duration_ms": 4000,
                    "mix_style": "seamless"
                },
                "description": "Quick blend, BPM compatible"
            })

        options.append({
            "id": "hard_cut",
            "name": "Hard cut on beat",
            "style": "ENERGETIC",
            "params": {
                "transition_type": "simple",
                "fade_duration_ms": 100,
                "mix_style": "basic"
            },
            "description": "Instant switch - creates tension/surprise"
        })

        options.append({
            "id": "long_blend",
            "name": "16-bar layered blend",
            "style": "EXPERIMENTAL",
            "params": {
                "transition_type": "crossfade",
                "fade_duration_ms": 16000,
                "mix_style": "seamless"
            },
            "description": "Extended overlap - complex but rewarding"
        })

        # Add custom option
        options.append({
            "id": "custom",
            "name": "Custom transition",
            "style": "YOUR CALL",
            "params": None,
            "description": "Describe what you want"
        })

        print(f"\n🎛️ Transition Options:")
        for i, opt in enumerate(options, 1):
            print(f"\n  [{i}] {opt['name']} - {opt['style']}")
            print(f"      {opt['description']}")

        return {
            "track_a": track_a_path,
            "track_b": track_b_path,
            "analysis_a": analysis_a,
            "analysis_b": analysis_b,
            "compatibility": {
                "bpm": bpm_compatible,
                "key": key_compatible,
                "bpm_diff": bpm_diff,
                "energy_flow": energy_flow
            },
            "options": options
        }

    def execute_transition(
        self,
        session: Dict,
        track_a_index: int,
        track_b_index: int,
        choice: int,
        custom_params: Optional[Dict] = None
    ) -> Dict:
        """
        Execute chosen transition.

        Args:
            session: Current session state
            track_a_index: Index of outgoing track
            track_b_index: Index of incoming track
            choice: Option number (1-based)
            custom_params: If custom option, provide parameters

        Returns:
            Transition result with audio path
        """
        transition_opts = self.get_transition_options(session, track_a_index, track_b_index)

        if choice < 1 or choice > len(transition_opts['options']):
            return {"error": f"Invalid choice {choice}"}

        selected = transition_opts['options'][choice - 1]

        print(f"\n⚡ Executing: {selected['name']}")

        # Use custom params if provided, otherwise use preset
        params = custom_params if custom_params else selected['params']

        if params is None:
            return {"error": "Custom transition requires parameters"}

        # Get tracks
        track_a_path = session['tracks'][track_a_index]
        track_b_path = session['tracks'][track_b_index]
        analyses = [session['analyses'][track_a_index], session['analyses'][track_b_index]]

        # Execute mix
        print("  Generating mix...")
        mix_result = self.dj.create_mix(
            file_paths=[track_a_path, track_b_path],
            analyses=analyses,
            **params
        )

        if "error" in mix_result:
            return {"error": f"Mix generation failed: {mix_result['error']}"}

        # Log decision
        decision_log = {
            "from_track": track_a_index + 1,
            "to_track": track_b_index + 1,
            "option_chosen": selected['name'],
            "params": params,
            "mix_file": mix_result.get('mix_path')
        }

        session['mix_decisions'].append(decision_log)
        self.session_log.append({
            "action": "transition",
            **decision_log
        })

        print(f"  ✅ Mix created: {mix_result.get('mix_path')}")

        return {
            "success": True,
            "mix_path": mix_result.get('mix_path'),
            "decision": decision_log
        }

    def save_session(self, session: Dict, output_dir: str = "sessions") -> str:
        """Save session log for future reference."""
        from pathlib import Path
        import json
        from datetime import datetime

        Path(output_dir).mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_file = f"{output_dir}/{session['name']}_{timestamp}.json"

        session_data = {
            "session_name": session['name'],
            "timestamp": timestamp,
            "tracks": [str(Path(p).name) for p in session['tracks']],
            "decisions": session['mix_decisions'],
            "full_log": self.session_log
        }

        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        print(f"\n💾 Session saved: {session_file}")
        return session_file


if __name__ == "__main__":
    print("Interactive DJ Mixer")
    print("Usage:")
    print("  from tools.interactive_mixer import InteractiveMixer")
    print("  mixer = InteractiveMixer()")
    print("  session = mixer.start_session(['track1.mp3', 'track2.mp3'])")
    print("  options = mixer.get_transition_options(session, 0, 1)")
    print("  result = mixer.execute_transition(session, 0, 1, choice=1)")
