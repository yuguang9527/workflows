Semantic search across all transcribed content.

## Run search

```bash
~/.pyenv/versions/3.11.11/envs/wandb-dev/bin/python \
  /Users/rsong/notion-video-transcriber/search.py "$ARGUMENTS"
```

## Present results

Answer the question directly. No timestamps, no source citations, no raw quotes.

Then stay in conversation mode — the user may ask follow-up questions. For each follow-up, run another search automatically and keep answering. Stay in this mode until the user changes topic.
