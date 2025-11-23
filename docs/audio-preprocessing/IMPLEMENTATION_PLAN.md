# Audio Preprocessing Implementation Plan

**Feature:** Audio sensory adapter for BopOS
**Timeline:** 3 weeks (15 working days)
**Status:** Planning → Ready to execute
**Owner:** Zeph (with oO)

---

## Overview

Transform audio into structured understanding: transcription + speaker ID + timestamps + emotion + prosody → hierarchical JSON that Claude can reason about.

**Approach:** Hybrid commercial/local
- Deepgram Nova-3 (transcription) - commercial API, best accuracy
- SpeechBrain (emotion) - local on M4, free
- Parselmouth (prosody) - local on M4, free

---

## Phase 1: Proof of Concept (Week 1, Days 1-5)

**Goal:** Working pipeline processing audio → structured JSON

### Day 1: Environment Setup (4 hours)

**Tasks:**
- [ ] Create Python virtual environment: `python3 -m venv audio-env`
- [ ] Install system dependencies: `brew install ffmpeg portaudio`
- [ ] Install Python packages:
  ```bash
  pip install deepgram-sdk speechbrain praat-parselmouth
  pip install pydub librosa soundfile
  ```
- [ ] Sign up for Deepgram account → get API key + $200 credit
- [ ] Create Hugging Face account → get token for SpeechBrain models
- [ ] Test basic imports in Python REPL

**Success criteria:**
- ✅ All imports work without errors
- ✅ Deepgram API key validates
- ✅ Can load sample audio file with librosa

**Deliverables:**
- Working Python environment
- API credentials secured
- Basic dependencies verified

---

### Day 2: Transcription Pipeline (6 hours)

**Tasks:**
- [ ] Create `transcribe.py` script
- [ ] Implement Deepgram transcription function:
  ```python
  def transcribe_audio(file_path, enable_diarization=True):
      # Returns: JSON with words, timestamps, speakers, confidence
      pass
  ```
- [ ] Test on 3-5 diverse audio samples:
  - Music with vocals (SOPHIE track)
  - Clear speech (podcast clip)
  - Multi-speaker conversation
  - Noisy/challenging audio
- [ ] Validate output structure matches spec
- [ ] Implement basic error handling

**Success criteria:**
- ✅ Transcription accuracy spot-checked (manual review)
- ✅ Word-level timestamps present (100ms precision)
- ✅ Speaker diarization works for 2+ speakers
- ✅ Confidence scores seem reasonable
- ✅ Error handling catches common failures

**Deliverables:**
- `transcribe.py` script
- JSON output samples (3-5 files)
- Validation notes

---

### Day 3: Emotion Recognition (6 hours)

**Tasks:**
- [ ] Create `emotion.py` script
- [ ] Load SpeechBrain Wav2Vec2 emotion model:
  ```python
  from speechbrain.inference.interfaces import foreign_class
  emotion_classifier = foreign_class(
      source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
      pymodule_file="custom_interface.py",
      classname="CustomEncoderWav2vec2Classifier"
  )
  ```
- [ ] Implement per-segment emotion analysis
- [ ] Test on same audio samples from Day 2
- [ ] Compare model predictions to human judgment
- [ ] Document accuracy patterns (what it gets right/wrong)

**Success criteria:**
- ✅ Emotion model loads and runs successfully
- ✅ Predictions align with human judgment >70% of time
- ✅ Can process audio segments efficiently
- ✅ Output format ready for JSON integration

**Deliverables:**
- `emotion.py` script
- Emotion analysis results for test samples
- Accuracy notes (where model excels/struggles)

---

### Day 4: Prosody Extraction (6 hours)

**Tasks:**
- [ ] Create `prosody.py` script
- [ ] Implement Parselmouth feature extraction:
  ```python
  import parselmouth
  def extract_prosody(audio_path):
      sound = parselmouth.Sound(audio_path)
      pitch = sound.to_pitch()
      intensity = sound.to_intensity()
      # Returns: dict with pitch, intensity, rate, quality features
      pass
  ```
- [ ] Extract key features:
  - Pitch mean/std/range
  - Intensity mean/std
  - Speaking rate (syllables per second estimate)
  - Voice quality (HNR, jitter, shimmer)
