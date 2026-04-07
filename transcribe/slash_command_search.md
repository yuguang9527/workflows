Semantic search across all transcribed meeting videos.

## Step 1 — List available meetings in datalake

```bash
~/.pyenv/versions/3.11.11/envs/wandb-dev/bin/python -c "
import chromadb
from pathlib import Path
c = chromadb.PersistentClient(path=str(Path.home()/'.local/share/transcribe-datalake'))
col = c.get_or_create_collection('transcripts', metadata={'hnsw:space': 'cosine'})
sources = sorted(set(m['source'] for m in col.get()['metadatas']))
print(f'Datalake: {len(sources)} meeting(s)')
for s in sources:
    print(f'  - {s}')
"
```

Show the user which meetings are available before searching.

## Step 2 — Search

```bash
~/.pyenv/versions/3.11.11/envs/wandb-dev/bin/python \
  /Users/rsong/notion-video-transcriber/search.py "$ARGUMENTS"
```

## Step 3 — Present results

- Group results by meeting
- For each hit: timestamp + quoted passage
- Give a direct answer to the query, not just raw results
