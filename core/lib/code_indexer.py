#!/usr/bin/env python3
"""代码索引器 - AST 切分 + embedding + LLM 关键词 + 增量更新
系统模块，位于 ClawsJoy 系统目录，多用户共享
"""

import ast
import json
import os
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional


class CodeIndexer:
    """代码索引器：AST 切分 + 向量索引 + 关键词映射
    每个用户/项目独立一个实例，索引数据存储在用户沙箱的 data/code_index/ 下
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.index_dir = self.project_root / "data" / "code_index"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.keyword_file = self.index_dir / "keyword_index.json"
        self.filehash_file = self.index_dir / "file_hashes.json"
        
        self._keyword_index: Dict[str, list] = {}
        self._file_hashes: Dict[str, str] = {}
        
        # 用户独立的 ChromaDB（禁用内置 embedding，手动传 embeddings）
        self.vector_dir = self.index_dir / "vector_db"
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        import chromadb
        self.chroma_client = chromadb.PersistentClient(path=str(self.vector_dir))
        self._collection = None
        
        self._load()

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.chroma_client.get_or_create_collection(
                "code_blocks",
                embedding_function=None
            )
        return self._collection

    def _load(self):
        if self.keyword_file.exists():
            with open(self.keyword_file, "r") as f:
                self._keyword_index = json.load(f)
        if self.filehash_file.exists():
            with open(self.filehash_file, "r") as f:
                self._file_hashes = json.load(f)

    def _save(self):
        with open(self.keyword_file, "w") as f:
            json.dump(self._keyword_index, f, ensure_ascii=False, indent=2)
        with open(self.filehash_file, "w") as f:
            json.dump(self._file_hashes, f, ensure_ascii=False, indent=2)

    def _file_hash(self, filepath: str) -> str:
        full_path = self.project_root / filepath
        if not full_path.exists():
            return ""
        with open(full_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def parse_file(self, filepath: str) -> List[Dict]:
        full_path = self.project_root / filepath
        if not full_path.exists():
            return []
        try:
            with open(full_path, "r") as f:
                source = f.read()
            tree = ast.parse(source)
        except SyntaxError:
            return []
        
        blocks = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno - 1
                end = getattr(node, 'end_lineno', start + len(node.body) + 1)
                lines = source.split("\n")[start:end]
                code = "\n".join(lines)
                blocks.append({
                    "name": node.name,
                    "kind": "function",
                    "lineno": node.lineno,
                    "code": code[:800],
                    "args": [arg.arg for arg in node.args.args],
                    "signature": f"{node.name}({', '.join(arg.arg for arg in node.args.args)})"
                })
            elif isinstance(node, ast.ClassDef):
                start = node.lineno - 1
                end = getattr(node, 'end_lineno', start + 5)
                lines = source.split("\n")[start:end]
                code = "\n".join(lines)
                blocks.append({
                    "name": node.name,
                    "kind": "class",
                    "lineno": node.lineno,
                    "code": code[:800],
                    "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    "signature": f"class {node.name}"
                })
        return blocks

    def _generate_keywords(self, filename: str) -> List[str]:
        import requests
        name = filename.replace(".py", "").replace("_", " ")
        prompt = f"""将以下代码模块名转换为 3-5 个中文关键词，用逗号分隔。只返回关键词，不要解释。

模块名: {name}"""
        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen2.5:7b-instruct-q4_0", "prompt": prompt, "stream": False, "options": {"num_predict": 50}},
                timeout=30
            )
            if resp.status_code == 200:
                text = resp.json().get("response", "").strip()
                keywords = [k.strip() for k in text.replace("，", ",").split(",") if k.strip()]
                return keywords[:5]
        except Exception:
            pass
        return name.split(" ")[:5]

    def _get_embedding(self, text: str) -> list:
        """通过 Ollama nomic-embed-text 获取 embedding"""
        import requests
        try:
            resp = requests.post(
                "http://localhost:11434/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text[:2000]},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json().get("embedding", [])
        except:
            pass
        return []

    def _add_to_vector(self, filepath: str, blocks: List[Dict]):
        """将代码块加入向量库（手动 Ollama embedding）"""
        try:
            import hashlib
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for b in blocks:
                doc_id = hashlib.md5(f"{filepath}::{b['lineno']}::{b['name']}".encode()).hexdigest()[:16]
                index_content = (
                    f"文件: {filepath}\n"
                    f"类型: {b['kind']}\n"
                    f"名称: {b['name']}\n"
                    f"签名: {b.get('signature', '')}\n"
                    f"代码:\n{b['code']}"
                )[:2000]
                
                emb = self._get_embedding(index_content)
                if not emb:
                    continue
                
                ids.append(doc_id)
                embeddings.append(emb)
                documents.append(index_content)
                metadatas.append({
                    "file": filepath,
                    "type": "code_block",
                    "name": b["name"],
                    "kind": b["kind"],
                    "lineno": b["lineno"],
                    "signature": b.get("signature", "")
                })
            
            if ids:
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
        except Exception as e:
            print(f"[CodeIndexer] 向量索引失败 {filepath}: {e}")


    def _remove_from_vector(self, filepath: str):
        """从向量库移除文件的所有代码块"""
        try:
            results = self.collection.get(where={"file": filepath})
            if results and results["ids"]:
                self.collection.delete(ids=results["ids"])
        except Exception:
            pass

        except Exception:
            pass

    def index_file(self, filepath: str) -> bool:
        if not filepath.endswith(".py"):
            return False
        full_path = self.project_root / filepath
        if not full_path.exists():
            return False
        new_hash = self._file_hash(filepath)
        if self._file_hashes.get(filepath) == new_hash:
            return False
        blocks = self.parse_file(filepath)
        if not blocks:
            return False
        keywords = self._generate_keywords(full_path.name)
        self._keyword_index[filepath] = keywords
        self._remove_from_vector(filepath)
        self._add_to_vector(filepath, blocks)
        self._file_hashes[filepath] = new_hash
        self._save()
        return True

    def _ensure_chinese_keywords(self, user_id: str = None) -> Dict:
        """用 DeepSeek 批量生成中文关键词。返回 {status, time_estimate}"""
        import requests
        
        # 检测是否需要生成：看前 5 个关键词是否含中文
        need_generate = False
        for keywords in list(self._keyword_index.values())[:5]:
            for kw in keywords:
                if any('一' <= c <= '鿿' for c in kw):
                    break
            else:
                need_generate = True
                break
        
        if not need_generate and len(self._keyword_index) > 0:
            return {"status": "ready", "time_estimate": 0}
        
        # 收集所有文件名
        files = list(self._keyword_index.keys())
        if not files:
            return {"status": "empty", "time_estimate": 0}
        
        # 构建 DeepSeek 批量 prompt
        file_list = "\n".join([f.replace("core/lib/", "").replace(".py", "") for f in files[:50]])  # 每批 50 个
        prompt = f"""将以下 Python 模块文件名转换为 3-5 个中文关键词，用逗号分隔。每行一个文件。

