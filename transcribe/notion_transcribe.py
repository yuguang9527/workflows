#!/usr/bin/env python3
"""
video-transcribe <url> [model]

Direct video URL → download → Whisper transcribe → save transcript.
No Notion token needed when you have a direct video link.

Also supports Notion page URLs if token is in config.json.
"""

import sys
import json
import re
import subprocess
import requests
from pathlib import Path

SCRIPT_DIR  = Path(__file__).parent
WORKER      = SCRIPT_DIR / "transcribe_worker.py"
WHISPER_PY  = Path.home() / ".pyenv/versions/3.11.11/envs/wandb-dev/bin/python"
CONFIG_PATH = Path.home() / ".config/notion-video-transcriber/config.json"
OUTPUT_DIR  = Path.home() / "Downloads/notion-transcripts"

sys.path.insert(0, str(SCRIPT_DIR))


def safe_name(s: str, fallback: str) -> str:
    s = re.sub(r"[^\w\s\-]", "", s).strip()
    s = re.sub(r"[\s\-]+", "_", s)
    return s or fallback


def _notion_cookies():
    """Load Notion cookies from Chrome to authenticate file downloads."""
    try:
        import browser_cookie3
        jar = browser_cookie3.chrome(domain_name=".notion.so")
        return jar
    except Exception:
        return None


def download_url(url: str, out_dir: Path, name: str = "video") -> Path:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.notion.so/",
    }
    cookies = _notion_cookies() if "notion.so" in url else None
    resp = requests.get(url, stream=True, timeout=120, headers=headers, cookies=cookies)
    resp.raise_for_status()
    ct  = resp.headers.get("content-type", "").lower()
    ext = (".webm" if "webm" in ct else
           ".mov"  if "mov"  in ct else
           ".mkv"  if "mkv"  in ct else ".mp4")
    # also sniff ext from URL if content-type is generic
    for e in (".mp4", ".webm", ".mov", ".mkv", ".m4v"):
        if e in url.split("?")[0]:
            ext = e; break
    dest = out_dir / f"{safe_name(name, 'video')}{ext}"
    size = 0
    with open(dest, "wb") as fh:
        for chunk in resp.iter_content(65536):
            fh.write(chunk); size += len(chunk)
    print(f"  Downloaded: {dest.name}  ({size // 1024:,} KB)")
    return dest


def transcribe(video_path: Path, model: str):
    print(f"  Transcribing with Whisper ({model})…")
    r = subprocess.run(
        [str(WHISPER_PY), str(WORKER), str(video_path), str(OUTPUT_DIR), model],
        text=True,
    )
    if r.returncode != 0:
        print(f"  Transcription failed (exit {r.returncode})")
    else:
        print(f"  Transcript saved to: {OUTPUT_DIR}/")


def handle_direct_url(url: str, model: str):
    """Direct video URL — just download and transcribe."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    name = url.split("/")[-1].split("?")[0] or "video"
    print(f"Downloading: {url[:80]}…")
    path = download_url(url, OUTPUT_DIR, name)
    transcribe(path, model)


def handle_notion_url(url: str, model: str):
    """Notion page URL — needs token in config.json."""
    if not CONFIG_PATH.exists():
        print("No config.json found. Provide a direct video URL instead, or save your Notion token to:")
        print(f"  {CONFIG_PATH}")
        sys.exit(1)
    cfg   = json.loads(CONFIG_PATH.read_text())
    token = cfg.get("token", "").strip()
    if not token:
        print("No token in config.json. Provide a direct video URL instead.")
        sys.exit(1)

    from notion_fetcher import extract_page_id, find_videos
    print("Fetching video blocks from Notion…")
    videos = find_videos(extract_page_id(url), token)
    if not videos:
        print("No hosted videos found on this page.")
        sys.exit(0)

    print(f"Found {len(videos)} video(s):")
    for i, v in enumerate(videos, 1):
        print(f"  {i}. {v['name']}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for i, vid in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] {vid['name'][:60]}")
        try:
            path = download_url(vid["url"], OUTPUT_DIR, vid["name"])
            transcribe(path, model)
        except Exception as e:
            print(f"  Error: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: video-transcribe <url> [model]")
        print("  url   — direct video URL or Notion page URL")
        print("  model — tiny | base | small | medium | large  (default: base)")
        sys.exit(1)

    url   = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "base"

    if "notion.so" in url and "file.notion.so" not in url:
        handle_notion_url(url, model)
    else:
        handle_direct_url(url, model)

    print(f"\nDone. Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
