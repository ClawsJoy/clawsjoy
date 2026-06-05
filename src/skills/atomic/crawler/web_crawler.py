#!/usr/bin/env python3
"""Web Crawler - Web Crawler 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import re
import sys

import requests
from bs4 import BeautifulSoup

from lib.smart_config import smart_config

sys.path.insert(0, "str(smart_config.ROOT)")
from src.lib.vector.vector_manager import vector_manager


class WebCrawlerSkill:
    name = "web_crawler"
    description = "抓取网页内容存入向量库"
    version = "1.0.0"
    category = "crawler"

    def execute(self, params):
        url = params.get("url", "")
        if not url:
            return {"success": False, "error": "需要提供URL"}

        try:
            resp = requests.get(
                url, timeout=30, headers={"User-Agent": "ClawsJoy-Bot/1.0"}
            )
            if resp.status_code != 200:
                return {"success": False, "error": f"HTTP {resp.status_code}"}

            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()

            text = soup.get_text()
            text = re.sub(r"\s+", " ", text).strip()
            text = text[:2000]

            title = soup.title.string if soup.title else url

            vector_manager.add_knowledge(
                text, category="web_page", metadata={"source_url": url, "title": title}
            )

            return {
                "success": True,
                "url": url,
                "title": title,
                "content_length": len(text),
                "message": f"已抓取并存入向量库",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


skill = WebCrawlerSkill()