格式: 文件名 → 关键词1,关键词2,关键词3

文件列表:
{file_list}"""
        
        try:
            import os
            api_key = os.getenv("DEEPSEEK_API_KEY", "")
            if not api_key:
                return {"status": "no_key", "time_estimate": 0}
            
            resp = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.3
                },
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30
            )
            
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"]
                # 解析结果
                for line in text.strip().split("\n"):
                    if "→" in line or "->" in line:
                        parts = line.replace("->", "→").split("→")
                        if len(parts) == 2:
                            filename = parts[0].strip().replace(" ", "_") + ".py"
                            keywords = [k.strip() for k in parts[1].split(",") if k.strip()]
                            filepath = f"core/lib/{filename}"
                            if filepath in self._keyword_index:
                                self._keyword_index[filepath] = keywords
                self._save()
                return {"status": "ready", "time_estimate": 0}
        except Exception as e:
            print(f"[CodeIndexer] DeepSeek keyword generation failed: {e}")
        
        return {"status": "fallback", "time_estimate": 0}

    def search_files(self, query: str, limit: int = 5) -> List[str]:
        scores = {}
        for filepath, keywords in self._keyword_index.items():
            score = 0
            filename = filepath.split("/")[-1].replace(".py", "").replace("_", " ")
            for kw in keywords:
                if kw in query:
                    score += 1
            # 查询中连续2个词同时出现在文件名中，加分
            query_words = query.lower().replace("_", " ").split()
            for i in range(len(query_words) - 1):
                if query_words[i] in filename and query_words[i+1] in filename:
                    score += 5
            
            if score > 0:
                scores[filepath] = score
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return [f for f, s in ranked[:limit]]

    def search_blocks(self, query: str, files: List[str] = None, limit: int = 5) -> List[Dict]:
        """在指定文件范围内，用 embedding 精排代码块（手动 Ollama embedding）"""
        try:
            query_emb = self._get_embedding(query)
            if not query_emb:
                return []
            results = self.collection.query(query_embeddings=[query_emb], n_results=limit * 3)
            matched = []
            if results.get("ids") and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    doc_file = metadata.get("file", "")
                    if files and doc_file not in files:
                        continue
                    if not doc_file:
                        continue
                    matched.append({
                        "doc_id": doc_id,
                        "file": doc_file,
                        "name": metadata.get("name", ""),
                        "kind": metadata.get("kind", ""),
                        "score": results["distances"][0][i] if results.get("distances") else 1.0
                    })
                    if len(matched) >= limit:
                        break
            return matched
        except Exception:
            return []

        py_files = list(lib_dir.glob("*.py"))
        new_count = 0
        update_count = 0
        for f in py_files:
            if f.name.startswith("_"):
                continue
            filepath = str(f.relative_to(self.project_root))
            new_hash = self._file_hash(filepath)
            if filepath not in self._file_hashes:
                if self.index_file(filepath):
                    new_count += 1
            elif self._file_hashes[filepath] != new_hash:
                if self.index_file(filepath):
                    update_count += 1
        if new_count or update_count:
            print(f"[CodeIndexer] 索引更新: +{new_count} 新, ~{update_count} 变更")
        else:
            print(f"[CodeIndexer] 索引已是最新 ({len(self._keyword_index)} 个文件)")

    def auto_init(self):
        """自动初始化索引 - 索引整个项目"""
        import os
        indexed = 0
        
        # 索引多个目录
        # 全量扫描：索引项目所有 .py 文件
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "node_modules", ".venv", "venv", "data", "exports", "logs", "memory")]
            for f in files:
                if not f.endswith(".py") or f.startswith("_"):
                    continue
                full_path = Path(root) / f
                try:
                    filepath = str(full_path.relative_to(self.project_root))
                except ValueError:
                    continue

                new_hash = self._file_hash(filepath)
                if filepath in self._file_hashes and self._file_hashes[filepath] == new_hash:
                    continue

                if self.index_file(filepath):
                    indexed += 1

        if indexed:
            print(f"[CodeIndexer] Index updated: {indexed} files")
        else:
            print(f"[CodeIndexer] Index up to date ({len(self._keyword_index)} files)")
            self._save()

    def stats(self) -> Dict:
        return {
            "indexed_files": len(self._keyword_index),
            "total_keywords": sum(len(v) for v in self._keyword_index.values())
        }


# 全局单例 - 由 startup 系统初始化
code_indexer = None
