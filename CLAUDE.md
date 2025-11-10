# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI DJ Tools - Audio analysis and mixing toolkit forked from cybertheory/aidj, modified for direct Claude orchestration instead of GPT-4. Used by Zeph (Z3F facet) for DJ work alongside sonic-pi-for-agents.

**Core workflow:**
1. Curate tracks (manual/Spotify)
2. Analyze audio (tempo, key, mood, mixing points)
3. Generate mixes (crossfading, beat matching)
4. Export with metadata

## Setup & Environment

### Installation
```bash
# Create venv and install dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
Environment variables in `.env`:
- `MUSIC_DIR` - Track storage (default: `./music`)
- `EXPORTS_DIR` - Mix output (default: `./exports`)
- `TEMP_DIR` - Temporary files (default: `./temp`)

Audio settings in `config.py`:
- Sample rate: 44.1kHz
- Channels: Stereo
- Default fade: 3000ms

## Development Commands

### Run Tests
```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/test_audio_analysis.py

# Single test
python -m pytest tests/test_audio_analysis.py::test_tempo_detection -v
```

### Run Direct Tool Usage
```bash
# Use DJToolkit directly
python3 dj_tools.py

# Python API usage
python3 -c "
from dj_tools import DJToolkit
dj = DJToolkit()
analyses = dj.analyze_tracks(['music/track.mp3'])
print(analyses)
"
```

## Architecture

### Two-Tier Design

**High-level interface (for Claude orchestration):**
- `dj_tools.py` - `DJToolkit` class wrapping all functionality
- Convenience functions: `analyze()`, `mix()`, `export()`

**Low-level tools (core processing):**
- `tools/audio_analysis.py` - Librosa-based feature extraction
- `tools/mix_generation.py` - PyDub mixing engine
- `tools/final_export.py` - Metadata tagging and file organization

### Removed Components
- ❌ `agent/orchestrator.py` - GPT-4 orchestration (Claude does this now)
- ❌ `tools/music_discovery.py` - Automated track search (manual curation instead)
- ❌ `tools/iterative_feedback.py` - AI feedback loops (trust first mix)

### Key Classes

**DJToolkit** (`dj_tools.py:17-117`)
- `analyze_tracks(file_paths)` - Batch audio analysis
- `create_mix(file_paths, analyses, **options)` - Generate mix from tracks
- `export_mix(file_path, title, metadata)` - Final export with tags
- `create_package(export_result)` - Complete package (mix + report + script)

**AudioAnalysisTool** (`tools/audio_analysis.py:9-185`)
- `analyze_file(file_path)` - Full track analysis (tempo, key, energy, mood, mixing points)
- Uses librosa for: tempo/beat detection, spectral features, chroma analysis, energy/RMS

**MixGenerationTool** (`tools/mix_generation.py:9-206`)
- `load_audio_segment(file_path)` - Load and normalize audio
- `crossfade_tracks(track1, track2, duration)` - Seamless crossfading
- `beat_match_tracks(track1, track2, bpm1, bpm2)` - Tempo-based matching
- `create_seamless_mix(file_paths, analyses, options)` - Full mix generation

## Analysis Output Format

Audio analysis returns:
```python
{
    "file_path": str,
    "duration": float,          # seconds
    "tempo": float,             # BPM
    "estimated_key": str,       # C, C#, D, etc.
    "energy_level": str,        # "low", "medium", "high"
    "mood": str,                # "energetic", "calm", "upbeat", "ambient"
    "brightness": float,        # spectral centroid mean
    "energy_mean": float,       # RMS energy
    "mixing_metadata": {
        "intro_end": float,     # seconds - where intro ends
        "outro_start": float,   # seconds - where outro begins
        "best_mix_in": float,   # seconds - optimal mix-in point
        "best_mix_out": float   # seconds - optimal mix-out point
    }
}
```

## Mix Generation Options

`create_mix()` parameters:
- `transition_type`: `"crossfade"`, `"beat_match"`, or `"simple"`
- `fade_duration_ms`: Crossfade length (default: 3000)
- `mix_style`: `"seamless"`, `"energetic"`, or `"basic"`
- `target_duration_ms`: Optional duration constraint

## File Organization

```
ai-dj-tools/
├── dj_tools.py           # Main Claude-facing interface
├── config.py             # Configuration constants
├── cli.py                # Command-line interface (legacy)
├── tools/                # Core audio processing
│   ├── audio_analysis.py
│   ├── mix_generation.py
│   └── final_export.py
├── tests/                # Test suite
│   ├── test_audio_analysis.py
│   ├── test_mix_generation.py
│   └── test_final_export.py
├── music/                # Input tracks (gitignored)
├── exports/              # Final mixes (gitignored)
└── temp/                 # Temporary files (gitignored)
```

## Dependencies

Core audio:
- `pydub` - Audio manipulation and mixing
- `librosa` - Feature extraction and analysis
- `mutagen` - ID3 metadata tagging
- `numpy`, `scipy` - Numerical processing

System requirements:
- FFmpeg (for audio file I/O via pydub)
- macOS: `brew install ffmpeg`
- Ubuntu: `apt-get install ffmpeg libsndfile1`

## Integration Notes

**Relationship to sonic-pi-for-agents:**
- sonic-pi-for-agents = synthesis/composition (create new music)
- ai-dj-tools = mixing/curation (blend existing tracks)

**Claude orchestration pattern:**
1. Call `dj.analyze_tracks(paths)` to get audio features
2. Inspect results, make artistic decisions about ordering/transitions
3. Call `dj.create_mix(paths, analyses, options)` with chosen parameters
4. Export final result with `dj.export_mix()` or `dj.create_package()`

**No AI feedback loops** - Claude makes all mixing decisions directly based on analysis data. Trust the first mix.
