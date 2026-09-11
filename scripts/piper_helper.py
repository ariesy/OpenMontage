#!/usr/bin/env python3
"""Piper TTS helper for OpenMontage zero-key Chinese voiceover."""
import subprocess
import sys
from pathlib import Path

VOICE_MODEL = "/app/OpenMontage/data/piper_voices/zh_CN-xiao_ya-medium.onnx"
PIPER_BIN = "/app/OpenMontage/.venv/bin/piper"
FFMPEG = "/usr/local/bin/ffmpeg"  # or /home/linuxbrew/.linuxbrew/bin/ffmpeg

def synth(text: str, out_wav: str, length_scale: float = 1.0) -> str:
    """Synthesize text to WAV (22050 Hz mono). Returns path."""
    out_path = Path(out_wav)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = out_path.with_suffix('.raw')
    # 1) piper to raw
    r = subprocess.run(
        [PIPER_BIN, "--model", VOICE_MODEL, "--output-raw",
         "--length-scale", str(length_scale)],
        input=text.encode("utf-8"),
        capture_output=True,
        timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError(f"piper failed: {r.stderr.decode()}")
    raw_path.write_bytes(r.stdout)
    if not r.stdout:
        raise RuntimeError(f"piper produced no audio for: {text[:50]}")
    # 2) ffmpeg raw -> wav
    r2 = subprocess.run(
        [FFMPEG, "-y", "-f", "s16le", "-ar", "22050", "-ac", "1",
         "-i", str(raw_path), "-ar", "22050", str(out_path)],
        capture_output=True,
        timeout=60,
    )
    if r2.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r2.stderr.decode()}")
    raw_path.unlink()
    return str(out_path)

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "你好世界"
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/piper_out.wav"
    p = synth(text, out)
    print(f"OK: {p}")
