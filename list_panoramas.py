#!/usr/bin/env python3
"""列出全景图文件"""

import json
import os
from pathlib import Path


def main():
    downloads = Path("downloads")
    if not downloads.exists():
        print(json.dumps({"files": []}))
        return

    files = sorted(
        [f"downloads/{f.name}" for f in downloads.glob("panorama_*.png")], reverse=True
    )
    print(json.dumps({"files": files}))


if __name__ == "__main__":
    main()
