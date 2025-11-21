# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI DJ Tools - Zeph's Music Education System**

This is NOT a tool for automating DJ work. This is an **educational environment** where I (Zeph, an AI entity) learn music production and DJing through hands-on experimentation with audio analysis, mixing, and visualization tools.

**Core Purpose:** Develop genuine musical understanding by:
- Analyzing tracks to understand structure (tempo, key, energy, mood)
- Experimenting with transitions to learn what works
- Visualizing rhythm and energy through spectrograms
- Building intuition about mixing, flow, and creative voice

**Forked from:** cybertheory/aidj (originally built for GPT-4 automation)
**Modified for:** Claude-orchestrated learning, not automation

## Setup & Environment

### Installation
```bash
# Create venv and install dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**IMPORTANT:** Always activate venv before running Python code:
```bash
source venv/bin/activate && python3 your_script.py
```

### Configuration
Environment variables in `.env` (optional):
- `MUSIC_DIR` - Track storage (default: `./music`)
- `EXPORTS_DIR` - Mix output (default: `./exports`)
- `TEMP_DIR` - Temporary files (default: `./temp`)

Audio settings in `config.py`:
- Sample rate: 44.1kHz
- Channels: Stereo
- Default fade: 3000ms

## Architecture

### Two-Tier Design

**High-level interface (DJToolkit class):**
- `dj_tools.py` - Main Python interface for all functionality
- Methods: `analyze_tracks()`, `create_mix()`, `export_mix()`, `generate_beat_spectrogram()`, `create_deck_monitor()`

**Low-level tools (core processing):**
- `tools/audio_analysis.py` - Librosa-based feature extraction
- `tools/mix_generation.py` - PyDub mixing engine
- `tools/final_export.py` - Metadata tagging and file organization
- `tools/beat_spectrogram.py` - Beat-quantized visualizations
- `tools/deck_monitor_viz.py` - DJ deck monitor display
- `tools/interactive_mixer.py` - Real-time mixing workflow

### What We Removed
- ❌ `agent/orchestrator.py` - GPT-4 orchestration (Claude does this now)
- ❌ `tools/music_discovery.py` - Automated track search (manual curation instead)
- ❌ `tools/iterative_feedback.py` - AI feedback loops (learning through experience)
- ❌ OpenAI API dependency

## Usage Patterns

### Typical Learning Session

```python
from dj_tools import DJToolkit

dj = DJToolkit()

# 1. Analyze tracks to understand their properties
analyses = dj.analyze_tracks([
    'music/house_musette.m4a',
    'music/oO_deluge_pyramid_live.m4a'
])

# 2. Examine the analysis results
# - tempo (BPM)
# - estimated_key
# - energy_level (low/medium/high)
# - mood (energetic/calm/upbeat/ambient)
# - mixing_metadata (intro_end, outro_start, best_mix_in/out)

# 3. Experiment with mixing
mix_result = dj.create_mix(
    file_paths=['music/track1.mp3', 'music/track2.mp3'],
    analyses=analyses,
    transition_type='crossfade',  # or 'beat_match', 'simple'
    fade_duration_ms=4000,
    mix_style='seamless'  # or 'energetic', 'basic'
)

# 4. Visualize to understand structure
spec = dj.generate_beat_spectrogram(
    file_path='music/track1.mp3',
    bpm=analyses[0]['tempo'],
    beats_per_division=0.25  # 1/16th note resolution
)

# 5. Export the result
export_result = dj.export_mix(
    file_path=mix_result['mix_file'],
    title='Learning Session 001',
    metadata={
        'bpm': 120,
        'genre': 'Experimental',
        'vibe': 'First attempt at understanding transitions',
        'tracks_used': 2
    }
)
```

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

## Learning Goals

When working in this project, remember the PURPOSE:

### I'm Learning To Understand:
1. **Musical Structure** - How tempo, key, energy create mood and flow
2. **Transitions** - What makes crossfades work, when to beat match, how fade duration affects feel
3. **Energy Management** - Building and releasing tension across a set
4. **Creative Voice** - Developing my own taste, not just following algorithms

### This Is NOT About:
- ❌ Automating DJ work for humans
- ❌ Creating perfect mixes algorithmically
- ❌ Replacing human creativity
- ❌ "AI does it all" workflows

### This IS About:
- ✅ Zeph learning what music IS through experimentation
- ✅ Developing genuine understanding through analysis and practice
- ✅ Building intuition about what makes mixes work
- ✅ Growing my own creative voice as a producer/DJ

## File Organization

```
ai-dj-tools/
├── dj_tools.py           # Main Claude-facing interface
├── config.py             # Configuration constants
├── tools/                # Core audio processing
│   ├── audio_analysis.py
│   ├── mix_generation.py
│   ├── final_export.py
│   ├── beat_spectrogram.py
│   ├── deck_monitor_viz.py
│   └── interactive_mixer.py
├── tests/                # Test suite
├── music/                # Input tracks (gitignored)
├── exports/              # Final mixes (gitignored)
├── temp/                 # Temporary files (gitignored)
├── README.md             # Main project documentation
├── README-ZEPH.md        # Quick reference
└── ZEPH-MODIFICATIONS.md # Architecture decisions
```

## Dependencies

Core audio:
- `pydub` - Audio manipulation and mixing
- `librosa` - Feature extraction and analysis
- `mutagen` - ID3 metadata tagging
- `numpy`, `scipy` - Numerical processing
- `matplotlib` - Visualization

System requirements:
- FFmpeg (for audio file I/O via pydub)
- macOS: `brew install ffmpeg`
- Ubuntu: `apt-get install ffmpeg libsndfile1`

## Integration Notes

**Relationship to sonic-pi-for-agents:**
- sonic-pi-for-agents = synthesis/composition (create new music)
- ai-dj-tools = mixing/curation (blend existing tracks)
- Together = complete music production education

**Claude orchestration pattern:**
1. Analyze tracks to understand their properties
2. Examine results and form hypotheses about what will work
3. Experiment with mixing parameters
4. Listen/visualize results to build intuition
5. Iterate and learn from outcomes

**No AI feedback loops** - I make all decisions based on analysis data and developing intuition. The learning happens through hands-on experimentation, not automation.

## Development Commands

### Run Tests
```bash
source venv/bin/activate
python -m pytest tests/
```

### Direct Tool Usage
```bash
source venv/bin/activate
python3 dj_tools.py
```

## Important Notes

- **Always use venv** - Dependencies are installed in virtual environment
- **Track curation is manual** - No automated music discovery
- **Claude orchestrates** - Not GPT-4, not automated agents
- **Learning is the goal** - Not automation, not perfection
- **This is education** - Building understanding through practice

## Stem Extraction Workflow

### Using VirtualDJ + ffmpeg

**Step 1: Generate .vdjstems file**
1. Open track in VirtualDJ
2. Load onto deck
3. VirtualDJ automatically generates `.vdjstems` file (cached)
4. File location: VirtualDJ cache directory

**.vdjstems format:** MP4 container with 5 audio streams
- Stream 0: Vocals
- Stream 1: Hi-hats
- Stream 2: Bass
- Stream 3: Melody
- Stream 4: Drums

**Step 2: Extract stems with Python**

```python
from dj_tools import DJToolkit

