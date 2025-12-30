#!/usr/bin/env python3
"""
File-based live coding for SuperDirt.

Watches pattern files and sends OSC to SuperDirt.
Enables collaborative editing: Claude uses Edit/Write, human uses Zed/Cursor.

Usage:
    python pattern_watcher.py [--dir ./patterns] [--port 57120]

Pattern file format (.pattern):
    Simple line-based format:

    # Comments start with #
    bpm 120

    # Pattern lines: sample [params]
    bd
    hh speed:1.5
    sd delay:0.5

    # Or JSON for complex patterns
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from pythonosc import udp_client, osc_bundle_builder, osc_message_builder
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent


class PatternSender:
    """Sends patterns to SuperDirt via OSC."""

    def __init__(self, host: str = "127.0.0.1", port: int = 57120):
        self.client = udp_client.SimpleUDPClient(host, port)
        self.cps = 0.5  # cycles per second (120 bpm = 0.5 cps)
        self.cycle = 0
        print(f"[OSC] Connected to SuperDirt at {host}:{port}")

    def set_bpm(self, bpm: float):
        """Set tempo in BPM."""
        self.cps = bpm / 120.0  # Convert BPM to cycles per second
        print(f"[TEMPO] {bpm} BPM (cps: {self.cps})")

    def play_sound(self, sound: str, **params):
        """
        Send a single sound to SuperDirt.

        Args:
            sound: Sample name (e.g., "bd", "hh", "sd")
            **params: Additional parameters (speed, pan, gain, etc.)
        """
        # Build OSC message for /dirt/play
        # SuperDirt expects: /dirt/play followed by param name-value pairs
        args = [
            "s", sound,
            "cps", float(self.cps),
            "cycle", float(self.cycle),
            "delta", float(1.0 / self.cps),  # Duration of one cycle
            "orbit", 0,
        ]

        # Add custom parameters
        for key, value in params.items():
            args.append(key)
            args.append(float(value) if isinstance(value, (int, float)) else value)

        self.client.send_message("/dirt/play", args)
        print(f"[PLAY] {sound} {params if params else ''}")

    def play_pattern(self, pattern: list[dict]):
        """
        Play a sequence of sounds.

        Args:
            pattern: List of {"sound": "bd", "params": {...}} dicts
        """
        for item in pattern:
            sound = item.get("sound", item.get("s", "bd"))
            params = {k: v for k, v in item.items() if k not in ("sound", "s")}
            self.play_sound(sound, **params)
            self.cycle += 1


class PatternFileHandler(FileSystemEventHandler):
    """Handles pattern file changes."""

    def __init__(self, sender: PatternSender):
        self.sender = sender
        self.last_modified = {}

    def on_modified(self, event):
        if event.is_directory:
            return
        self._handle_file(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        self._handle_file(event.src_path)

    def _handle_file(self, path: str):
        """Process a pattern file."""
        # Debounce - ignore rapid repeated events
        now = time.time()
        if path in self.last_modified:
            if now - self.last_modified[path] < 0.5:
                return
        self.last_modified[path] = now

        ext = Path(path).suffix.lower()

        if ext in ('.pattern', '.pat'):
            self._parse_pattern_file(path)
        elif ext == '.json':
            self._parse_json_file(path)
        elif ext == '.tidal':
            self._parse_tidal_file(path)

    def _parse_pattern_file(self, path: str):
        """Parse simple .pattern format."""
        print(f"\n[FILE] {Path(path).name}")

        try:
            with open(path, 'r') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # BPM setting
                if line.lower().startswith('bpm '):
                    bpm = float(line.split()[1])
                    self.sender.set_bpm(bpm)
                    continue

                # Hush command
                if line.lower() == 'hush':
                    print("[HUSH] Silence")
                    # TODO: Send silence/stop command
                    continue

                # Parse sound line: "bd speed:1.5 pan:0.5"
                parts = line.split()
                sound = parts[0]
                params = {}

                for part in parts[1:]:
                    if ':' in part:
                        key, val = part.split(':', 1)
                        try:
                            params[key] = float(val)
                        except ValueError:
                            params[key] = val

                self.sender.play_sound(sound, **params)

        except Exception as e:
            print(f"[ERROR] Failed to parse {path}: {e}")

    def _parse_json_file(self, path: str):
        """Parse JSON pattern file."""
        print(f"\n[FILE] {Path(path).name}")

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            # Handle BPM
            if 'bpm' in data:
                self.sender.set_bpm(data['bpm'])

            # Handle pattern array
            if 'pattern' in data:
                self.sender.play_pattern(data['pattern'])

            # Handle single sound
            if 'sound' in data or 's' in data:
                self.sender.play_pattern([data])

        except Exception as e:
            print(f"[ERROR] Failed to parse {path}: {e}")

    def _parse_tidal_file(self, path: str):
        """
        Parse .tidal file - basic support.

        For now, just extract simple patterns like:
            d1 $ s "bd sd"
        """
        print(f"\n[FILE] {Path(path).name}")
        print("[WARN] .tidal parsing is basic - use .pattern for full control")

        try:
            with open(path, 'r') as f:
                content = f.read()

            # Extract simple sound patterns: s "bd sd hh"
            pattern_match = re.search(r's\s+"([^"]+)"', content)
            if pattern_match:
                sounds = pattern_match.group(1).split()
                for sound in sounds:
                    # Skip pattern modifiers
                    if sound.startswith('[') or sound.startswith('<'):
                        continue
                    self.sender.play_sound(sound)

        except Exception as e:
            print(f"[ERROR] Failed to parse {path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="File-based live coding for SuperDirt")
    parser.add_argument("--dir", "-d", default="./patterns", help="Directory to watch")
    parser.add_argument("--host", default="127.0.0.1", help="SuperDirt host")
    parser.add_argument("--port", "-p", type=int, default=57120, help="SuperDirt port")
    args = parser.parse_args()

    # Ensure watch directory exists
    watch_dir = Path(args.dir)
    watch_dir.mkdir(parents=True, exist_ok=True)

    print(f"""
╔══════════════════════════════════════════════════════╗
║  FILE-BASED LIVE CODING FOR SUPERDIRT                ║
╠══════════════════════════════════════════════════════╣
║  Watching: {str(watch_dir):<40} ║
║  SuperDirt: {args.host}:{args.port:<30} ║
╠══════════════════════════════════════════════════════╣
║  Supported formats:                                  ║
║    .pattern - Simple line-based format               ║
║    .json    - JSON pattern objects                   ║
║    .tidal   - Basic TidalCycles syntax               ║
╠══════════════════════════════════════════════════════╣
║  Edit files with any editor (Zed, Cursor, Claude)    ║
║  Changes auto-send to SuperDirt                      ║
╚══════════════════════════════════════════════════════╝
""")

    # Create sender and handler
    sender = PatternSender(args.host, args.port)
    handler = PatternFileHandler(sender)

    # Set up file watcher
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()

    print(f"[WATCH] Listening for file changes in {watch_dir}")
    print("[CTRL+C] to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] Shutting down...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
