# Model D Setup for Ableton

## Overview

The Behringer Model D is connected via USB MIDI and responds on **MIDI Channel 11**.

## Ableton Setup

### 1. Connect Model D

- Plug Model D into your laptop via USB cable
- The Model D should appear as a MIDI device named "MODEL D"

### 2. Enable MIDI Output in Ableton

1. Go to **Preferences** → **Link/Tempo/MIDI**
2. Under **MIDI Ports**, find "MODEL D"
3. Enable **Track** and **Sync** output for MODEL D

### 3. Create a MIDI Track

1. Create a new MIDI track (Cmd+Shift+T)
2. Set **MIDI To** to "MODEL D"
3. Set **Channel** to **11** (important!)
4. Arm the track for recording (or set monitoring to "In")

### 4. Test It

- Play notes on your MIDI keyboard or draw notes in the piano roll
- You should hear the Model D respond

## Important Settings

| Setting | Value |
|---------|-------|
| MIDI Device | MODEL D |
| MIDI Channel | **11** |
| Connection | USB |

## Synth Settings Checklist

On the Model D itself:
- [ ] Power on
- [ ] All 3 oscillators ON (switches up)
- [ ] Volume at reasonable level
- [ ] Filter cutoff open (turn up if no sound)
- [ ] VCA sustain up (for held notes)
- [ ] Audio output connected (or use headphones jack)

## Troubleshooting

**No sound:**
1. Check MIDI channel is set to 11 in Ableton
2. Verify Model D appears in MIDI preferences
3. Check oscillators are ON on the synth
4. Check filter isn't fully closed
5. Check audio output/volume

**Notes stick:**
- Model D may hold notes if Ableton loses sync
- Turn synth off/on to reset

**Latency:**
- Use ASIO driver on Windows, Core Audio on Mac
- Reduce buffer size in Audio preferences (256-512 samples)

## Optional: External Instrument

For effects processing through Ableton:
1. Add "External Instrument" to MIDI track
2. Set **MIDI To** = MODEL D, **Channel** = 11
3. Set **Audio From** = your audio interface input (where Model D audio out connects)
4. Adjust hardware latency compensation

This lets you process Model D's audio through Ableton's effects.

---

*Setup by Zeph - December 2025*
