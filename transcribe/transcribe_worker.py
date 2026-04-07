#!/usr/bin/env python3
"""
Transcription worker — runs under the wandb-dev Python that has openai-whisper.
Called by app.py via subprocess.

Usage:
    python transcribe_worker.py <video_path> <output_dir> <model_name>

Prints log lines to stdout.  Exits 0 on success, 1 on failure.
"""

import sys
import os
from pathlib import Path

# Make ~/transcript importable
sys.path.insert(0, str(Path.home() / "transcript"))

def main():
    if len(sys.argv) != 4:
        print("usage: transcribe_worker.py <video_path> <output_dir> <model>", flush=True)
        sys.exit(1)

    video_path, output_dir, model = sys.argv[1], sys.argv[2], sys.argv[3]

    print(f"[worker] Loading Whisper model '{model}'…", flush=True)

    try:
        from audio_transcript import AudioTranscriber
    except ImportError as e:
        print(f"[worker] Import error: {e}", flush=True)
        sys.exit(1)

    try:
        t = AudioTranscriber(model_name=model, output_dir=output_dir)
        print(f"[worker] Transcribing: {Path(video_path).name}", flush=True)
        result = t.process_audio_file(video_path)
        if result:
            print(f"[worker] Transcript saved: {result}", flush=True)
            sys.exit(0)
        else:
            print("[worker] Transcription returned no result.", flush=True)
            sys.exit(1)
    except Exception as e:
        print(f"[worker] Error: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
