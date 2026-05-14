#!/usr/bin/env python3
"""关键词索引查询 - 中文 ↔ slug"""
import json
from pathlib import Path

KW_FILE = Path("/mnt/d/clawsjoy/data/keywords.json")

def load_index():
    with open(KW_FILE) as f:
        data = json.load(f)
    index = {}
    for cat in data.get("categories", {}).values():
        for kw in cat.get("keywords", []):
            if isinstance(kw, dict):
                name = kw.get("name")
                slug = kw.get("slug")
                if name:
                    index[name] = slug
                if slug:
                    index[slug] = slug
    return index

def to_slug(keywords):
    idx = load_index()
    return [idx.get(k, k) for k in keywords]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(to_slug(sys.argv[1:]))