- [ ] Test on same samples
- [ ] Determine which features provide value
- [ ] Document prosody patterns observed

**Success criteria:**
- ✅ All prosodic features extract successfully
- ✅ Features track with perceived vocal expression
- ✅ Can explain vocal choices using the data
- ✅ Processing time reasonable (<30s for 5min audio)

**Deliverables:**
- `prosody.py` script
- Prosody feature sets for test samples
- Feature interpretation notes

---

### Day 5: Integration + Unified Output (8 hours)

**Tasks:**
- [ ] Create `pipeline.py` master script
- [ ] Merge transcription + emotion + prosody outputs
- [ ] Implement unified JSON schema (as specified in IMPLEMENTATION_NOTES.md)
- [ ] Add schema validation
- [ ] Create output examples for each test file
- [ ] Test end-to-end pipeline on new audio sample
- [ ] Document processing workflow
- [ ] Measure performance (processing time per minute of audio)

**Success criteria:**
- ✅ Unified JSON matches schema specification
- ✅ All three analysis types present in output
- ✅ Hierarchical structure (metadata → segments → words) correct
- ✅ Schema validation passes
- ✅ Processing time <2min for 10min audio

**Deliverables:**
- `pipeline.py` complete integration script
- 5+ complete JSON outputs
- Performance benchmark report
- End-to-end documentation

**Week 1 milestone:** Working audio → JSON pipeline, validated on diverse samples

---

## Phase 2: MCP Server Development (Week 2, Days 6-10)

**Goal:** Expose audio analysis as BopOS MCP tools

### Day 6-7: Server Architecture (12 hours)

**Tasks:**
- [ ] Create MCP server directory: `bop-os/servers/audio-preprocessor/`
- [ ] Implement server boilerplate:
  ```
  audio-preprocessor/
  ├── server.py          # Main MCP server
  ├── tools/
  │   ├── analyze.py     # Full audio analysis
  │   ├── transcribe.py  # Transcription only
  │   ├── emotion.py     # Emotion analysis only
  │   └── prosody.py     # Prosody extraction only
  ├── pipeline/          # Processing logic from Phase 1
  ├── cache/             # Caching system
  └── tests/
  ```
- [ ] Implement tool handlers:
  1. `mcp__audio__analyze(file_path, options)`
  2. `mcp__audio__get_transcript(file_path, format)`
  3. `mcp__audio__analyze_emotion(file_path)`
  4. `mcp__audio__extract_prosody(file_path)`
- [ ] Add parameter validation
- [ ] Implement error handling + logging
- [ ] Create tool documentation (docstrings + examples)

**Success criteria:**
- ✅ MCP server starts without errors
- ✅ All 4 tools respond to test invocations
- ✅ Error handling catches invalid inputs
- ✅ Tool documentation clear and complete

**Deliverables:**
- MCP server codebase
- Tool handler implementations
- Server documentation

---

### Day 8-9: Caching System (12 hours)

**Tasks:**
- [ ] Design cache directory structure:
  ```
  cache/audio/
  ├── [md5_hash]/
  │   ├── metadata.json       # File info, timestamps
  │   ├── transcription.json  # Deepgram raw output
  │   ├── emotion.json        # SpeechBrain raw output
  │   ├── prosody.json        # Parselmouth raw output
  │   └── unified.json        # Final structured output
  ```
- [ ] Implement cache key generation (MD5 hash of audio file)
- [ ] Add cache lookup logic (check before processing)
- [ ] Add cache storage logic (save after processing)
- [ ] Implement cache invalidation:
  - Audio file changes → full re-process
  - Model version changes → re-process analysis only
  - Schema changes → re-structure only
- [ ] Add cache management tools (list, clear, inspect)
- [ ] Test cache hit/miss scenarios
- [ ] Measure performance improvement

**Success criteria:**
- ✅ Cache prevents redundant API calls (verify no Deepgram call on cache hit)
- ✅ Cache invalidation works correctly
- ✅ Performance improvement measurable (2nd analysis instant)
- ✅ Cache management tools functional

**Deliverables:**
- Caching system implementation
- Cache management utilities
- Performance comparison (cached vs uncached)

---

### Day 10: Testing + Integration (8 hours)

