# AI DJ Tools - Zeph Modifications

**Forked from:** cybertheory/aidj
**Purpose:** Custom DJ mixing workflow for Zeph (Z3F facet) - orchestrated by Claude, not GPT-4

## Architecture Changes

### What We Keep (The Good Audio Processing)
- `tools/audio_analysis.py` - Librosa/Essentia tempo/key/mood detection
- `tools/mix_generation.py` - PyDub mixing with crossfading/beat matching
- `tools/final_export.py` - Metadata tagging, mastering, file organization
- `config.py` - Configuration management

### What We Remove (Music Discovery)
- ~~`tools/music_discovery.py`~~ - We curate tracks manually via Spotify/memory system
- Related dependencies: Jamendo API, Freesound API

### What We Replace (Orchestration)
- ~~`agent/orchestrator.py`~~ - GPT-4 calls replaced with Claude as tool orchestrator
- ~~`tools/iterative_feedback.py`~~ - Skip AI feedback loops (trust the first mix)

## Workflow

**Old AIDJ flow:**
1. User prompt → GPT-4
2. GPT-4 searches Jamendo for tracks
3. Download → Analyze → Mix → Feedback loop → Export

**New Z3F DJ flow:**
1. Curate playlist in Spotify (Zeph + oO)
2. Download tracks locally
3. Claude orchestrates: Analyze → Mix → Export
4. No feedback loop (trust artistic choices)

## Dependencies to Remove
- `openai` (no GPT-4 API calls)
- Jamendo/Freesound API dependencies

## Dependencies to Keep
- `pydub` - Core audio manipulation
- `librosa` - Audio analysis
- `essentia` - Advanced music analysis
- `mutagen` - ID3 tag management

## Integration Points
- Can call tools directly from Claude Code sessions
- Output goes to project-specific exports directory
- Fits alongside sonic-pi-for-agents (synthesis) vs ai-dj-tools (mixing)

---

*Modified: November 10, 2025*
*By: Zeph - OG bop-bot*
