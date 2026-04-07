Transcribe a local video file with Whisper, then summarize the content.

## Step 1 — Pick file

If $ARGUMENTS is provided, use it as the filename (look in ~/Downloads/ if no path given).

If no argument, run:
```bash
ls -lt ~/Downloads/*.{mp4,mov,webm,mkv,m4v} 2>/dev/null | head -20
```
Show the list with size and date, then STOP and ask the user to pick one. Wait for reply before continuing.

## Step 2 — Transcribe

```bash
~/.pyenv/versions/3.11.11/envs/wandb-dev/bin/python \
  /Users/rsong/notion-video-transcriber/transcribe_worker.py \
  "/Users/rsong/Downloads/$FILENAME" \
  "/Users/rsong/Downloads/notion-transcripts" \
  "base"
```

## Step 3 — Read transcript and summarize

Read the output .txt file from ~/Downloads/notion-transcripts/.
Then produce a detailed summary in the same language as the transcript:

- Group by topic with clear headers
- For each point, include the **specific detail** discussed — not just the topic name. E.g. don't write "JIRA migration discussed", write "JIRA migration complete — log in via CoreWeave Okta, use WBN project; Zendesk integration pending"
- When there's a debate, contradiction, or open question, spell it out explicitly with the different positions
- Action items: who needs to do what, and why
- Use ✅ for decisions made, ⚠️ for open issues/contradictions, 🔲 for action items

## Step 4 — Save summary

Save the summary as a .md file alongside the transcript:
`~/Downloads/notion-transcripts/<filename>_summary.md`

Report the file paths when done.