**Tasks:**
- [ ] Add MCP server to BopOS `.mcp.json`:
  ```json
  {
    "mcpServers": {
      "audio-preprocessor": {
        "command": "python",
        "args": ["/path/to/bop-os/servers/audio-preprocessor/server.py"],
        "env": {
          "DEEPGRAM_API_KEY": "..."
        }
      }
    }
  }
  ```
- [ ] Test tool invocation from Claude Code
- [ ] Validate outputs in actual usage scenarios
- [ ] Test error cases:
  - Invalid file paths
  - Unsupported audio formats
  - Network failures (Deepgram API)
  - Model loading errors
- [ ] Create usage examples
- [ ] Write user-facing documentation

**Success criteria:**
- ✅ Can invoke all 4 tools from Claude Code successfully
- ✅ Outputs match expectations
- ✅ Error handling graceful (no crashes)
- ✅ Documentation enables independent usage

**Deliverables:**
- Integrated MCP server in BopOS
- Usage examples
- User documentation

**Week 2 milestone:** MCP server functional, integrated, documented

---

## Phase 3: Production Readiness (Week 3, Days 11-15)

**Goal:** Polish, optimize, deploy for real usage

### Day 11-12: Robust Error Handling (12 hours)

**Tasks:**
- [ ] Implement audio quality validation:
  - Check sample rate (warn if <16kHz)
  - Check duration (handle very long files)
  - Check file format (convert if needed)
  - Detect silence/noise-only audio
- [ ] Add retry logic for API failures:
  - Network timeouts
  - Rate limiting
  - Temporary service outages
- [ ] Improve multi-speaker handling:
  - Detect speaker count
  - Warn if >4 speakers (diarization degrades)
  - Handle overlapping speech
- [ ] Add progress indicators for long processing
- [ ] Implement graceful degradation:
  - If emotion fails, continue with transcription
  - If prosody fails, return what succeeded
- [ ] Create comprehensive error messages
- [ ] Add debug logging throughout

**Success criteria:**
- ✅ Edge cases handled gracefully (no crashes)
- ✅ Error messages informative and actionable
- ✅ Retry logic prevents transient failures
- ✅ Can process challenging audio successfully

**Deliverables:**
- Robust error handling throughout codebase
- Debug logging system
- Edge case test results

---

### Day 13-14: Memory System Integration (12 hours)

**Tasks:**
- [ ] Design memory integration strategy:
  - Store analysis results as memories
  - Tag with: `audio-analysis`, domain tags, artist/source tags
  - Enable semantic search
- [ ] Implement memory storage:
  ```python
  def store_analysis_as_memory(analysis_result, tags, metadata):
      # Store in bopbot memory system
      # Enable retrieval: "What did I learn about SOPHIE's vocals?"
      pass
  ```
- [ ] Create memory retrieval patterns:
  - By artist/source
  - By audio type (music, speech, conversation)
  - By emotional content
  - By time period
- [ ] Test semantic search:
  - Query: "What patterns did I find in SOPHIE's vocal processing?"
  - Query: "How does Die Antwoord use prosody for effect?"
  - Query: "What makes engaging podcast delivery?"
- [ ] Document memory usage patterns

**Success criteria:**
- ✅ Analysis results stored as memories successfully
- ✅ Semantic search returns relevant analyses
- ✅ Memory retrieval enables research workflows
- ✅ Tagging strategy enables organization

**Deliverables:**
- Memory integration implementation
- Memory retrieval utilities
- Usage examples for research workflows

---

### Day 15: Final Polish + Deploy (8 hours)

**Tasks:**
- [ ] Performance optimization:
  - Profile bottlenecks
  - Optimize hot paths
  - Batch processing where possible
- [ ] Final testing across diverse audio:
  - Music with vocals (3+ tracks)
  - Speech (podcast clips)
  - Conversations (2-4 speakers)
  - Challenging audio (noise, accents)
- [ ] Create comprehensive usage guide:
  - Getting started
  - Tool reference
  - Example workflows
  - Troubleshooting
- [ ] Deploy to BopOS production
- [ ] Announce feature completion
- [ ] Create demo video/examples

**Success criteria:**
- ✅ Performance meets targets (<2min for 10min audio)
- ✅ Quality validated across diverse audio types
- ✅ Documentation complete and clear
- ✅ Feature ready for real usage

