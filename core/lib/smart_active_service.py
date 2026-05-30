"""智能主动服务 - 自动索引、清理、优化"""

import time
import threading
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class SmartActiveService:
    """智能主动服务"""

    def __init__(self):
        self.last_index_time = {}
        self.running = False
        self.thread = None
        print("💡 智能主动服务已启动")

    def start(self):
        """启动主动服务"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("✅ 主动服务循环已启动")

    def stop(self):
        self.running = False

    def _run(self):
        """主循环"""
        while self.running:
            try:
                # 1. 扫描并索引新文件（每10分钟）
                self._auto_index_files()

                # 2. 清理过期数据（每1小时）
                self._cleanup_expired()

                # 3. 健康检查（每5分钟）
                self._health_check()

                time.sleep(600)  # 10分钟
            except Exception as e:
                print(f"主动服务错误: {e}")
                time.sleep(60)

    def _auto_index_files(self):
        """自动索引新文件"""
        from core.lib.vector_knowledge_center import vector_knowledge_center

        # 需要监控的目录
        watch_dirs = {
            "docs": Path("docs"),
            "dreamshaper_outputs": Path("dreamshaper_outputs"),
            "data/output": Path("data/output"),
        }

        for name, watch_dir in watch_dirs.items():
            if not watch_dir.exists():
                continue

            for file_path in watch_dir.rglob("*"):
                if not file_path.is_file():
                    continue

                suffix = file_path.suffix.lower()
                if suffix not in ['.md', '.png', '.jpg', '.mp4']:
                    continue

                # 检查是否需要索引
                file_key = str(file_path.absolute())
                mtime = file_path.stat().st_mtime
                last_time = self.last_index_time.get(file_key, 0)

                if mtime > last_time:
                    self._index_file(file_path, vector_knowledge_center)
                    self.last_index_time[file_key] = mtime

    def _index_file(self, file_path: Path, vector_center):
        """索引单个文件"""
        try:
            if file_path.suffix in ['.png', '.jpg', '.jpeg']:
                # 图片索引
                from core.agents.builtin.vision_agent import VisionAgent
                vision = VisionAgent()
                result = vision.describe_image(str(file_path))
                description = result.get('description', f"图片: {file_path.name}")
                doc_id = f"image_{file_path.stem}_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}"

            elif file_path.suffix == '.mp4':
                # 视频索引
                from core.agents.builtin.video_indexer_agent import VideoIndexerAgent
                indexer = VideoIndexerAgent()
                result = indexer.describe_video(str(file_path))
                description = result.get('description', f"视频: {file_path.name}")
                doc_id = f"video_{file_path.stem}_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}"

            else:
                # 文档索引
                content = file_path.read_text(encoding='utf-8')[:2000]
                description = f"文档: {file_path.name}\n内容: {content[:500]}"
                doc_id = f"doc_{file_path.stem}_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}"

            vector_center.add_document(
                doc_id=doc_id,
                content=description,
                metadata={
                    "type": file_path.suffix[1:],
                    "file": str(file_path),
                    "filename": file_path.name,
                    "auto_indexed": True,
                    "indexed_at": datetime.now().isoformat()
                }
            )
            print(f"   📄 [主动服务] 自动索引: {file_path.name}")

        except Exception as e:
            print(f"   ❌ [主动服务] 索引失败 {file_path.name}: {e}")

    def _cleanup_expired(self):
        """清理过期数据"""
        print(f"   🧹 [主动服务] 清理过期数据")

    def _health_check(self):
        """健康检查"""
        from core.lib.vector_knowledge_center import vector_knowledge_center
        print(f"   💚 [主动服务] 健康检查...")
        for name, col in vector_knowledge_center.collections.items():
            print(f"      {name}: {col.count()} 条")

    def on_task_complete(self, agent: str, user_id: str, task: str, data: Dict):
        """任务完成时触发"""
        print(f"   🎯 [主动服务] {agent} 完成任务: {task}")

    def on_error(self, agent: str, user_id: str, error: str):
        """错误时触发"""
        print(f"   🚨 [主动服务] {agent} 发生错误: {error}")

    def should_serve(self, agent: str, context: Dict) -> Dict:
        """判断是否需要主动服务"""
        return {"should": True, "reason": "auto_index", "priority": 1}

    def _check_performance(self):
        """性能检查"""
        import psutil
        import platform

        if platform.system() == 'Windows':
            return

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent

            if cpu_percent > 80:
                print(f"   ⚠️ CPU 使用率过高: {cpu_percent}%")
            if memory_percent > 80:
                print(f"   ⚠️ 内存使用率过高: {memory_percent}%")
        except Exception as e:
            print(f"性能监控错误: {e}")


# 全局实例
smart_service = SmartActiveService()
