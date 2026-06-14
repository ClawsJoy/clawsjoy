#!/usr/bin/env python3
"""file_agent v4.0 - 智慧化文件管理智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple, List

from core.agents.business.business_agent import BusinessAgent


class FileAgentV4(BusinessAgent):
    """智慧化文件管理智能体"""
    
    name = "file_agent_v4"
    description = "智慧化文件助手"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.user_dir = Path(f"data/users/{user_id}")
        self.user_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 {self.name} v{self.version} 智慧化启动")
        print(f"   📂 工作目录: {self.user_dir}")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("read", "file"): (True, 0.95),
            ("write", "file"): (True, 0.95),
            ("list", "file"): (True, 0.90),
            ("delete", "file"): (True, 0.85),
            ("search", "file"): (True, 0.85),
        }
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        
        # 读取文件
        if any(kw in user_input for kw in ["读取", "查看", "打开"]):
            return self._read_file(user_input)
        
        # 写入/创建文件
        if any(kw in user_input for kw in ["写入", "创建", "保存"]):
            return self._write_file(user_input)
        
        # 列出文件
        if any(kw in user_input for kw in ["列出", "目录", "文件列表"]):
            return self._list_files(user_input)
        
        # 删除文件
        if "删除" in user_input:
            return self._delete_file(user_input)
        
        # 搜索文件
        if "搜索" in user_input:
            return self._search_files(user_input)
        
        return self._response(self._get_help())
    
    def _read_file(self, user_input: str) -> Dict:
        """读取文件"""
        # 提取文件名
        match = re.search(r'(?:读取|查看|打开)[：:]\s*(\S+)', user_input)
        if not match:
            match = re.search(r'(?:读取|查看|打开)\s+(\S+)', user_input)
        
        if not match:
            return self._response("请指定要读取的文件名。\n示例：读取 readme.txt")
        
        filename = match.group(1)
        file_path = self.user_dir / filename
        
        if not file_path.exists():
            return self._response(f"❌ 文件不存在：{filename}")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            preview = content[:500] + "..." if len(content) > 500 else content
            return self._response(
                f"📄 **{filename}**\n\n```\n{preview}\n```",
                metadata={"filename": filename, "size": file_path.stat().st_size}
            )
        except Exception as e:
            return self._response(f"❌ 读取失败：{e}")
    
    def _write_file(self, user_input: str) -> Dict:
        """写入文件"""
        # 解析文件名和内容
        match = re.search(r'(?:写入|创建|保存)[：:]\s*(\S+)\s+内容[：:]\s*(.+)$', user_input, re.DOTALL)
        if not match:
            match = re.search(r'(?:写入|创建|保存)\s+(\S+)\s+内容\s+(.+)$', user_input, re.DOTALL)
        
        if not match:
            # 简单格式：写入 test.txt Hello World
            parts = user_input.replace("写入", "").replace("创建", "").replace("保存", "").strip().split(maxsplit=1)
            if len(parts) == 2:
                filename, content = parts[0], parts[1]
            else:
                return self._response("请指定文件名和内容。\n示例：写入 test.txt 内容 Hello World")
        else:
            filename, content = match.group(1), match.group(2)
        
        file_path = self.user_dir / filename
        
        try:
            file_path.write_text(content, encoding='utf-8')
            return self._response(
                f"✅ 已保存：{filename}\n📝 大小：{len(content)} 字符",
                metadata={"filename": filename, "size": len(content)}
            )
        except Exception as e:
            return self._response(f"❌ 保存失败：{e}")
    
    def _list_files(self, user_input: str) -> Dict:
        """列出文件"""
        # 获取目录
        match = re.search(r'(?:列出|目录)[：:]\s*(.+)', user_input)
        if match:
            subdir = match.group(1)
            target_dir = self.user_dir / subdir
        else:
            target_dir = self.user_dir
        
        if not target_dir.exists():
            return self._response(f"❌ 目录不存在：{target_dir}")
        
        files = []
        for item in target_dir.iterdir():
            info = {
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            }
            files.append(info)
        
        if not files:
            return self._response("📁 目录为空")
        
        lines = [f"📁 **{target_dir}** ({len(files)} 项)"]
        for f in sorted(files, key=lambda x: (x["type"], x["name"])):
            icon = "📁" if f["type"] == "dir" else "📄"
            size_info = f" ({f['size']} B)" if f["type"] == "file" else ""
            lines.append(f"  {icon} {f['name']}{size_info}")
        
        return self._response("\n".join(lines), metadata={"files": files})
    
    def _delete_file(self, user_input: str) -> Dict:
        """删除文件"""
        match = re.search(r'删除[：:]\s*(\S+)', user_input)
        if not match:
            match = re.search(r'删除\s+(\S+)', user_input)
        
        if not match:
            return self._response("请指定要删除的文件名。\n示例：删除 test.txt")
        
        filename = match.group(1)
        file_path = self.user_dir / filename
        
        if not file_path.exists():
            return self._response(f"❌ 文件不存在：{filename}")
        
        try:
            file_path.unlink()
            return self._response(f"🗑️ 已删除：{filename}")
        except Exception as e:
            return self._response(f"❌ 删除失败：{e}")
    
    def _search_files(self, user_input: str) -> Dict:
        """搜索文件"""
        match = re.search(r'搜索[：:]\s*(.+)', user_input)
        if not match:
            match = re.search(r'搜索\s+(.+)', user_input)
        
        if not match:
            return self._response("请指定搜索关键词。\n示例：搜索 readme")
        
        keyword = match.group(1).lower()
        results = []
        
        for item in self.user_dir.rglob("*"):
            if item.is_file() and keyword in item.name.lower():
                results.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.user_dir)),
                    "size": item.stat().st_size
                })
        
        if not results:
            return self._response(f"🔍 未找到包含 '{keyword}' 的文件")
        
        lines = [f"🔍 搜索 '{keyword}' 找到 {len(results)} 个文件："]
        for r in results[:20]:
            lines.append(f"  📄 {r['path']} ({r['size']} B)")
        
        if len(results) > 20:
            lines.append(f"  ... 还有 {len(results) - 20} 个文件")
        
        return self._response("\n".join(lines), metadata={"results": results})
    
    def _get_help(self) -> str:
        return """📁 **文件助手**

使用方式:
- 读取文件: "读取 test.txt"
- 写入文件: "写入 test.txt 内容 Hello World"
- 列出文件: "列出文件" 或 "目录"
- 删除文件: "删除 test.txt"
- 搜索文件: "搜索 关键词"

💡 文件保存在用户专属目录: data/users/{user_id}/"""
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }


if __name__ == "__main__":
    agent = FileAgentV4("test")
    print("✅ file_agent_v4 测试通过")
