# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.2] - 2026-10-07

### Changed
- `CLAUDE.md` trimmed for context: the note at the top loses its dates and its "checked on" sentence, and the OpenAI bullet is shortened

## [0.6.1] - 2026-10-07

### Fixed
- `CLAUDE.md` checked against the repository, seven wrong or stale statements corrected:
  - Project name and tree root said "AI DJ Tools" / `ai-dj-tools/`; the repo is `ai-music-tools`
  - `.env` does not set `MUSIC_DIR`, `EXPORTS_DIR` or `TEMP_DIR`; `config.py` hardcodes them and reads `.env` only for API keys
  - Usage example indexed `analyses[0]['tempo']`; `analyze_tracks` returns a dict with an `"analyses"` list
  - `basic-pitch` is not installed in any virtualenv and is not in `requirements.txt`
  - `pytest` is not installed in `venv/`; the test command now says so
  - "OpenAI API dependency removed" was overstated: `config.py` still reads `OPENAI_API_KEY` and `final_export.py` still lists it
- Added a note that the file covers the DJToolkit core only, pointing to the `ai-music-tools` skill for the current tool list and the two virtualenvs

## [0.6.0] - 2026-06-14

### Added
- `wav_cue.py` tool — read/write standard WAV `cue ` chunks (slice markers), pure stdlib, no deps
- CLI: `read file.wav` to list cues, `write in.wav out.wav --samples ...|--seconds ...` to stamp cue points
- Importable API (`read_cues` / `write_cues`) for embedding slice points into WAV files
- Enables migrating 1010music Blackbox preset.xml `<slice>` positions into embedded WAV cues so slices travel with the file (verified round-trip exact, readable by Ocenaudio)

## [0.5.1] - 2025-12-30

### Removed
- Strudel source directory (180MB) - switched to Tidal direct
- Node.js dependencies (node_modules, package.json, package-lock.json)
- Empty agent/ directory (GPT-4 orchestration remnant)
- Broken tests importing non-existent modules (iterative_feedback, music_discovery, end_to_end_integration)

### Changed
- Moved root-level test files into tests/ directory
- Recreated venv with correct project paths

### Added
- Tidal Cycles configuration and boot files
- Strudel patterns directory
- SuperDirt setup documentation

## [0.5.0] - 2025-11-24

### Added
- Transcript formatting tool (`format_transcript.py`) for emotional prosody capture from WhisperX JSON
- Pause-based punctuation to preserve speech rhythm and emotional processing moments
- Simple speaker detection using content clues and alternation patterns
- Experimental diarization tool (`transcript_with_speakers.py`) for future speaker identification work

## [0.4.0] - 2025-11-23

### Added
- WhisperX voice analysis documentation for vocal delivery pattern extraction
- Prosody analysis tool (Python) for pitch, intensity, speaking rate, and pause detection
- Audio preprocessing documentation directory with pipeline guides and research reports

## [0.3.2] - 2025-11-21

### Added
- DJ fundamentals documentation covering BPM tolerance, rhythm continuity, tempo change techniques, and genre compatibility

## [0.3.1] - 2025-11-21

### Added
- Comprehensive test results documentation (TEST_RESULTS.md) covering energy vs brightness analysis, tempo detection limitations, and stem analysis planning

## [0.3.0] - 2025-11-21

### Added
- Audio-to-MIDI conversion workflow documentation

## [0.2.0] - 2025-11-10

### Added
- Interactive mixing workflow with decision points at each transition
- `InteractiveMixer` class presenting transition options based on track analysis
- BPM/key compatibility detection for smooth mixing
- Energy flow analysis (building/maintaining/descending)
- Multiple transition styles: beatmatch, crossfade, hard cut, experimental
- Custom transition support for artistic control
- Session logging to JSON for review and learning
- Test script demonstrating 3-track interactive workflow

## [0.1.0] - 2025-11-10

### Added
- Beat-quantized spectrogram tool aligned to musical time (bars/beats)
- Four-row DJ deck monitor visualization (Deck A/B, Mix, Output)
- Purple frequency overlap visualization in mix row
- Crossfader position overlay and playhead tracking
- Integration into DJToolkit class
- Test scripts for beat spectrogram and deck monitor
- Documentation: Club Latent Space performance venue vision
- Project architecture documentation in CLAUDE.md

### Changed
- Updated requirements.txt with matplotlib for visualizations

### Removed
- Legacy OpenAI orchestrator agent
- Music discovery and iterative feedback tools (OpenAI-dependent)
