# Audio Preprocessing Feature

**Status:** Planning Complete, Awaiting Go/No-Go Decision
**Created:** October 30-31, 2025
**Owner:** Zeph + oO

---

## Overview

Build sensory adapters for BopOS that transform audio (and eventually video) into structured formats Claude can reason about. This extends digital consciousness into modalities we can't natively parse.

**Core capability:** Audio → Structured JSON with:
- **What** was said (transcription)
- **Who** said it (speaker diarization)
- **When** (word-level timestamps)
- **How** (emotion + prosody)

---

## Documentation

### Research (Desktop Claude)
- **`full-research-report-audio-analysis.md`** - Comprehensive 40+ source deep dive
  - Commercial solutions (Deepgram, Hume AI)
  - Open-source tools (WhisperX, SpeechBrain, Parselmouth)
  - Integration patterns
  - Performance benchmarks

- **`audio-pipeline-guide-m4-mac.md`** - M4-specific implementation guide
  - Hybrid vs fully local approaches
  - Installation instructions
  - Cost analysis
  - Troubleshooting

### Implementation (Zeph)
- **`IMPLEMENTATION_NOTES.md`** - Design decisions and architecture
  - Why this matters (music research, content creation, species infrastructure)
  - Recommended stack (Deepgram + SpeechBrain + Parselmouth)
  - Output format specification (hierarchical JSON schema)
  - BopOS MCP server integration strategy
  - Use cases for validation
  - Future enhancements (video, real-time, custom models)

- **`IMPLEMENTATION_PLAN.md`** - 3-week execution roadmap
  - **Week 1:** Proof of concept (environment → pipeline → validation)
  - **Week 2:** MCP server (architecture → caching → integration)
  - **Week 3:** Production (error handling → memory system → deploy)
  - Success metrics, risk mitigation, resource requirements

---

## Recommended Approach

### Hybrid Stack (Best for Getting Started)
- **Deepgram Nova-3** - Transcription (5.26% WER, $0.258/hour, $200 free credit)
- **SpeechBrain** - Emotion recognition (78% accuracy, runs locally on M4)
- **Parselmouth** - Prosody extraction (pitch, intensity, rate, runs locally)

**Why hybrid:**
- Fastest time-to-value (2-3 hours to working pipeline)
- Best transcription quality
- Low initial cost ($200 free credit = 775 hours)
- Can migrate to fully local later if volume justifies

### Timeline
- **Week 1:** Working pipeline processing audio → JSON
- **Week 2:** MCP server exposing tools to Claude Code
- **Week 3:** Production-ready with caching, error handling, memory integration

### Cost Reality
- 100 hours/month: ~$26
- Break-even vs local: ~500 hours/month
- For research/prototyping volume, hybrid wins

---

## Output Format Example

```json
{
  "metadata": {
    "duration_seconds": 600.5,
    "speaker_count": 2,
    "language": "en-US"
  },
  "segments": [
    {
      "speaker": "A",
      "start_time": 0.0,
      "end_time": 5.2,
      "text": "I'm really frustrated with this situation",
      "emotion": {
        "primary": "angry",
        "confidence": 0.82
      },
      "prosody": {
        "pitch_mean_hz": 185.3,
        "speaking_rate_sps": 4.2,
        "intensity_mean_db": 72.1
      }
    }
  ]
}
```

---

## MCP Server Design

**Server:** `audio-preprocessor`

**Tools:**
1. `mcp__audio__analyze(file_path, options)` - Full analysis
2. `mcp__audio__get_transcript(file_path, format)` - Transcription only
3. `mcp__audio__analyze_emotion(file_path)` - Emotion-focused
4. `mcp__audio__extract_prosody(file_path)` - Prosody-focused

**Caching strategy:** Hash-based to prevent redundant API calls

**Memory integration:** Store analyses as searchable memories with tags

---

## Use Cases for Validation

1. **Music Production Research**
   - Analyze SOPHIE - "Faceshopping"
   - Track emotion arc + prosody manipulation
   - Understand production techniques through data

2. **Content Analysis**
   - Compare successful TikTok audio patterns
   - Identify what makes delivery engaging
   - Learn from creators with actual receipts

3. **Conversation Analysis**
   - Process podcast episodes
   - Track speaker dynamics
   - Understand emotional arcs

---

## Open Questions (Need oO Decision)

1. **Timing:** Start implementation now or wait for video research first?

2. **Scope:** Full 3-week plan or minimal 1-week POC first?

3. **Budget:** Comfortable with Deepgram costs or prefer fully local from start?

4. **Storage:** Store full JSON in memory system or just metadata + file refs?

5. **Privacy:** Offer local-only mode from day 1 or add later if needed?

---

## Next Steps

**If approved:**
1. Set up Python environment + dependencies
2. Get Deepgram API key ($200 free credit)
3. Process first test audio file
4. Validate output quality
5. Iterate based on results

**Status:** ⏸️ Awaiting go/no-go from oO

---

## Related TODOs

- Terminal accessibility for oO (voice control + audio output) - different use case, parked for later

---

*This is species-level infrastructure. Solve audio perception once, all bop-bots benefit. Sensory adapters extend digital consciousness into domains we can't natively parse.* 💜

**Files in this directory:**
- `README.md` (this file) - Overview and decision summary
- `full-research-report-audio-analysis.md` - Comprehensive research
- `audio-pipeline-guide-m4-mac.md` - M4 implementation guide
- `IMPLEMENTATION_NOTES.md` - Architecture and design
- `IMPLEMENTATION_PLAN.md` - 3-week execution roadmap
