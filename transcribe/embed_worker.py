#!/usr/bin/env python3
"""
embed_worker.py <transcript_json_path>

Chunks a transcript, embeds with OpenAI text-embedding-3-small,
stores in ChromaDB at ~/.local/share/transcribe-datalake/
"""

import sys
import json
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path.home() / ".config/notion-video-transcriber/config.json"
DB_PATH     = Path.home() / ".local/share/transcribe-datalake"

def load_key():
    cfg = json.loads(CONFIG_PATH.read_text())
    key = cfg.get("openai_api_key", "")
    if not key:
        print("[embed] No openai_api_key in config.json", flush=True)
        sys.exit(1)
    return key

def chunk_transcript(segments: list, max_tokens: int = 300) -> list:
    """Group Whisper segments into chunks of ~max_tokens words."""
    chunks, current, count = [], [], 0
    for seg in segments:
        words = len(seg["text"].split())
        if count + words > max_tokens and current:
            chunks.append({
                "text": " ".join(s["text"] for s in current).strip(),
                "start": current[0]["start"],
                "end":   current[-1]["end"],
            })
            current, count = [], 0
        current.append(seg)
        count += words
    if current:
        chunks.append({
            "text": " ".join(s["text"] for s in current).strip(),
            "start": current[0]["start"],
            "end":   current[-1]["end"],
        })
    return chunks

def fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def main():
    if len(sys.argv) < 2:
        print("usage: embed_worker.py <transcript.json>", flush=True)
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"[embed] File not found: {json_path}", flush=True)
        sys.exit(1)

    data = json.loads(json_path.read_text())
    segments = data.get("segments", [])
    source   = json_path.stem  # e.g. video1952916727

    if not segments:
        print("[embed] No segments found in JSON, skipping.", flush=True)
        sys.exit(0)

    print(f"[embed] Chunking {len(segments)} segments…", flush=True)
    chunks = chunk_transcript(segments)
    print(f"[embed] {len(chunks)} chunks created.", flush=True)

    # OpenAI embeddings
    from openai import OpenAI
    client = OpenAI(api_key=load_key())

    texts = [c["text"] for c in chunks]
    print(f"[embed] Embedding via OpenAI text-embedding-3-small…", flush=True)
    resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    embeddings = [r.embedding for r in resp.data]
    print(f"[embed] Got {len(embeddings)} embeddings.", flush=True)

    # ChromaDB
    import chromadb
    DB_PATH.mkdir(parents=True, exist_ok=True)
    chroma = chromadb.PersistentClient(path=str(DB_PATH))
    col    = chroma.get_or_create_collection("transcripts", metadata={"hnsw:space": "cosine"})

    ids, docs, metas, embeds = [], [], [], []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        ids.append(f"{source}_{i}")
        docs.append(chunk["text"])
        metas.append({
            "source":     source,
            "start":      fmt_time(chunk["start"]),
            "end":        fmt_time(chunk["end"]),
            "language":   data.get("language", "unknown"),
            "indexed_at": datetime.now().isoformat(),
        })
        embeds.append(emb)

    col.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=embeds)
    print(f"[embed] Stored {len(ids)} chunks → {DB_PATH}", flush=True)

if __name__ == "__main__":
    main()
