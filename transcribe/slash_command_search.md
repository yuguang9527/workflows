Enter knowledge search conversation mode.

Tell the user: "Knowledge search mode — ask me anything about your meetings."

Then stay in conversation. For every question the user asks:

1. Run search automatically:
```bash
~/.pyenv/versions/3.11.11/envs/wandb-dev/bin/python \
  /Users/rsong/notion-video-transcriber/search.py "<user's question>"
```

2. Answer directly in natural language. No timestamps, no citations, no raw quotes.

3. Wait for next question. Keep searching and answering until the user explicitly exits.
