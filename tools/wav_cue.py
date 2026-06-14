#!/usr/bin/env python3
"""wav_cue.py — read/write standard WAV `cue ` chunks (slice markers).

The 1010music Blackbox stores slicer slice points as standard WAV cue points
(manual: "Slice Points ... Stored in the WAV cue points"). Author slices on the
Mac, stamp them into the WAV here, drop on the SD card, load as a Slicer pad.

Usage:
  # write cues at sample offsets
  wav_cue.py write in.wav out.wav --samples 0,44100,88200

  # write cues at times in seconds (converted via the file's sample rate)
  wav_cue.py write in.wav out.wav --seconds 0,0.5,1.25,2.0

  # read/list cues already in a file
  wav_cue.py read file.wav
"""
import struct
import sys
import argparse


def _read_chunks(buf):
    """Yield (chunk_id, offset_of_payload, size) for each chunk in a RIFF/WAVE."""
    assert buf[0:4] == b"RIFF", "not a RIFF file"
    assert buf[8:12] == b"WAVE", "not a WAVE file"
    pos = 12
    while pos + 8 <= len(buf):
        cid = buf[pos:pos + 4]
        size = struct.unpack_from("<I", buf, pos + 4)[0]
        yield cid, pos + 8, size
        pos += 8 + size + (size & 1)  # chunks are word-aligned (pad byte if odd)


def _fmt_info(buf):
    for cid, off, size in _read_chunks(buf):
        if cid == b"fmt ":
            # fmt: audioFormat(H) numChannels(H) sampleRate(I) ...
            _afmt, channels, rate = struct.unpack_from("<HHI", buf, off)
            return rate, channels
    raise ValueError("no fmt chunk")


def _build_cue_chunk(offsets):
    """offsets: list of sample-frame offsets into the data chunk."""
    n = len(offsets)
    body = struct.pack("<I", n)
    for i, off in enumerate(offsets, start=1):
        # id, position, 'data', chunkStart, blockStart, sampleOffset
        body += struct.pack("<I I 4s I I I", i, off, b"data", 0, 0, off)
    return b"cue " + struct.pack("<I", len(body)) + body


def write_cues(in_path, out_path, offsets):
    with open(in_path, "rb") as f:
        buf = f.read()
    # keep every chunk except an existing cue (we replace it), append fresh cue
    out = bytearray(b"RIFF\x00\x00\x00\x00WAVE")
    for cid, off, size in _read_chunks(buf):
        if cid == b"cue ":
            continue
        raw = buf[off - 8: off + size + (size & 1)]
        out += raw
    out += _build_cue_chunk(offsets)
    struct.pack_into("<I", out, 4, len(out) - 8)  # fix RIFF size
    with open(out_path, "wb") as f:
        f.write(out)
    return len(offsets)


def read_cues(path):
    with open(path, "rb") as f:
        buf = f.read()
    for cid, off, size in _read_chunks(buf):
        if cid == b"cue ":
            (n,) = struct.unpack_from("<I", buf, off)
            cues = []
            for i in range(n):
                base = off + 4 + i * 24
                ident, _pos, _chunk, _cs, _bs, samp = struct.unpack_from("<I I 4s I I I", buf, base)
                cues.append((ident, samp))
            return cues
    return []


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("infile"); w.add_argument("outfile")
    g = w.add_mutually_exclusive_group(required=True)
    g.add_argument("--samples", help="comma-separated sample-frame offsets")
    g.add_argument("--seconds", help="comma-separated times in seconds")
    r = sub.add_parser("read")
    r.add_argument("infile")
    a = ap.parse_args()

    if a.cmd == "read":
        cues = read_cues(a.infile)
        rate, _ = _fmt_info(open(a.infile, "rb").read())
        if not cues:
            print("no cue points"); return
        for ident, samp in cues:
            print(f"  cue {ident:>3}: sample {samp:>10}  ({samp / rate:.4f}s)")
        print(f"{len(cues)} cue point(s)")
        return

    with open(a.infile, "rb") as f:
        rate, _ = _fmt_info(f.read())
    if a.samples:
        offs = [int(x) for x in a.samples.split(",") if x.strip()]
    else:
        offs = [round(float(x) * rate) for x in a.seconds.split(",") if x.strip()]
    n = write_cues(a.infile, a.outfile, offs)
    print(f"wrote {n} cue point(s) -> {a.outfile}")


if __name__ == "__main__":
    main()
