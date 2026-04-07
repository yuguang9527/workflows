#!/usr/bin/env python3
"""
search.py "<natural language query>" [--top 5]

Semantic search across all embedded transcripts in ChromaDB.
"""

import sys
import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".config/notion-video-transcriber/config.json"
DB_PATH     = Path.home() / ".local/share/transcribe-datalake"

def load_key():
    cfg = json.loads(CONFIG_PATH.read_text())
    return cfg.get("openai_api_key", "")

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

    from openai import OpenAI
    import chromadb

    client = OpenAI(api_key=load_key())
    resp   = client.embeddings.create(model="text-embedding-3-small", input=[query])
    q_emb  = resp.data[0].embedding

    chroma = chromadb.PersistentClient(path=str(DB_PATH))
    col    = chroma.get_or_create_collection("transcripts", metadata={"hnsw:space": "cosine"})

    results = col.query(query_embeddings=[q_emb], n_results=top_n)

    docs   = results["documents"][0]
    metas  = results["metadatas"][0]
    dists  = results["distances"][0]

    print(f"\nQuery: {query}\n{'─'*60}")
    for doc, meta, dist in zip(docs, metas, dists):
        score = round((1 - dist) * 100, 1)  # cosine: dist=0 → 100%, dist=1 → 0%
        print(f"\n[{meta['source']}]  {meta['start']} → {meta['end']}  (relevance {score}%)")
        print(f"{doc[:400]}{'…' if len(doc) > 400 else ''}")
    print(f"\n{'─'*60}")

if __name__ == "__main__":
    main()
