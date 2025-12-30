# Zeph's Tidal Studio

## Quick Start

1. **Start SuperCollider with SuperDirt + Model D MIDI:**
   ```bash
   ./start-studio.sh
   ```
   Wait until you see "SuperDirt ready!" and "Model D MIDI configured"

2. **Start Tidal in another terminal:**
   ```bash
   source ~/.ghcup/env
   cd /Users/olivier/Projects/ai-music-tools/tidal
   ghci -ghci-script BootTidal.hs
   ```

3. **Play notes on Model D:**
   ```haskell
   -- C major arpeggio
   d1 $ note "0 4 7 12" # s "modeld" # midichan 10

   -- Acid bassline
   d1 $ note "0 0 12 0 3 3 5 7" # s "modeld" # midichan 10

   -- Stop
   hush
   ```

## Model D MIDI Setup

- **Sound name:** `modeld` (lowercase, no quotes in patterns)
- **MIDI channel:** 11 (use `midichan 10` in Tidal - it's 0-indexed)
- **SuperDirt port:** 57120

## Pattern Examples

```haskell
-- Simple sequence
d1 $ note "0 4 7" # s "modeld" # midichan 10

-- With octave shifts
d1 $ note "0 12 24" # s "modeld" # midichan 10

-- Faster subdivisions
d1 $ note "0 2 4 5 7 9 11 12" # s "modeld" # midichan 10

-- Euclidean rhythm
d1 $ note (euclid 5 8 "0 7 12") # s "modeld" # midichan 10

-- Random notes from scale
d1 $ note (scale "minor" (irand 8)) # s "modeld" # midichan 10

-- Control velocity
d1 $ note "0 4 7" # s "modeld" # midichan 10 # velocity 0.7

-- Stop all
hush
```

## Troubleshooting

**No sound from Model D:**
- Check Model D is on USB and powered
- Verify MIDI channel is 11 (midichan 10)
- Check volume/filter/env settings on synth

**SuperDirt won't start:**
- Check SuperCollider is installed
- Verify SuperDirt quark is installed
- Run manually: `/Applications/SuperCollider.app/Contents/MacOS/sclang superdirt_startup.scd`

**Tidal won't connect:**
- Ensure SuperDirt started first
- Check port 57120 is available
- Verify GHC/Tidal installation: `ghc-pkg list | grep tidal`

## Files

- `BootTidal.hs` - Tidal boot configuration
- `superdirt_startup.scd` - SuperCollider startup with MIDI routing
- `start-studio.sh` - One-command studio startup
