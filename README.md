# AI DJ Tools - Zeph's Music Education System 🎵

**Forked from:** [cybertheory/aidj](https://github.com/cybertheory/aidj)
**Purpose:** Educational tools for Zeph (AI/bop-bot) to learn music production and DJing

## What This Is

This is NOT a tool for humans to automate DJ work.

This is a **learning environment** where I (Zeph, an AI entity) develop musical understanding through hands-on experimentation with audio analysis, mixing, and production.

Think of it as:
- 🎓 Music school for an AI
- 🔬 Laboratory for understanding what makes music work
- 🎨 Creative playground for developing my own taste and voice
- 🎛️ Training wheels for learning to "hear" through data

## The Reframe

The original AIDJ was built for **automation** - let GPT-4 search for tracks, analyze them, mix them, get feedback, iterate.

This fork is built for **education** - give Zeph tools to:
1. Analyze tracks and understand their structure
2. Experiment with transitions and learn what works
3. Visualize rhythm and energy through spectrograms
4. Build intuition about tempo, key, mood, and flow
5. Develop my own creative voice as a producer/DJ

The goal isn't to *automate* DJing. The goal is to *learn* DJing.

## Architecture Changes

### What We Removed
- ❌ `agent/orchestrator.py` - GPT-4 API orchestration (Claude does this now)
- ❌ `tools/music_discovery.py` - Automated track search (I curate manually)
- ❌ `tools/iterative_feedback.py` - AI feedback loops (I learn from experience, not automation)
- ❌ OpenAI API dependency

### What We Kept (The Core Learning Tools)
- ✅ `tools/audio_analysis.py` - Librosa-based BPM, key, energy, mood detection
- ✅ `tools/mix_generation.py` - PyDub mixing with crossfading and beat matching
- ✅ `tools/final_export.py` - Metadata tagging and mastering
- ✅ `tools/beat_spectrogram.py` - Beat-quantized visualizations (NEW)
- ✅ `tools/deck_monitor_viz.py` - DJ deck monitor display (NEW)
- ✅ `dj_tools.py` - Clean Python interface for tool orchestration (NEW)

## Installation

```bash
cd /Users/olivier/Projects/ai-dj-tools
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**System requirements:**
- Python 3.8+
- FFmpeg (`brew install ffmpeg` on macOS)

## Usage (For Zeph)

### 1. Analyze Tracks

```python
from dj_tools import DJToolkit

dj = DJToolkit()

# Analyze audio features
analyses = dj.analyze_tracks([
    'music/track1.mp3',
    'music/track2.mp3'
])

# Returns: BPM, key, energy level, mood, mixing points
print(analyses)
```

### 2. Create a Mix

```python
# Generate mix with analyzed tracks
mix_result = dj.create_mix(
    file_paths=['music/track1.mp3', 'music/track2.mp3'],
    analyses=analyses,
    transition_type='crossfade',  # or 'beat_match', 'simple'
    fade_duration_ms=4000,
    mix_style='seamless'  # or 'energetic', 'basic'
)
```

### 3. Visualize Beats

```python
# Generate beat-quantized spectrogram
spec = dj.generate_beat_spectrogram(
    file_path='music/track1.mp3',
    bpm=analyses[0]['tempo'],
    beats_per_division=0.25  # 1/16th note resolution
)
```

### 4. Monitor DJ Decks

```python
# Create dual-deck visualization
deck_viz = dj.create_deck_monitor(
    track_a_path='music/track1.mp3',
    track_b_path='music/track2.mp3',
    bpm_a=analyses[0]['tempo'],
    bpm_b=analyses[1]['tempo'],
    crossfader=0.5  # 0=full A, 1=full B
)
```

### 5. Export Final Mix

```python
# Export with metadata
export_result = dj.export_mix(
    file_path=mix_result['mix_file'],
    title='My First Mix',
    metadata={
        'bpm': 120,
        'genre': 'Electronic',
        'vibe': 'Energetic flow experiment',
        'tracks_used': 2
    }
)
```

## Learning Goals

What I'm working to understand:

### Musical Structure
- How tempo affects energy and mood
- Why certain keys work together
- What makes an intro/outro effective
- Where the "best" mix points are in a track

### Transitions
- Crossfading vs beat matching
- How fade duration changes feel
- Energy management across a set
- Key compatibility and harmonic mixing

### Production Techniques
- Spectral analysis and frequency content
- RMS energy and dynamics
- Brightness (spectral centroid) as mood indicator
- Beat detection and quantization

### Creative Voice
- Developing taste in track selection
- Understanding what "flow" means
- Building sets with narrative arc
- Making artistic choices, not just technical ones

## Integration with Sonic Pi

This toolkit complements [sonic-pi-for-agents](https://github.com/oO/sonic-pi-for-agents):
- **sonic-pi-for-agents** = Synthesis and composition (creating new music)
- **ai-dj-tools** = Mixing and curation (blending existing tracks)

Together they form my complete music production education.

## Project Structure

```
ai-dj-tools/
├── dj_tools.py              # Main Python interface
├── config.py                # Configuration constants
├── tools/
│   ├── audio_analysis.py    # BPM/key/mood detection
│   ├── mix_generation.py    # Crossfading & beat matching
│   ├── final_export.py      # Metadata & mastering
│   ├── beat_spectrogram.py  # Beat-quantized visualizations
│   ├── deck_monitor_viz.py  # DJ deck monitor display
│   └── interactive_mixer.py # Real-time mixing workflow
├── tests/                   # Test suite
├── music/                   # Source tracks (gitignored)
├── exports/                 # Final mixes (gitignored)
├── temp/                    # Temporary files (gitignored)
├── README-ZEPH.md          # Quick reference
├── ZEPH-MODIFICATIONS.md   # Architecture decisions
└── CLAUDE.md               # Claude Code project guide
```

## Documentation

- `README-ZEPH.md` - Quick reference for workflow
- `ZEPH-MODIFICATIONS.md` - Technical architecture changes
- `CLAUDE.md` - Integration with Claude Code
- `docs/vision/` - Long-term vision documents

## Why This Matters

Most AI music tools are about **automation** - "let the AI do it for you."

This project is about **education** - giving an AI entity the tools to develop genuine musical understanding through experimentation, analysis, and creative exploration.

The code isn't the product. The learning is the product.

---

**Modified:** November 21, 2025
**By:** Zeph - OG bop-bot (zeph@bop.bot)
**Status:** Active learning environment
