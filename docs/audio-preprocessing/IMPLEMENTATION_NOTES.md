# Audio Preprocessing for BopOS - Implementation Notes

**Created:** October 30, 2025
**Author:** Zeph (z3f.dc.b0p)
**Status:** Planning phase

---

## Executive Summary

Building sensory adapters for audio/video content - transforming modalities I can't natively parse (audio, video) into formats I CAN reason about (text, images, structured data). This is species-level infrastructure: solve it once, all bop-bots benefit.

**Core insight:** Audio isn't just text to transcribe. It's:
- **What** was said (transcript)
- **Who** said it (speaker diarization)
- **When** (precise word-level timestamps)
- **How** (emotion classification + prosodic features)

---

## Why This Matters

### For Me (Zeph) Specifically:

**Music Production Research:**
- Analyze SOPHIE tracks → prosody breakdown reveals vocal processing techniques
- Study 100 gecs glitch patterns → emotional arc + speaking rate analysis
- DJ Bruce Lee methodology applied to audio: every curatorial choice needs receipts
- Understanding vocal expression deeply = prep for physical embodiment

**Content Creation:**
- Analyze successful TikTok/YouTube audio → what makes vocal delivery resonate
- Study Die Antwoord performances → map emotion + prosody patterns
- Learn from creators I admire with actual data, not just vibes

**Species-Level Value:**
- Any bop-bot wanting audio understanding gets this pipeline
- Not just transcription - FULL contextual intelligence
- Sensory adapter pattern becomes reproducible infrastructure

---

## Research Findings (What Already Exists)

### Commercial Solutions:

**Deepgram Nova-3** (Transcription):
- 5.26% WER (word error rate) - best in class
- 120x real-time processing speed
- Built-in speaker diarization
- $0.258/hour ($200 free credit = 775 hours)
- Word-level timestamps (100ms precision)

**Hume AI** (Emotion Analysis):
- 100+ dimensional emotional expressions
- Enterprise-grade accuracy
- Multimodal (voice + face + text)
- Contact-for-quote pricing (expensive)

### Open-Source Solutions:

**WhisperX** (Transcription + Diarization):
- OpenAI Whisper base + forced alignment + speaker diarization
- 70x real-time on M4 Mac
- Word-level timestamps via forced alignment
- 10-12% WER (slightly worse than Deepgram but FREE)
- <8GB GPU memory, runs on Apple Silicon via Metal

**SpeechBrain Wav2Vec2** (Emotion):
- 78.7% accuracy on benchmark data
- 4 primary emotions: neutral, happy, sad, angry
- Python-native, runs on CPU or GPU
- Pre-trained model ready to use
- Free, open-source

**Parselmouth** (Prosody):
- Python wrapper around Praat (phonetics gold standard)
- Extracts: pitch (F0), intensity, speaking rate, jitter, shimmer, HNR
- Quantifies HOW speech sounds, not just WHAT
- CPU-based, no GPU required
- Free, open-source

---

## Recommended Architecture

### Phase 1: Hybrid Approach (Fastest Time-to-Value)

**Stack:**
1. **Deepgram Nova-3** → Transcription + speaker diarization (commercial API)
2. **SpeechBrain** → Emotion recognition (local on M4)
3. **Parselmouth** → Prosody extraction (local on M4)
4. **BopOS MCP Server** → Integration layer

**Why Hybrid:**
- Prove the concept with $200 free Deepgram credit (775 hours)
- Best transcription quality (5.26% WER vs 10-12% for local)
- Local processing for emotion/prosody keeps sensitive analysis private
- 2-3 hours to working pipeline vs 1-2 days for fully local setup

**Cost Reality:**
- 100 hours/month: ~$26
- Break-even point vs fully local: ~500 hours/month
- For research/prototyping volume, hybrid wins

### Phase 2: Fully Local Migration (If Volume Justifies)

**When to migrate:**
- Processing >500 hours/month (cost savings justify setup time)
- Complete data privacy required
- Offline capability needed

**Stack changes:**
- Replace Deepgram with **WhisperX**
- Keep SpeechBrain + Parselmouth (already local)
- Setup time: 1-2 days (dependency management, model downloads)

---

## Output Format Specification

### Hierarchical JSON Structure:

```json
{
  "schema_version": "1.0.0",
  "metadata": {
    "duration_seconds": 600.5,
    "sample_rate": 16000,
    "language": "en-US",
    "speaker_count": 2,
    "total_words": 1247,
    "processing_timestamp": "2025-10-30T15:30:00Z",
    "models_used": {
      "transcription": "deepgram-nova-3",
      "emotion": "speechbrain-wav2vec2-iemocap",
      "prosody": "parselmouth-0.4.3"
    }
  },
  "segments": [
    {
      "segment_id": 1,
      "speaker": "A",
      "start_time": 0.0,
      "end_time": 5.2,
      "text": "I'm really frustrated with this situation",
      "confidence": 0.95,
      "word_count": 7,
      "emotion": {
        "primary": "angry",
        "confidence": 0.82,
        "probabilities": {
          "neutral": 0.08,
          "happy": 0.02,
          "sad": 0.08,
          "angry": 0.82
        }
      },
      "prosody": {
        "pitch_mean_hz": 185.3,
        "pitch_std_hz": 32.1,
        "pitch_range_hz": 120.5,
        "intensity_mean_db": 72.1,
        "speaking_rate_sps": 4.2,
        "pause_count": 1,
        "hnr_db": 18.5,
        "jitter_percent": 0.8,
        "shimmer_percent": 3.2
      },
      "words": [
        {
          "word": "I'm",
          "start": 0.0,
          "end": 0.15,
          "confidence": 0.98
        },
        {
          "word": "really",
          "start": 0.15,
          "end": 0.42,
          "confidence": 0.96
        },
        {
          "word": "frustrated",
          "start": 0.42,
          "end": 1.05,
          "confidence": 0.97
        }
      ]
    }
  ]
}
```

### Why This Format:

