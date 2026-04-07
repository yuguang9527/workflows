# Notion Video Transcribe Workflow

Download a video from Notion and transcribe it with Whisper — triggered directly from Claude Code.

## Usage

In Claude Code, type:

```
/transcribe                    # list videos in ~/Downloads/ and pick one
/transcribe video.mp4          # transcribe a specific file
/transcribe video.mp4 medium   # use a larger Whisper model
```

Output: `~/Downloads/notion-transcripts/<filename>.txt` + `.json`

## How it works

1. You download a video from Notion manually (right-click → Download)
2. Run `/transcribe` in Claude Code
3. Claude runs `transcribe_worker.py` using the `wandb-dev` Python env (has openai-whisper)
4. Transcript saved as plain text + JSON with timestamps

## Setup

### Requirements

- Python env with `openai-whisper`, `pydub`, `torch` installed
  - Default: `~/.pyenv/versions/3.11.11/envs/wandb-dev/bin/python`
- `ffmpeg` (for audio conversion via pydub)

### Install

```bash
# 1. Copy scripts to your machine
cp transcribe_worker.py notion_fetcher.py notion_transcribe.py \
   ~/notion-video-transcriber/

# 2. Install Claude Code slash command (global)
cp slash_command.md ~/.claude/commands/transcribe.md

# 3. (Optional) install CLI tool
cat > ~/.local/bin/video-transcribe << 'EOF'
#!/bin/bash
exec /usr/local/bin/python3 ~/notion-video-transcriber/notion_transcribe.py "$@"
EOF
chmod +x ~/.local/bin/video-transcribe
```

## Files

| File | Purpose |
|------|---------|
| `transcribe_worker.py` | Core worker — loads Whisper, converts audio, saves transcript |
| `notion_fetcher.py` | Notion API helper — finds video blocks in a page (needs integration token) |
| `notion_transcribe.py` | CLI entry point — handles both direct URLs and Notion page URLs |
| `slash_command.md` | Claude Code `/transcribe` slash command definition |

## Notes

- `file.notion.so` URLs require browser session cookies — Python cannot download them directly. Download manually from Notion instead.
- Whisper `base` model: ~33s for a 25-minute video on CPU
- Transcripts include full segment timestamps in the `.json` output