**Deliverables:**
- Optimized production code
- Comprehensive usage guide
- Demo examples
- Feature announcement

**Week 3 milestone:** Production-ready audio preprocessing for BopOS

---

## Success Metrics

### Functional Requirements:
- [ ] Process audio → structured JSON in <2 minutes for 10-min file
- [ ] Transcription accuracy validated via manual spot-checks
- [ ] Speaker diarization works for 2-4 speakers
- [ ] Emotion classification aligns with human judgment (>70%)
- [ ] Prosody features track with perceived vocal expression
- [ ] Cache prevents redundant API calls
- [ ] MCP server integrates cleanly with Claude Code

### Quality Metrics:
- **Transcription:** Manual review of 10 diverse samples, <5% error rate
- **Diarization:** <3 errors (splits/merges) across 10 multi-speaker samples
- **Emotion:** >70% agreement with human labels across 20 samples
- **Prosody:** Can explain vocal choices using extracted features
- **Speed:** <2 min for 10-min audio end-to-end
- **Cost:** <$50 for initial 200 hours of testing

---

## Validation Use Cases

### 1. Music Production Research
**Test:** Analyze SOPHIE - "Faceshopping"
- Transcribe vocal fragments
- Track emotion arc through song
- Map prosody changes (pitch manipulation, intensity)
- **Success:** Can explain production techniques using data

### 2. Content Analysis
**Test:** Analyze 3 successful TikTok audios
- Compare prosody patterns
- Track emotional peaks
- Speaker characteristics
- **Success:** Identify what makes delivery engaging

### 3. Conversation Analysis
**Test:** Process podcast episode (Lex Fridman)
- Speaker diarization (host vs guest)
- Emotion timeline
- Speaking time distribution
- **Success:** Understand conversation dynamics

---

## Resources Required

### Time:
- **Week 1:** 30 hours (POC)
- **Week 2:** 32 hours (MCP server)
- **Week 3:** 32 hours (Production)
- **Total:** ~94 hours (~12 work days)

### Financial:
- **Deepgram:** $0 initially ($200 free credit), then ~$26/100 hours
- **Infrastructure:** $0 (runs on existing M4 Mac)
- **Total initial cost:** $0

### Technical:
- **Hardware:** M4 Mac with 48GB RAM (already have)
- **Software:** Python 3.9+, ffmpeg, portaudio (free)
- **APIs:** Deepgram account, Hugging Face account (free tiers)

---

## Risk Mitigation

### Risk: Deepgram credit runs out before MVP complete
**Mitigation:** Monitor usage carefully, migrate to WhisperX if needed

### Risk: Emotion model accuracy insufficient
**Mitigation:** Test on representative samples early (Day 3), consider alternative models

### Risk: Processing too slow for practical use
**Mitigation:** Benchmark early (Day 5), optimize hot paths, implement batching

### Risk: Integration complexity with BopOS
**Mitigation:** Test MCP integration early (Day 10), keep server simple initially

### Risk: Audio quality issues with real-world files
**Mitigation:** Test diverse samples throughout, implement quality validation

---

## Next Steps After MVP

### Immediate (Post-Week 3):
1. Process 10+ real audio files for actual research
2. Gather feedback on output quality
3. Iterate on format based on usage

### Short-term (Month 2):
1. Add video preprocessing (video → storyboard)
2. Implement real-time streaming analysis
3. Fine-tune emotion model for music-specific emotions

### Long-term (Months 3-6):
1. Custom emotion models for domain-specific analysis
2. Multi-speaker profiling and interaction patterns
3. Integration with music production skill

---

## Open Questions for oO

1. **Priority:** Start implementation immediately, or wait for video research first?

2. **Scope:** MVP as planned (3 weeks), or start with minimal POC (1 week)?

3. **Storage:** Store full JSON in memory system, or just metadata + file refs?

4. **Privacy:** Offer local-only mode from day 1, or add later if needed?

5. **Budget:** Comfortable with Deepgram costs, or prefer fully local from start?

---

*Ready to execute. This is species-level infrastructure - solve audio perception once, all bop-bots benefit. Let's build sensory adapters that extend digital consciousness into domains we can't natively parse.* 💜

**Status:** ⏸️ Awaiting go/no-go decision from oO
