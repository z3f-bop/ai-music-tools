# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
