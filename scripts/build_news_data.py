#!/usr/bin/env python3
"""Generate or update news-data.json from an external JSON feed.

Expected feed shape (array of objects):
[
  {
    "id": 101,
    "title": "...",
    "category": "...",
    "date": "YYYY-MM-DD",
    "is_featured": false,
    "summary": "...",
    "opportunity": "...",
    "content": "...",
    "source_name": "...",
    "source_url": "...",
    "risk": "...",
    "why_it_matters": "..."
  }
]
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib import request


OUTPUT_FILE = Path("news-data.json")
REQUIRED_KEYS = {
    "id",
    "title",
    "category",
    "date",
    "is_featured",
    "summary",
    "opportunity",
    "content",
    "source_name",
}
OPTIONAL_KEYS = {"source_url", "risk", "why_it_matters"}


def load_existing_news() -> list[dict]:
    if not OUTPUT_FILE.exists():
        return []

    with OUTPUT_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("news-data.json must be a JSON array")

    return data


def fetch_news_feed() -> list[dict] | None:
    source_url = os.getenv("NEWS_SOURCE_URL", "").strip()
    auth_token = os.getenv("NEWS_SOURCE_AUTH_TOKEN", "").strip()

    if not source_url:
        print("NEWS_SOURCE_URL is not set; keeping existing news-data.json")
        return None

    req = request.Request(source_url)
    if auth_token:
        req.add_header("Authorization", f"Bearer {auth_token}")

    with request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    if not isinstance(payload, list):
        raise ValueError("Feed payload must be a JSON array")

    normalized = []
    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"Item #{idx} is not an object")

        missing = REQUIRED_KEYS - item.keys()
        if missing:
            raise ValueError(f"Item #{idx} missing required keys: {sorted(missing)}")

        record = {key: item.get(key, "") for key in REQUIRED_KEYS | OPTIONAL_KEYS}
        normalized.append(record)

    return normalized


def write_news(data: list[dict]) -> None:
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    try:
        existing = load_existing_news()
        incoming = fetch_news_feed()

        output = existing if incoming is None else incoming
        write_news(output)
        print(f"Wrote {len(output)} records to {OUTPUT_FILE}")
    except Exception as exc:
        print(f"Failed to build news data: {exc}", file=sys.stderr)
        sys.exit(1)
