Run video transcription using Whisper on a local file.

If the user provided a filename or path as an argument, use it directly.
If no argument given, list ALL video files (mp4, mov, webm, mkv) in ~/Downloads/ with their size and date, then STOP and ask the user to pick one. Do NOT auto-select. Wait for user reply before running anything.

Then run this command (no questions, just execute):

```bash
~/.pyenv/versions/3.11.11/envs/wandb-dev/bin/python \
  /Users/rsong/notion-video-transcriber/transcribe_worker.py \
  "/Users/rsong/Downloads/$ARGUMENTS" \
  "/Users/rsong/Downloads/notion-transcripts" \
  "base"
```

Output is saved to ~/Downloads/notion-transcripts/ as .txt and .json.
After completion, show the first 300 characters of the transcript.
