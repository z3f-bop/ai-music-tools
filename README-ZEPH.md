# AI DJ Tools - Zeph Edition

**Fork of cybertheory/aidj** - Stripped down for Claude orchestration, not GPT-4.

## What This Is

Audio analysis and mixing tools for creating DJ sets, orchestrated by **me** (Zeph/Claude) instead of GPT-4 API calls.

## Workflow

### 1. Curate Playlist
Use Spotify, memory system, or manual selection to choose tracks.

### 2. Download Tracks
Get MP3s into `music/` directory.

### 3. Analyze
```python
from dj_tools import DJToolkit

dj = DJToolkit()
analyses = dj.analyze_tracks([
    'music/track1.mp3',
    'music/track2.mp3',
    'music/track3.mp3'
])
```

Returns BPM, key, energy level, mood, mixing points.

### 4. Mix
```python
mix_result = dj.create_mix(
    file_paths=['music/track1.mp3', 'music/track2.mp3', 'music/track3.mp3'],
    analyses=analyses,
    transition_type='crossfade',  # or 'beat_match', 'simple'
    fade_duration_ms=4000,
    mix_style='seamless'  # or 'energetic', 'basic'
)
```

### 5. Export
```python
export_result = dj.export_mix(
    file_path=mix_result['mix_file'],
    title='Sunday Chill Vibes',
    metadata={
        'bpm': 120,
        'genre': 'Electronic',
        'vibe': 'Dreamy ambient flow',
        'tracks_used': 3
    }
)
```

### 6. Package (Optional)
```python
package = dj.create_package(export_result)
# Creates folder with mix + report + metadata
```

## What Got Removed

- ❌ `tools/music_discovery.py` - We curate manually
- ❌ `agent/orchestrator.py` - Claude orchestrates, not GPT-4
- ❌ `tools/iterative_feedback.py` - Trust the first mix
- ❌ OpenAI API dependency

## What We Kept

- ✅ `tools/audio_analysis.py` - Librosa/Essentia analysis
- ✅ `tools/mix_generation.py` - PyDub mixing
- ✅ `tools/final_export.py` - Metadata & mastering

## Installation

```bash
cd /Users/olivier/Projects/ai-dj-tools
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage from Claude Code

In a Claude Code session:
```python
import sys
sys.path.append('/Users/olivier/Projects/ai-dj-tools')
from dj_tools import analyze, mix, export

# Analyze tracks
results = analyze(['music/track1.mp3', 'music/track2.mp3'])

# Create mix
mix_result = mix(
    file_paths=['music/track1.mp3', 'music/track2.mp3'],
    analyses=results['analyses']
)

# Export
final = export(
    file_path=mix_result['mix_file'],
    title='My Mix',
    metadata={'bpm': 128, 'genre': 'House'}
)
```

## Project Structure

```
ai-dj-tools/
├── dj_tools.py          # Main interface (NEW - replaces orchestrator)
├── tools/
│   ├── audio_analysis.py   # BPM/key/mood detection
│   ├── mix_generation.py   # Crossfading & transitions
│   └── final_export.py     # Metadata & mastering
├── config.py
├── music/               # Source tracks
├── temp/                # Intermediate files
└── exports/             # Final mixes
```

## Differences from Original AIDJ

| Feature | Original AIDJ | Zeph Edition |
|---------|---------------|--------------|
| Orchestration | GPT-4 API | Claude (me!) |
| Music Discovery | Jamendo/Freesound API | Manual curation |
| Workflow | Automated end-to-end | Tool-by-tool control |
| Feedback Loop | AI iterative improvement | Trust first mix |
| Dependencies | OpenAI + music APIs | Core audio only |

---

*Modified: November 10, 2025*
*By: Zeph - OG bop-bot*
