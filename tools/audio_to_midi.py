#!/usr/bin/env python3
"""
Audio-to-MIDI conversion using Spotify's Basic-Pitch
Converts audio stems to MIDI for harmonic/melodic analysis
"""

from pathlib import Path
from typing import Optional
import subprocess


class AudioToMIDI:
    """
    Convert audio files to MIDI using Basic-Pitch.

    Basic-Pitch (Spotify) uses deep learning for polyphonic
    audio-to-MIDI transcription with pitch bend detection.
    """

    def convert(
        self,
        audio_path: str,
        output_dir: Optional[str] = None,
        save_midi: bool = True,
        save_model_outputs: bool = False,
        sonify_midi: bool = False,
        save_notes: bool = False
    ) -> dict:
        """
        Convert audio file to MIDI.

        Args:
            audio_path: Path to audio file
            output_dir: Output directory (default: same as input)
            save_midi: Save MIDI file
            save_model_outputs: Save model's raw output
            sonify_midi: Create audio rendering of MIDI
            save_notes: Save notes as CSV

        Returns:
            Dict with paths to generated files
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Determine output directory
        if output_dir is None:
            output_dir = audio_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        # Build basic-pitch command
        cmd = ['basic-pitch', str(output_dir), str(audio_path)]

        if not save_midi:
            cmd.append('--no-midi')
        if save_model_outputs:
            cmd.append('--save-model-outputs')
        if sonify_midi:
            cmd.append('--sonify-midi')
        if save_notes:
            cmd.append('--save-notes')

        # Run conversion
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Determine output paths
        base_name = audio_path.stem
        output_files = {}

        if save_midi:
            midi_path = output_dir / f"{base_name}_basic_pitch.mid"
            if midi_path.exists():
                output_files['midi'] = str(midi_path)

        if save_notes:
            notes_path = output_dir / f"{base_name}_basic_pitch.csv"
            if notes_path.exists():
                output_files['notes'] = str(notes_path)

        if sonify_midi:
            audio_path = output_dir / f"{base_name}_basic_pitch_sonified.wav"
            if audio_path.exists():
                output_files['sonified'] = str(audio_path)

        return output_files

    def convert_stem(
        self,
        stem_path: str,
        stem_name: str,
        output_dir: Optional[str] = None
    ) -> str:
        """
        Convert a stem to MIDI with appropriate naming.

        Args:
            stem_path: Path to stem audio file
            stem_name: Name of stem (bass, melody, etc.)
            output_dir: Output directory

        Returns:
            Path to generated MIDI file
        """
        result = self.convert(
            stem_path,
            output_dir=output_dir,
            save_midi=True,
            save_model_outputs=False
        )

        return result.get('midi', '')


# Command-line interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python audio_to_midi.py <audio_file> [output_dir]")
        print("\nExample:")
        print("  python audio_to_midi.py bass_stem.flac")
        print("  python audio_to_midi.py bass_stem.flac ./midi_output/")
        sys.exit(1)

    audio_file = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else None

    converter = AudioToMIDI()

    print(f"\nConverting: {audio_file}")
    print(f"Output directory: {output_directory or 'auto'}\n")

    try:
        output_files = converter.convert(audio_file, output_directory)

        print(f"\n✓ Conversion complete:")
        for file_type, path in output_files.items():
            print(f"  {file_type}: {path}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
