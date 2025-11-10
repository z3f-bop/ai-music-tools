#!/usr/bin/env python3
"""
AI DJ Tools - Direct interface to audio analysis and mixing
Orchestrated by Claude, not GPT-4
"""

from typing import List, Dict, Optional
from pathlib import Path

# Import the core tools we're keeping
from tools.audio_analysis import audio_analysis_tool, batch_audio_analysis_tool
from tools.mix_generation import mix_generation_tool
from tools.final_export import final_mix_export_tool, create_mix_package_tool
from tools.beat_spectrogram import beat_spectrogram_tool
from tools.deck_monitor_viz import create_deck_monitor_visualization
from config import Config


class DJToolkit:
    """
    Simplified interface to AIDJ's audio processing tools.
    No GPT-4 orchestration - designed for direct Claude control.
    """

    def __init__(self):
        Config.ensure_directories()

    def analyze_tracks(self, file_paths: List[str]) -> Dict:
        """
        Analyze audio files for BPM, key, energy, mood.

        Args:
            file_paths: List of paths to audio files

        Returns:
            Dict with analysis results for each file
        """
        return batch_audio_analysis_tool(file_paths)

    def create_mix(
        self,
        file_paths: List[str],
        analyses: List[Dict],
        transition_type: str = "crossfade",
        fade_duration_ms: int = 3000,
        mix_style: str = "seamless",
        target_duration_ms: Optional[int] = None
    ) -> Dict:
        """
        Generate a mix from analyzed tracks.

        Args:
            file_paths: Audio files to mix
            analyses: Analysis results from analyze_tracks()
            transition_type: "crossfade", "beat_match", or "simple"
            fade_duration_ms: Crossfade duration
            mix_style: "seamless", "energetic", or "basic"
            target_duration_ms: Optional target duration (will trim/extend)

        Returns:
            Dict with mix file path and metadata
        """
        return mix_generation_tool(
            file_paths=file_paths,
            analyses=analyses,
            transition_type=transition_type,
            fade_duration_ms=fade_duration_ms,
            mix_style=mix_style,
            target_duration_ms=target_duration_ms
        )

    def export_mix(
        self,
        file_path: str,
        title: str,
        metadata: Dict,
        export_format: str = "mp3",
        bitrate: str = "320k"
    ) -> Dict:
        """
        Export final mix with metadata and organization.

        Args:
            file_path: Path to mix file
            title: Mix title
            metadata: Dict with bpm, genre, vibe, etc.
            export_format: "mp3" or "wav"
            bitrate: Audio bitrate (for mp3)

        Returns:
            Dict with export paths and file info
        """
        return final_mix_export_tool(
            file_path=file_path,
            title=title,
            metadata=metadata,
            export_format=export_format,
            bitrate=bitrate
        )

    def create_package(
        self,
        export_result: Dict,
        include_source_files: bool = False
    ) -> Dict:
        """
        Create complete package with mix, report, and script.

        Args:
            export_result: Result from export_mix()
            include_source_files: Whether to include original tracks

        Returns:
            Dict with package directory path
        """
        return create_mix_package_tool(
            export_result=export_result,
            include_source_files=include_source_files
        )

    def generate_beat_spectrogram(
        self,
        file_path: str,
        bpm: float,
        beats_per_division: float = 0.25,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Generate beat-quantized spectrogram visualization.

        Args:
            file_path: Path to audio file
            bpm: Tempo in BPM (from analyze_tracks)
            beats_per_division: Musical resolution (0.25 = 1/16th note, 0.5 = 1/8th, etc.)
            output_path: Optional base path for output files

        Returns:
            Dict with spectrogram data, image path, and metadata
        """
        return beat_spectrogram_tool(
            file_path=file_path,
            bpm=bpm,
            beats_per_division=beats_per_division,
            output_path=output_path
        )

    def create_deck_monitor(
        self,
        track_a_path: str,
        track_b_path: str,
        bpm_a: float,
        bpm_b: float,
        crossfader: float = 0.5,
        playhead_a_seconds: Optional[float] = None,
        playhead_b_seconds: Optional[float] = None,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Create DJ deck monitor visualization showing A/Mix/B in vertical stack.

        Args:
            track_a_path: Path to deck A audio
            track_b_path: Path to deck B audio
            bpm_a: Tempo of track A
            bpm_b: Tempo of track B
            crossfader: Position 0-1 (0=full A, 1=full B)
            playhead_a_seconds: Current position in track A
            playhead_b_seconds: Current position in track B
            output_path: Optional output image path

        Returns:
            Dict with visualization paths and metadata
        """
        return create_deck_monitor_visualization(
            track_a_path=track_a_path,
            track_b_path=track_b_path,
            bpm_a=bpm_a,
            bpm_b=bpm_b,
            crossfader=crossfader,
            playhead_a_seconds=playhead_a_seconds,
            playhead_b_seconds=playhead_b_seconds,
            output_path=output_path
        )


# Convenience functions for Claude Code tool integration
def analyze(file_paths: List[str]) -> Dict:
    """Quick analysis of audio files"""
    toolkit = DJToolkit()
    return toolkit.analyze_tracks(file_paths)


def mix(file_paths: List[str], analyses: List[Dict], **kwargs) -> Dict:
    """Quick mix generation"""
    toolkit = DJToolkit()
    return toolkit.create_mix(file_paths, analyses, **kwargs)


def export(file_path: str, title: str, metadata: Dict, **kwargs) -> Dict:
    """Quick export"""
    toolkit = DJToolkit()
    return toolkit.export_mix(file_path, title, metadata, **kwargs)


if __name__ == "__main__":
    print("AI DJ Tools - Use via Python import or Claude Code session")
    print("Example:")
    print("  from dj_tools import DJToolkit")
    print("  dj = DJToolkit()")
    print("  analyses = dj.analyze_tracks(['track1.mp3', 'track2.mp3'])")
    print("  mix_result = dj.create_mix(['track1.mp3', 'track2.mp3'], analyses)")
