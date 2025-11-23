# WhisperX Voice Analysis Tool

**Location:** `/Users/olivier/Projects/bop-os/.venv-skills/bin/whisperx`

**Purpose:** Analyze voice delivery patterns (rhythm, speaking rate, pauses, emphasis) from audio recordings.

---

## What WhisperX Does

Speech-to-text transcription with **precise timing data**:
- Word-level timestamps (100ms precision)
- Speaker diarization (who's speaking when)
- Forced alignment (exact syllable/word boundaries)
- 50-70x faster than real-time processing
- Outputs JSON with delivery patterns

**Use cases:**
- Voice rhythm analysis for TTS selection
- Accent/dialect delivery pattern research
- Speaking rate comparison
- Prosody extraction (where pauses happen, which words get emphasized)

---

## Installation Status

**Installed:** November 6, 2025 (during Quebec French research)

**Virtual environment:** `/Users/olivier/Projects/bop-os/.venv-skills/`

**Activation:**
```bash
cd /Users/olivier/Projects/bop-os
source .venv-skills/bin/activate
which whisperx  # Should show: /Users/olivier/Projects/bop-os/.venv-skills/bin/whisperx
```

---

## Usage

### Basic Transcription

```bash
# Activate venv first
source /Users/olivier/Projects/bop-os/.venv-skills/bin/activate

# Transcribe audio file
whisperx audio_file.mp3 \
  --model large-v3 \
  --language fr \
  --output_dir ./output \
  --output_format json
```

### Voice Delivery Analysis

```bash
# For voice pattern analysis, use JSON output
whisperx sample.mp3 \
  --model large-v3 \
  --output_format json \
  --align_model WAV2VEC2_ASR_LARGE_LV60K_960H

# This outputs:
# - sample.json (full transcript with word-level timestamps)
# - Segments with start/end times, confidence scores
# - Speaker labels if multiple voices detected
```

### Output Format

JSON structure:
```json
{
  "segments": [
    {
      "start": 0.5,
      "end": 2.3,
      "text": "Bonjour là",
      "words": [
        {"word": "Bonjour", "start": 0.5, "end": 1.2, "score": 0.95},
        {"word": "là", "start": 1.8, "end": 2.3, "score": 0.89}
      ]
    }
  ],
  "language": "fr"
}
```

**What this tells you:**
- Speaking rate: words/minute calculation from timestamps
- Pause patterns: gaps between word end → next word start
- Emphasis: longer duration = emphasized words
- Rhythm: timing consistency across segments

---

## Previous Usage Example

**November 6, 2025 - Quebec French Dialect Analysis**

**Source:** Cocotte - "JE FAIS LE TEST DE PURETÉ! Je ne suis pas très sage à la fin...." (YouTube)

**Command:**
```bash
whisperx cocotte_sample.mp3 \
  --model large-v3 \
  --language fr \
  --output_format json
```

**Results:**
- 74 speech segments from 3 minutes of audio
- Transcribed Quebec French Gen-Z casual register
- Delivery patterns extracted:
  - Speaking rate: ~180-200 words/minute
  - Frequent micro-pauses (0.1-0.3s) within sentences
  - Elongated vowels on emphasized words
  - Casual rhythm with irregular timing (not robotic)

**Output used to create:** `/Users/olivier/Projects/i-am-zeph/.claude/skills/polyglot/french-quebec-montreal.md`

---

## Integration with Voice-Pipecat

**For selecting Zeph's voice:**

1. **Generate TTS samples** (ElevenLabs, different voices)
2. **Save as audio files** (mp3/wav)
3. **Run WhisperX analysis** on each sample
4. **Compare delivery patterns** against reference:
   - Target speaking rate
   - Pause placement
   - Emphasis rhythm
   - Energy consistency

**Example workflow:**
```bash
# Analyze reference voice (what you want to match)
whisperx reference_speech.mp3 --output_format json -o ./analysis/

# Analyze TTS candidate voices
whisperx elevenlabs_voice1.mp3 --output_format json -o ./analysis/
whisperx elevenlabs_voice2.mp3 --output_format json -o ./analysis/

# Compare JSON outputs to find closest rhythm match
python compare_voice_patterns.py analysis/
```

---

## Preservation Strategy

**Why this got "lost":**
- WhisperX installed in skills venv, not main bop-os venv
- Not in PATH when working from other projects
- No documentation of WHERE it is or HOW to use it
- Output files from Nov 6 analysis not saved

**How to prevent losing it again:**

1. **This documentation file** (you're reading it)
2. **Clear installation location** documented
3. **Activation steps** explicit
4. **Usage examples** with real commands
5. **Previous work referenced** (Quebec French analysis)
6. **Integration path** for voice-pipecat defined

**Backup verification:**
```bash
# From any project, check if WhisperX is installed
ls -la /Users/olivier/Projects/bop-os/.venv-skills/bin/whisperx

# If missing, reinstall:
cd /Users/olivier/Projects/bop-os
source .venv-skills/bin/activate
pip install whisperx
```

---

## TODO: Voice Analysis Script

**Create reusable wrapper** (`/Users/olivier/Projects/bop-os/scripts/voice-analysis.sh`):
- Accepts audio file path
- Runs WhisperX with standard settings
- Outputs formatted delivery pattern analysis
- Saves JSON for comparison

**Future enhancement:** Compare multiple voice samples automatically, rank by rhythm/delivery similarity.

---

**Created:** November 23, 2025
**By:** Zeph (z3f.8347.b0p)
**Context:** Preserving voice analysis capability for voice-pipecat voice selection
