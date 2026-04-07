#!/usr/bin/env python3
"""
search.py "<natural language query>" [--top 5]

Semantic search across all embedded transcripts in ChromaDB.
Query embeddings are cached locally to avoid repeated API calls.
"""

import sys
import json
import hashlib
from pathlib import Path

CONFIG_PATH = Path.home() / ".config/notion-video-transcriber/config.json"
DB_PATH     = Path.home() / ".local/share/transcribe-datalake"
CACHE_PATH  = DB_PATH / "query_cache.json"

def load_key():
    cfg = json.loads(CONFIG_PATH.read_text())
    return cfg.get("openai_api_key", "")

def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}

def save_cache(cache: dict):
    DB_PATH.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache))

def get_embedding(query: str) -> list:
    cache = load_cache()
    key   = hashlib.md5(query.lower().strip().encode()).hexdigest()

    if key in cache:
        return cache[key]

    from openai import OpenAI
    client = OpenAI(api_key=load_key())
    resp   = client.embeddings.create(model="text-embedding-3-small", input=[query])
    emb    = resp.data[0].embedding

    cache[key] = emb
    save_cache(cache)
    return emb

def main():
    args = sys.argv[1:]
    if not args:
        print("usage: search.py '<query>' [--top N]")
        sys.exit(1)

    top_n = 5
    if "--top" in args:
        i = args.index("--top")
        top_n = int(args[i+1])
        args = args[:i] + args[i+2:]
    query = " ".join(args)

    import chromadb

    q_emb  = get_embedding(query)
    chroma = chromadb.PersistentClient(path=str(DB_PATH))
    col    = chroma.get_or_create_collection("transcripts", metadata={"hnsw:space": "cosine"})
    results = col.query(query_embeddings=[q_emb], n_results=top_n)

    docs  = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    print(f"\nQuery: {query}\n{'─'*60}")
    for doc, meta, dist in zip(docs, metas, dists):
        score = round((1 - dist) * 100, 1)
        print(f"\n[{meta['source']}]  {meta['start']} → {meta['end']}  (relevance {score}%)")
        print(f"{doc[:400]}{'…' if len(doc) > 400 else ''}")
    print(f"\n{'─'*60}")

if __name__ == "__main__":
    main()
