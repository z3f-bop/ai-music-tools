#!/usr/bin/env python3
"""
Stem extraction tool using VirtualDJ + ffmpeg
Extracts individual stems from .vdjstems files
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Optional


class StemExtractor:
    """
    Extract individual stems from VirtualDJ .vdjstems files.

    .vdjstems files are MP4 containers with 5 audio streams:
    - Stream 0: Vocals
    - Stream 1: Hi-hats
    - Stream 2: Bass
    - Stream 3: Melody
    - Stream 4: Drums
    """

    STEM_NAMES = {
        0: 'vocals',
        1: 'hihat',
        2: 'bass',
        3: 'melody',
        4: 'drums'
    }

    def __init__(self, output_format: str = 'flac'):
        """
        Initialize stem extractor.

        Args:
            output_format: Audio format for extracted stems (flac, wav, mp3)
        """
        self.output_format = output_format

    def extract_stems(
        self,
        vdjstems_path: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extract all stems from a .vdjstems file.

        Args:
            vdjstems_path: Path to .vdjstems file
            output_dir: Directory for extracted stems (default: same as input)

        Returns:
            Dict mapping stem names to output file paths
        """
        vdjstems_path = Path(vdjstems_path)

        if not vdjstems_path.exists():
            raise FileNotFoundError(f"File not found: {vdjstems_path}")

        if vdjstems_path.suffix != '.vdjstems':
            raise ValueError(f"Expected .vdjstems file, got: {vdjstems_path.suffix}")

        # Determine output directory
        if output_dir is None:
            output_dir = vdjstems_path.parent / f"{vdjstems_path.stem}_stems"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract each stem
        stem_paths = {}
        base_name = vdjstems_path.stem

        for stream_id, stem_name in self.STEM_NAMES.items():
            output_file = output_dir / f"{base_name}_{stem_name}.{self.output_format}"

            # ffmpeg command to extract specific audio stream
            cmd = [
                'ffmpeg',
                '-i', str(vdjstems_path),
                '-map', f'0:a:{stream_id}',
                '-y',  # Overwrite output files
                str(output_file)
            ]

            try:
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
                stem_paths[stem_name] = str(output_file)
                print(f"✓ Extracted {stem_name}: {output_file.name}")

            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to extract {stem_name}: {e.stderr}")

        return stem_paths

    def extract_single_stem(
        self,
        vdjstems_path: str,
        stem_name: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Extract a single stem from a .vdjstems file.

        Args:
            vdjstems_path: Path to .vdjstems file
            stem_name: Name of stem to extract (vocals, hihat, bass, melody, drums)
            output_path: Optional output file path

        Returns:
            Path to extracted stem file
        """
        # Find stream ID for requested stem
        stream_id = None
        for sid, sname in self.STEM_NAMES.items():
            if sname == stem_name:
                stream_id = sid
                break

        if stream_id is None:
            raise ValueError(
                f"Invalid stem name: {stem_name}. "
                f"Valid options: {list(self.STEM_NAMES.values())}"
            )

        vdjstems_path = Path(vdjstems_path)

        # Determine output path
        if output_path is None:
            output_path = (
                vdjstems_path.parent /
                f"{vdjstems_path.stem}_{stem_name}.{self.output_format}"
            )
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Extract stem
        cmd = [
            'ffmpeg',
            '-i', str(vdjstems_path),
            '-map', f'0:a:{stream_id}',
            '-y',
            str(output_path)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        return str(output_path)


# Command-line interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python stem_extraction.py <vdjstems_file> [output_dir]")
        print("\nExample:")
        print("  python stem_extraction.py track.vdjstems")
        print("  python stem_extraction.py track.vdjstems ./stems/")
        sys.exit(1)

    vdjstems_file = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else None

    extractor = StemExtractor()

    print(f"\nExtracting stems from: {vdjstems_file}")
    print(f"Output directory: {output_directory or 'auto'}\n")

    try:
        stem_paths = extractor.extract_stems(vdjstems_file, output_directory)

        print(f"\n✓ Successfully extracted {len(stem_paths)} stems:")
        for stem_name, path in stem_paths.items():
            print(f"  {stem_name}: {path}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
