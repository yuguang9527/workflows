#!/usr/bin/env python3
"""Notion API helpers - fetch video blocks from a page."""

import re
import requests
from typing import Optional

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def extract_page_id(url: str) -> str:
    """Extract the 32-char hex page ID from a Notion URL."""
    # Strip anchor and query params
    url = url.split("#")[0].split("?")[0].rstrip("/")

    # Dashed UUID form: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    m = re.search(r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", url)
    if m:
        return m.group(1).replace("-", "")

    # Compact 32-char hex at end of path
    m = re.search(r"([a-f0-9]{32})$", url.replace("-", ""))
    if m:
        return m.group(1)

    raise ValueError(f"Cannot extract page ID from: {url}")


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
    }


def _list_children(block_id: str, token: str) -> list:
    """Fetch all child blocks (handles pagination)."""
    blocks = []
    cursor = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        resp = requests.get(
            f"{NOTION_API}/blocks/{block_id}/children",
            headers=_headers(token),
            params=params,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        blocks.extend(data["results"])
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    return blocks


def find_videos(page_id: str, token: str, max_depth: int = 4) -> list:
    """
    Recursively walk a Notion page tree and collect all hosted video blocks.

    Returns a list of dicts:
        id, name, url, expiry
    """
    videos = []

    def _recurse(block_id: str, depth: int):
        if depth > max_depth:
            return
        try:
            blocks = _list_children(block_id, token)
        except requests.HTTPError as e:
            # May lack access to some blocks — skip silently
            return
        for block in blocks:
            btype = block.get("type", "")
            if btype == "video":
                video = block["video"]
                if video.get("type") == "file":
                    caption_parts = [
                        t.get("plain_text", "")
                        for t in video.get("caption", [])
                    ]
                    caption = " ".join(caption_parts).strip()
                    name = caption if caption else f"video_{block['id'][:8]}"
                    videos.append(
                        {
                            "id": block["id"],
                            "name": name,
                            "url": video["file"]["url"],
                            "expiry": video["file"].get("expiry_time", ""),
                        }
                    )
            # Recurse into containers that may hold videos
            if block.get("has_children") and btype in (
                "column",
                "column_list",
                "toggle",
                "bulleted_list_item",
                "numbered_list_item",
                "quote",
                "callout",
                "synced_block",
                "template",
                "child_page",
                "child_database",
                "table",
            ):
                _recurse(block["id"], depth + 1)

    _recurse(page_id, 0)
    return videos
