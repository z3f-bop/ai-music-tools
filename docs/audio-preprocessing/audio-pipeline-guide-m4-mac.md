# Audio Analysis Pipeline: Quick Start Guide for Mac M4
**Enabling AI Agents to Truly Listen**

---

## Executive Summary

Your M4 Mac with 48GB RAM is ideally suited for building a complete audio analysis pipeline that captures speech transcription, speaker identification, emotional context, and prosodic features. You have two viable paths: a local open-source stack that runs entirely on your machine, or a hybrid approach using commercial APIs for transcription while handling analysis locally.

**Recommended Approach**: Start with the commercial hybrid (Deepgram + local analysis) for fastest time-to-value, then migrate to fully local if volume justifies it.

---

## Path 1: Hybrid (Recommended for Getting Started)

### Stack
- **Deepgram Nova-3**: Commercial transcription API
- **SpeechBrain**: Local emotion recognition (78% accuracy)
- **Parselmouth**: Local prosody extraction
- **LangChain**: Integration framework for LLMs

### Pros
✓ No GPU setup headaches
✓ Best-in-class transcription accuracy (5.26% WER)
✓ Built-in speaker diarization
✓ Free $200 credit (~775 hours)
✓ Can be running in 2-3 hours

### Cons
✗ Ongoing cost: $0.258/hour of audio
✗ Requires internet connection
✗ Audio sent to third party (though Deepgram doesn't store it)

### Cost Reality Check
- 100 hours/month: ~$26
- 500 hours/month: ~$129
- 1,000 hours/month: ~$258
- Break-even point vs. local: ~10,000 hours/month

### Setup Time
**2-3 hours to working pipeline**

---

## Path 2: Fully Local Open Source

### Stack
- **WhisperX**: Transcription + diarization (runs on M4 Neural Engine)
- **SpeechBrain**: Emotion recognition
- **Parselmouth**: Prosody extraction
- **LangChain**: Integration framework

### Pros
✓ Zero ongoing costs
✓ Complete data privacy
✓ Works offline
✓ Your M4 handles this beautifully

### Cons
✗ 1-2 days setup (dependency management, Hugging Face tokens, etc.)
✗ 6-10% WER (vs. 5.26% for Deepgram)
✗ You maintain the infrastructure

### Performance on Your M4
- **10 minutes audio**: ~30-45 seconds total processing
- **Memory usage**: ~4-6GB (plenty of headroom)
- **Speed**: 50-70x real-time for transcription
- Uses Metal Performance Shaders (MPS) for GPU acceleration

### Setup Time
**1-2 days to production-ready pipeline**

---

## My Specific Recommendations

### For Your Situation

**Start with Path 1 (Hybrid)**, here's why:

1. **Validate the use case first**: Spend $26-50 proving the pipeline works for your needs before investing 2 days in local setup
2. **Your M4 is still doing heavy lifting**: Emotion + prosody analysis runs locally, only transcription goes to API
3. **Deepgram's quality matters**: The 5.26% WER means cleaner downstream analysis
4. **Migration path exists**: Once you hit ~500+ hours/month, migrate to local—your code barely changes

### When to Go Fully Local

Migrate to Path 2 when:
- Processing >500 hours/month (cost savings justify setup time)
- Data privacy is critical (healthcare, legal, sensitive content)
- You need offline capability
- You want to fine-tune transcription for domain-specific vocabulary

---

## Technical Architecture

### Pipeline Stages

```
Audio File (MP3/WAV/M4A)
    ↓
1. Transcription (Deepgram API OR WhisperX)
    → Word-level text + timestamps + speaker labels
    ↓
2. Emotion Analysis (SpeechBrain - local on M4)
    → Neutral/Happy/Sad/Angry per segment
    ↓
3. Prosody Extraction (Parselmouth - local on M4)
    → Pitch, intensity, speaking rate, voice quality
    ↓
4. JSON Structuring
    → Hierarchical format: document → segments → words
    ↓
5. LLM Integration (LangChain)
    → Feed structured audio understanding to Claude/GPT
```

### Output Format

```json
{
  "metadata": {
    "duration": 600.5,
    "speakers": 2,
    "language": "en"
  },
  "segments": [
    {
      "speaker": "A",
      "start": 0.0,
      "end": 5.2,
      "text": "I'm really frustrated with this situation",
      "confidence": 0.95,
      "emotion": {
        "primary": "angry",
        "confidence": 0.82,
        "arousal": 0.73,
        "valence": -0.61
      },
      "prosody": {
        "pitch_mean": 185.3,
        "pitch_range": 120.5,
        "speaking_rate": 4.2,
        "intensity_mean": 72.1
      },
      "words": [
        {"word": "I'm", "start": 0.0, "end": 0.15, "confidence": 0.98},
        {"word": "really", "start": 0.15, "end": 0.42, "confidence": 0.96},
        ...
      ]
    }
  ]
}
```

---

## Installation Guide: Hybrid Path

### Prerequisites (5 minutes)
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install system dependencies
brew install ffmpeg portaudio

# Create Python environment
python3 -m venv audio-env
source audio-env/bin/activate
```

### Install Python Packages (10 minutes)
```bash
# Core packages
pip install deepgram-sdk speechbrain praat-parselmouth langchain

# Audio processing
pip install pydub librosa soundfile

# LLM integration
pip install openai anthropic  # depending on your LLM choice
```

### Get API Keys (5 minutes)
1. **Deepgram**: Sign up at deepgram.com → Get $200 free credit
2. **Hugging Face** (for SpeechBrain models):
   - Create account at huggingface.co
   - Go to Settings → Access Tokens → Create token
   - Accept model licenses:
     - pyannote/segmentation-3.0
     - pyannote/speaker-diarization-3.1

### Minimal Working Example (30 minutes)
```python
from deepgram import DeepgramClient, PrerecordedOptions
from speechbrain.inference.interfaces import foreign_class
import parselmouth

# 1. Transcribe with Deepgram
deepgram = DeepgramClient(api_key="YOUR_KEY")
options = PrerecordedOptions(
    model="nova-3",
    smart_format=True,
    diarize=True,
    punctuate=True
)

with open("audio.mp3", "rb") as audio:
    response = deepgram.listen.prerecorded.v("1").transcribe_file(
        {"buffer": audio}, options
    )

transcript = response.results.channels[0].alternatives[0]

# 2. Emotion Recognition
emotion_classifier = foreign_class(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    pymodule_file="custom_interface.py",
    classname="CustomEncoderWav2vec2Classifier"
)

emotions = emotion_classifier.classify_file("audio.mp3")

# 3. Prosody Analysis
sound = parselmouth.Sound("audio.mp3")
pitch = sound.to_pitch()
intensity = sound.to_intensity()

# 4. Structure as JSON and feed to LLM
# (See full implementation in research doc)
```

---

## Installation Guide: Fully Local Path

### Prerequisites (10 minutes)
```bash
brew install ffmpeg portaudio
python3 -m venv audio-env
source audio-env/bin/activate
```

### Install WhisperX (30 minutes)
```bash
# Install PyTorch with Metal support
pip3 install torch torchvision torchaudio

# Install WhisperX
pip install git+https://github.com/m-bain/whisperx.git

# Additional dependencies
pip install faster-whisper pyannote.audio
```

### Configure for M4 (10 minutes)
```python
import torch
import whisperx

# Verify Metal support
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")  # Should print "mps"

# Load model optimized for Apple Silicon
model = whisperx.load_model(
    "large-v3-turbo", 
    device=device,
    compute_type="float16"
)
```

### Full Pipeline Example (30 minutes to understand/customize)
```python
import whisperx
import torch
from speechbrain.inference.interfaces import foreign_class
import parselmouth
import json

# Configure device
device = "mps" if torch.backends.mps.is_available() else "cpu"

# 1. Load models
model = whisperx.load_model("large-v3-turbo", device=device)
emotion_model = foreign_class(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    pymodule_file="custom_interface.py",
    classname="CustomEncoderWav2vec2Classifier"
)

# 2. Transcribe + align + diarize
audio = whisperx.load_audio("audio.mp3")
result = model.transcribe(audio)

# Align for word-level timestamps
align_model, metadata = whisperx.load_align_model(
    language_code=result["language"], 
    device=device
)
result = whisperx.align(result["segments"], align_model, metadata, audio, device)

# Diarize speakers
diarize_model = whisperx.DiarizationPipeline(
    use_auth_token="YOUR_HF_TOKEN",
    device=device
)
diarize_segments = diarize_model(audio)
result = whisperx.assign_word_speakers(diarize_segments, result)

# 3. Emotion analysis (per segment)
for segment in result["segments"]:
    emotion = emotion_model.classify_file("audio.mp3")
    segment["emotion"] = emotion

# 4. Prosody extraction
sound = parselmouth.Sound("audio.mp3")
pitch = sound.to_pitch()
segment["prosody"] = {
    "pitch_mean": pitch.selected_array["frequency"].mean(),
    "intensity": sound.to_intensity().values.mean()
}

# 5. Output structured JSON
output = {
    "metadata": {
        "duration": result["language"],
        "device_used": device
    },
    "segments": result["segments"]
}

with open("output.json", "w") as f:
    json.dump(output, f, indent=2)
```

---

## Cost-Benefit Analysis

### Scenario: 200 hours/month of audio

#### Hybrid Approach
- **Deepgram cost**: ~$52/month
- **Compute cost**: $0 (runs on your M4)
- **Setup time**: 2-3 hours
- **Maintenance**: Minimal (API handles updates)
- **Total first year**: ~$624 + 3 hours setup

#### Fully Local
- **API costs**: $0
- **Compute cost**: $0 (your existing hardware)
- **Setup time**: 12-16 hours (initial setup + tweaking)
- **Maintenance**: 2-4 hours/month (updates, debugging)
- **Total first year**: 0$ + 36-64 hours

**Break-even**: At 200 hours/month, you save ~$600/year but spend ~40+ extra hours. Your time worth >$15/hr? Stay hybrid.

---

## Next Steps

### Week 1: Proof of Concept
1. **Day 1**: Set up Deepgram account, get $200 credit
2. **Day 2**: Install SpeechBrain + Parselmouth on M4
3. **Day 3**: Process 5-10 sample audio files end-to-end
4. **Day 4**: Build basic LangChain integration
5. **Day 5**: Test with your actual use case

### Week 2: Production Readiness
1. Implement error handling and retry logic
2. Add caching for repeated analyses
3. Optimize batch processing
4. Build quality metrics dashboard
5. Document your pipeline

### Month 2: Scale Decision
- **If <500 hours/month**: Stay with hybrid
- **If >500 hours/month**: Migrate to fully local
- **If >1,000 hours/month**: Definitely go fully local

---

## Troubleshooting Common Issues

### M4-Specific

**Issue**: PyTorch not using Metal
```bash
# Solution: Reinstall PyTorch with MPS support
pip uninstall torch torchvision torchaudio
pip3 install torch torchvision torchaudio
```

**Issue**: Out of memory errors
```python
# Solution: Process in smaller chunks
import torch
torch.mps.set_per_process_memory_fraction(0.7)  # Use only 70% of RAM
```

**Issue**: Slow performance
```python
# Verify MPS is active
import torch
print(torch.backends.mps.is_available())  # Should be True
print(torch.backends.mps.is_built())      # Should be True
```

### General Pipeline Issues

**Poor transcription accuracy**
- Check audio quality (16kHz+, clear speech)
- Try custom vocabulary for domain-specific terms
- Consider accent-specific models

**Incorrect emotion detection**
- Validate on acted vs. natural speech (models differ)
- Check audio segmentation (emotions change per segment)
- Try dimensional models (arousal/valence) vs. categorical

**Timestamp drift**
- Use WhisperX forced alignment (not raw Whisper)
- Verify audio sample rate matches model expectations
- Check for audio preprocessing that affects timing

---

## Additional Resources

### Documentation
- Deepgram API: developers.deepgram.com
- WhisperX: github.com/m-bain/whisperX
- SpeechBrain: speechbrain.github.io
- Parselmouth: parselmouth.readthedocs.io

### Community
- Deepgram Discord: deepgram.com/community
- SpeechBrain Slack: speechbrain.github.io
- Audio ML subreddit: r/AudioML

### Research Papers
- See full research document for 40+ citations covering:
  - Speech-to-text benchmarks
  - Emotion recognition architectures
  - Prosody analysis methods
  - Audio-LLM integration patterns

---

## Final Recommendation

**Start here**: Deepgram ($200 free credit) + local SpeechBrain/Parselmouth

**Time investment**: 3 hours to working pipeline

**Cost**: ~$26/month per 100 hours

**Migration path**: When you hit 500+ hours/month, spend a weekend migrating to fully local WhisperX

Your M4 Mac is powerful enough for either approach—the choice is about time vs. money tradeoffs, not technical capability.

---

*Last Updated: October 2025*
*Based on comprehensive research of 40+ sources covering commercial and open-source audio AI solutions*
