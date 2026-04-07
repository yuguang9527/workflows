Semantic search across all transcribed meeting videos.

Run this command with the user's query:

```bash
~/.pyenv/versions/3.11.11/envs/wandb-dev/bin/python \
  /Users/rsong/notion-video-transcriber/search.py "$ARGUMENTS"
```

Then present the results clearly:
- Show which meeting (source file) and timestamp each result comes from
- Quote the relevant passage
- If multiple results are from the same meeting, group them together
- Add a one-line interpretation of why each result is relevant to the query