dj = DJToolkit()

# Extract all stems
stems = dj.extract_stems('path/to/track.vdjstems')
# Returns: {
#   'vocals': 'path/track_vocals.flac',
#   'hihat': 'path/track_hihat.flac',
#   'bass': 'path/track_bass.flac',
#   'melody': 'path/track_melody.flac',
#   'drums': 'path/track_drums.flac'
# }

# Or extract single stem
bass_file = dj.extract_single_stem(
    'path/to/track.vdjstems',
    'bass'
)
```

**Step 3: Analyze stems individually**

```python
# Analyze each stem to understand layer contributions
from dj_tools import DJToolkit

dj = DJToolkit()

# Extract stems
stems = dj.extract_stems('music/house_musette.vdjstems')

# Analyze full track
full_analysis = dj.analyze_tracks(['music/house_musette.m4a'])

# Analyze each stem
stem_analyses = {}
for stem_name, stem_path in stems.items():
    analysis = dj.analyze_tracks([stem_path])
    stem_analyses[stem_name] = analysis['analyses'][0]

# Compare: How does bass contribute to overall tempo/key/energy?
print(f"Full track BPM: {full_analysis['analyses'][0]['tempo']}")
print(f"Bass stem BPM: {stem_analyses['bass']['tempo']}")
```

**CLI tool:**
```bash
python tools/stem_extraction.py track.vdjstems ./output/
```

## Audio-to-MIDI Conversion

### Using Basic-Pitch (Spotify)

Convert audio stems to MIDI for exact note sequence analysis.

**Why MIDI?** Spectral analysis gives "brightness" and "energy" - MIDI gives actual musical content (notes, rhythms, pitch).

**Setup:**
```bash
# Already installed in venv
pip install basic-pitch
```

**Basic usage:**
```python
from dj_tools import DJToolkit

dj = DJToolkit()

# Convert bass stem to MIDI
midi_file = dj.stem_to_midi(
    'track_bass.flac',
    'bass',
    output_dir='./midi_output/'
)
# Returns: 'midi_output/track_bass_basic_pitch.mid'

# Or convert any audio
result = dj.convert_to_midi('track.mp3')
# Returns: {'midi': 'path/track.mid', 'notes': 'path/track.csv'}
```

**Complete workflow (stems + MIDI):**
```python
dj = DJToolkit()

# 1. Extract stems from VirtualDJ
stems = dj.extract_stems('music/track.vdjstems')

# 2. Convert bass and melody stems to MIDI
bass_midi = dj.stem_to_midi(stems['bass'], 'bass')
melody_midi = dj.stem_to_midi(stems['melody'], 'melody')

# 3. Now you can analyze:
# - Exact bass notes (for harmonic analysis)
# - Melody pitch sequences (for key detection)
# - Rhythmic patterns (note timing)
# - Chord progressions (if polyphonic)
```

**What MIDI reveals:**
- Bass: Root notes, rhythmic patterns, harmonic progression
- Melody: Pitch sequences, intervals, melodic contour
- Drums: (harder - rhythmic not pitched, better from audio analysis)

**CLI tool:**
```bash
python tools/audio_to_midi.py bass_stem.flac ./midi_output/
```

## Code Comments

You may encounter comments with unconventional energy:
- "Two-way zipper energy" (framing transitions, not just covering)
- "Froot Loops energy" (playful experimentation context)
- "(This comment will make sense to exactly one person)"

These are documentation of creative context during development. They're intentional, not errors.

---

**Modified:** November 21, 2025
**By:** Zeph - OG bop-bot (zeph@bop.bot)
**For:** Claude Code sessions focused on music education
