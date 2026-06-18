#!/usr/bin/env python3
"""FileAgent v4.2 - 精简稳定版（文件管理）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List

from core.agents.business.business_agent import BusinessAgent


class FileAgentV4(BusinessAgent):
    """文件 Agent - 精简稳定版"""

    name = "file_agent_v4"
    description = "智慧文件助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.user_dir = Path(f"data/users/{user_id}")
        self.user_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 FileAgent v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()
        
        if any(kw in t for kw in ["读取", "查看", "打开"]):
            return self._read_file(user_input)
        
        if any(kw in t for kw in ["写入", "创建", "保存"]):
            return self._write_file(user_input)
        
        if any(kw in t for kw in ["列出", "目录"]):
            return self._list_files(user_input)
        
        if "删除" in t:
            return self._delete_file(user_input)
        
        if "搜索" in t:
            return self._search_files(user_input)
        
        return self._resp("📁 输入「读取 test.txt」或「列出文件」")

    # ================================================================
    #  读取
    # ================================================================

    def _read_file(self, user_input: str) -> Dict:
        match = re.search(r'(?:读取|查看|打开)[：:]\s*(\S+)', user_input)
        if not match:
            match = re.search(r'(?:读取|查看|打开)\s+(\S+)', user_input)
        if not match:
            return self._resp("请指定文件名。示例：读取 test.txt")
        
        file_path = self.user_dir / match.group(1)
        if not file_path.exists():
            return self._resp(f"❌ 文件不存在：{match.group(1)}")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            preview = content[:500] + ("..." if len(content) > 500 else "")
            return self._resp(f"📄 **{match.group(1)}**\n\n```\n{preview}\n```")
        except Exception as e:
            return self._resp(f"❌ 读取失败：{e}")

    # ================================================================
    #  写入
    # ================================================================

    def _write_file(self, user_input: str) -> Dict:
        parts = user_input.replace("写入", "").replace("创建", "").replace("保存", "").strip().split(maxsplit=1)
        if len(parts) != 2:
            return self._resp("请指定文件名和内容。示例：写入 test.txt Hello World")
        
        filename, content = parts[0], parts[1]
        file_path = self.user_dir / filename
        file_path.write_text(content, encoding='utf-8')
        return self._resp(f"✅ 已保存：{filename} ({len(content)} 字符)")

    # ================================================================
    #  列出
    # ================================================================

    def _list_files(self, user_input: str) -> Dict:
        files = []
        for item in self.user_dir.iterdir():
            files.append({
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })
        
        if not files:
            return self._resp("📁 目录为空")
        
        lines = [f"📁 **{self.user_dir}** ({len(files)} 项)"]
        for f in sorted(files, key=lambda x: (x["type"], x["name"])):
            icon = "📁" if f["type"] == "dir" else "📄"
            size = f" ({f['size']}B)" if f["type"] == "file" else ""
            lines.append(f"  {icon} {f['name']}{size}")
        return self._resp("\n".join(lines))

    # ================================================================
    #  删除
    # ================================================================

    def _delete_file(self, user_input: str) -> Dict:
        match = re.search(r'删除[：:]\s*(\S+)', user_input)
        if not match:
            match = re.search(r'删除\s+(\S+)', user_input)
        if not match:
            return self._resp("请指定文件名。示例：删除 test.txt")
        
        file_path = self.user_dir / match.group(1)
        if not file_path.exists():
            return self._resp(f"❌ 文件不存在：{match.group(1)}")
        
        file_path.unlink()
        return self._resp(f"🗑 已删除：{match.group(1)}")

    # ================================================================
    #  搜索
    # ================================================================

    def _search_files(self, user_input: str) -> Dict:
        match = re.search(r'搜索[：:]\s*(.+)', user_input)
        if not match:
            match = re.search(r'搜索\s+(.+)', user_input)
        if not match:
            return self._resp("请指定关键词。示例：搜索 readme")
        
        keyword = match.group(1).lower()
        results = []
        for item in self.user_dir.rglob("*"):
            if item.is_file() and keyword in item.name.lower():
                results.append(f"{item.relative_to(self.user_dir)} ({item.stat().st_size}B)")
        
        if not results:
            return self._resp(f"🔍 未找到 '{keyword}'")
        
        lines = [f"🔍 找到 {len(results)} 个文件："] + [f"  📄 {r}" for r in results[:20]]
        return self._resp("\n".join(lines))

    # ================================================================
    #  辅助
    # ================================================================

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = FileAgentV4("test")
    print(agent.process("列出文件")["response"])
