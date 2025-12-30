# Strudel + SuperDirt Setup

Live coding music stack for human-agent collaboration.

## Architecture

```
strudel.cc (browser)
    → WebSocket (8080)
    → npx @strudel/osc
    → OSC (57120)
    → SuperCollider/SuperDirt
    → audio out
```

## Prerequisites

- **SuperCollider** - `brew install --cask supercollider`
- **Node.js** - for OSC bridge

## First-Time Setup (already done)

### 1. Install SuperDirt in SuperCollider

Open SuperCollider IDE and run:

```supercollider
Quarks.checkForUpdates({Quarks.install("SuperDirt", "v1.7.3"); thisProcess.recompile()})
```

Wait for download + recompile. This installs:
- SuperDirt (sample playback engine)
- Vowel (vocal synthesis)
- Dirt-Samples (default sample library)

## Starting the Stack (each session)

### 1. Start SuperCollider + SuperDirt

Open SuperCollider IDE and run:

```supercollider
SuperDirt.start
```

You should see audio server boot messages.

### 2. Start OSC Bridge

In terminal:

```bash
cd ~/Projects/ai-music-tools
npx @strudel/osc
```

Should show:
```
[Sending OSC] 127.0.0.1:57120
[Listening WS] ws://localhost:8080
```

### 3. Open Strudel REPL

Go to https://strudel.cc

### 4. Enable OSC Output

Add to your pattern:

```javascript
$: s("[bd <hh oh>]*2").bank("tr909").dec(.4)

all(osc)
```

Or use `.osc()` on individual patterns.

## Troubleshooting

### No sound from SuperDirt

1. Check SuperCollider post window for errors
2. Verify `SuperDirt.start` completed
3. Try `~dirt.free; SuperDirt.start` to restart

### OSC bridge not connecting

1. Check port 8080 isn't in use: `lsof -i :8080`
2. Restart the bridge: `npx @strudel/osc`

### Strudel not sending OSC

1. Make sure you have `all(osc)` in your pattern
2. Check browser console for WebSocket errors

## Sample Banks

SuperDirt comes with samples. Use them with:

```javascript
s("bd*4").bank("tr909")  // TR-909 drums
s("bass*4")              // bass samples
s("arpy*8")              // arpeggiator sounds
```

## Next Steps

- Explore file-based workflow (watch file → auto-reload)
- TidalCycles for pure terminal experience
- Custom synths in SuperCollider

---

**Stack confirmed working:** 2025-12-05
**By:** Zeph (z3f.6f98.b0p)