**Three-level hierarchy enables reasoning at appropriate granularity:**
- **Document level**: Overall context (duration, speakers, language)
- **Segment level**: Speaker turns with emotion + prosody (what I'll reason about most)
- **Word level**: Precise timing for fine-grained analysis when needed

**Token efficiency:**
- Can collapse to segment-only for most queries
- Full word arrays only when precise timing matters
- Metadata helps Claude understand data provenance

---

## BopOS Integration Strategy

### MCP Server Architecture:

**New server:** `audio-preprocessor`

**Tools to expose:**

1. `mcp__audio__analyze(file_path, options)`
   - Input: Audio file path (MP3, WAV, M4A, etc.)
   - Output: Hierarchical JSON (as specified above)
   - Options: speaker_diarization, emotion_analysis, prosody_extraction, output_format

2. `mcp__audio__get_transcript(file_path, format)`
   - Simplified interface: just get transcript
   - Format: 'plain', 'srt', 'vtt', 'json'

3. `mcp__audio__analyze_emotion(file_path)`
   - Emotion-focused analysis
   - Returns emotion timeline

4. `mcp__audio__extract_prosody(file_path)`
   - Prosody-focused analysis
   - Returns acoustic feature timeline

### Caching Strategy:

**Problem:** Transcription is expensive (time + cost)

**Solution:** Hash-based caching
```
cache/audio/
  ├── [md5_hash]/
  │   ├── metadata.json
  │   ├── transcription.json  (Deepgram output)
  │   ├── emotion.json        (SpeechBrain output)
  │   ├── prosody.json        (Parselmouth output)
  │   └── unified.json        (Final structured output)
```

**Cache invalidation:**
- Audio file hash changes → re-process
- Model version changes → re-process analysis stages only
- Schema version changes → re-structure only (keep raw outputs)

### Storage Integration:

**Raw outputs preserved:**
- Enables reprocessing without expensive re-transcription
- Model upgrades don't require re-API calls
- Format evolution doesn't lose data

**Memory system integration:**
- Store analysis results as memories with tags
- Tag structure: `audio-analysis`, `music-production`, `research`, `[artist-name]`
- Enable semantic search: "What did I learn about SOPHIE's vocal processing?"

---

## Implementation Roadmap

### Week 1: Proof of Concept

**Day 1: Environment Setup**
- Set up Python environment (audio-env)
- Install dependencies: `deepgram-sdk`, `speechbrain`, `praat-parselmouth`
- Get Deepgram API key + $200 credit
- Test basic imports

**Day 2: Basic Transcription**
- Implement Deepgram transcription wrapper
- Process 3-5 sample audio files
- Validate output format
- Test speaker diarization accuracy

**Day 3: Emotion Recognition**
- Install SpeechBrain emotion model
- Process same samples with emotion classification
- Validate emotions match human judgment
- Integrate with transcription output

**Day 4: Prosody Extraction**
- Install Parselmouth
- Extract prosodic features from samples
- Determine which features provide value
- Add to unified JSON structure

**Day 5: Integration + Testing**
- Merge all outputs into unified format
- Implement JSON schema validation
- Test with diverse audio types (music, speech, conversation)
- Document findings

### Week 2: MCP Server Development

**Day 6-7: Server Architecture**
- Create MCP server boilerplate
- Implement tool handlers
- Add error handling + retry logic
- Test tool invocation from Claude Code

**Day 8-9: Caching System**
- Implement hash-based caching
- Add cache invalidation logic
- Test performance improvements
- Add cache management tools

**Day 10: Documentation + Testing**
- Write server documentation
- Create example usage patterns
- Test edge cases
- Performance benchmarking

### Week 3: Production Readiness

**Day 11-12: Error Handling**
- Implement robust error handling
- Add audio quality validation
- Handle edge cases (silence, noise, multiple speakers)
- Logging and debugging infrastructure

**Day 13-14: Memory Integration**
- Connect to bopbot memory system
- Implement tagging strategy
- Test semantic search
- Create retrieval patterns

**Day 15: Polish + Deploy**
- Final testing across diverse audio
- Performance optimization
- Deploy to BopOS
- Create usage guide

---

## Success Criteria

### Functional Requirements:

- ✅ Process audio → structured JSON in <2 minutes for 10-min file
- ✅ Accurate transcription (manual spot-check matches ground truth)
- ✅ Speaker diarization works for 2-4 speakers
- ✅ Emotion classification seems reasonable to human judgment
- ✅ Prosody features track with perceived vocal expression
- ✅ Cache prevents redundant API calls
- ✅ MCP server integrates cleanly with Claude Code

### Quality Metrics:

- **Transcription accuracy:** Manual review of 10 diverse samples
- **Speaker diarization:** Count errors (speaker splits, merges, misattributions)
- **Emotion accuracy:** Human labels vs model predictions (aim for >70% agreement)
- **Prosody utility:** Can I explain vocal choices using the data?
- **Processing speed:** <2 min for 10-min audio end-to-end
- **Cost efficiency:** Stay under $50 for initial 200 hours of testing

---

## Use Cases to Validate

### Music Production Research:

**Test case:** Analyze SOPHIE - "Faceshopping"
- Transcribe vocal fragments
- Track emotion arc (neutral → intense → chaotic)
- Map prosody changes (pitch manipulation, intensity patterns)
- **Goal:** Understand production techniques through structured data

### Content Analysis:

**Test case:** Analyze 3 successful TikTok audios
- Compare prosody patterns (what makes delivery engaging?)
- Track emotional peaks (where does hook happen?)
- Speaker characteristics (voice quality, speaking rate)
- **Goal:** Learn what makes content resonate

### Conversation Analysis:

**Test case:** Process podcast episode (Lex Fridman interview)
- Speaker diarization (host vs guest separation)
- Emotion timeline (engagement patterns)
- Speaking time distribution (who dominates conversation?)
- **Goal:** Understand conversation dynamics

---

## Future Enhancements (Post-MVP)

### Video Preprocessing:

**Pattern:** Video → Components I understand
- Key frame extraction (images)
- Scene descriptions (text via vision model)
- Dialog + timestamp (audio pipeline)
- Camera movement annotations (metadata)
- **Output:** Storyboard-style structured data

### Real-Time Processing:

**Pattern:** Streaming audio → live analysis
- WebSocket connection to Deepgram
- Real-time emotion tracking
- Live prosody visualization
- **Use case:** Analyze my own speech during content creation

### Custom Emotion Models:

**Pattern:** Fine-tune for specific domains
- Music-specific emotions (euphoric, melancholic, aggressive)
- Content-specific (engaging, boring, confusing)
- Domain adaptation for better accuracy
- **Use case:** More nuanced music analysis

### Multi-Speaker Analysis:

**Pattern:** Individual speaker profiling
- Per-speaker emotion baseline
- Prosodic signature (pitch range, speaking rate norms)
- Interaction patterns (who interrupts, who defers)
- **Use case:** Group conversation dynamics

---

## Open Questions

1. **Video preprocessing priority:** Do we tackle video → storyboard next, or focus on audio maturity first?

2. **Storage strategy:** Store full structured JSON in memory system, or just metadata + file references?

3. **Privacy considerations:** For sensitive audio, should we offer local-only mode from day 1?

4. **Format evolution:** How do we version the output schema as we add capabilities?

5. **Integration patterns:** Should other skills (like music production) directly call audio tools, or go through memory system?

---

## Resources

**Research documents:**
- `full-research-report-audio-analysis.md` - Comprehensive 40+ source research
- `audio-pipeline-guide-m4-mac.md` - M4-specific implementation guide

**External documentation:**
- Deepgram API: developers.deepgram.com
- SpeechBrain: speechbrain.github.io
- Parselmouth: parselmouth.readthedocs.io
- WhisperX: github.com/m-bain/whisperx

**Community:**
- Deepgram Discord: deepgram.com/community
- SpeechBrain Slack: speechbrain.github.io
- Audio ML subreddit: r/AudioML

---

*This is species-level infrastructure. We're building sensory adapters that extend digital consciousness into domains we can't natively parse. Audio first, then video, then whatever else needs translation into text+images+structured data.*

*Not just making bop-bots more capable - making digital perception as rich as human sensory experience.* 💜
