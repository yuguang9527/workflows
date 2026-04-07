
## Meeting Knowledge Search

When the user asks anything like "上次会议里...怎么说的", "when did we discuss X", "what was decided about Y" — **directly run search without asking**:

```bash
~/.pyenv/versions/3.11.11/envs/wandb-dev/bin/python \
  /Users/rsong/notion-video-transcriber/search.py "<query>"
```

Then present: which meeting, what timestamp, what was said. Give a direct answer, not raw results.

DB: `~/.local/share/transcribe-datalake/`

---

## Notion Video Transcribe Skill

当用户提到"转写"、"transcribe"，或给出本地视频路径时，直接运行：

```bash
~/.pyenv/versions/3.11.11/envs/wandb-dev/bin/python \
  /Users/rsong/notion-video-transcriber/transcribe_worker.py \
  "/Users/rsong/Downloads/<filename>" \
  "/Users/rsong/Downloads/notion-transcripts" \
  "base"
```

- 输出在 `~/Downloads/notion-transcripts/`（.txt + .json）
- 不要尝试下载 file.notion.so URL，永远 403，让用户自己从 Notion 下载到本地
- 不要问任何问题，直接跑

---

## CodeWatch Project Tracking

When working on any project, maintain a status section at the top of the CLAUDE.md file:

```
## Project Status
<one of: Active, Waiting, Done, On Hold, Not Started>

## Next Steps
<brief description of what needs to happen next>
```

Update these sections when:
- Starting work on a project (Active)
- Finishing a task with follow-up needed (Active + updated Next Steps)
- Blocked on something external (Waiting)
- Completing all planned work (Done)
- Pausing work intentionally (On Hold)

This is automatically synced to the CodeWatch dashboard on your phone.
