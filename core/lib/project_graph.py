#!/usr/bin/env python3
"""项目依赖图 - 跨文件分析"""

import re
from pathlib import Path
from typing import Dict, List, Set


class ProjectGraph:
    """项目依赖图"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.graph: Dict[str, Set[str]] = {}
        self._build()

    def _build(self):
        """构建依赖图"""
        py_files = list(self.project_path.rglob("*.py"))
        
        for file in py_files:
            try:
                content = file.read_text(encoding='utf-8')
                imports = self._extract_imports(content)
                rel_path = str(file.relative_to(self.project_path))
                self.graph[rel_path] = imports
            except Exception as e:
                print(f"跳过 {file}: {e}")

    def _extract_imports(self, content: str) -> Set[str]:
        """提取导入"""
        imports = set()
        # import xxx
        for m in re.findall(r'^import\s+(\w+)', content, re.MULTILINE):
            imports.add(f"{m}.py")
        # from xxx import
        for m in re.findall(r'^from\s+(\w+)', content, re.MULTILINE):
            imports.add(f"{m}.py")
        return imports

    def get_affected_files(self, file_path: str) -> List[str]:
        """获取受影响的文件"""
        affected = set()
        for f, deps in self.graph.items():
            if file_path in deps:
                affected.add(f)
        return list(affected)

    def get_dependencies(self, file_path: str) -> List[str]:
        """获取文件依赖"""
        return list(self.graph.get(file_path, []))

    def get_stats(self) -> Dict:
        return {
            "total_files": len(self.graph),
            "total_edges": sum(len(v) for v in self.graph.values())
        }


def get_project_graph(project_id: str, user_id: str = "codex_user"):
    """获取项目依赖图"""
    try:
        from core.lib.code_repo import get_code_repo
        repo = get_code_repo(user_id)
        project = repo.get_project(project_id)
        if not project:
            return None
        return ProjectGraph(project["path"])
    except:
        return None
