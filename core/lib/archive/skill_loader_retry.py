from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""技能加载器 - 带重试机制"""

import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional

class SkillLoaderWithRetry:
    """带重试机制的技能加载器"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.failed_skills = {}  # 记录失败的技能
        self.loaded_skills = {}

    def load_skill_with_retry(self, skill_path: Path) -> Optional[object]:
        """带重试的加载技能"""
        skill_name = skill_path.stem

        for attempt in range(self.max_retries):
            try:
                # 尝试加载
                import importlib.util
                spec = importlib.util.spec_from_file_location(skill_name, skill_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找 skill 实例
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, 'execute') and callable(attr.execute):
                        self.loaded_skills[skill_name] = attr
                        # 清除失败记录
                        if skill_name in self.failed_skills:
                            del self.failed_skills[skill_name]
                        return attr
                
                raise Exception(f"未找到 execute 方法")
                
            except Exception as e:
                error_msg = str(e)
                self.failed_skills[skill_name] = {
                    "error": error_msg,
                    "attempt": attempt + 1,
                    "timestamp": time.time()
                }
                
                if attempt < self.max_retries - 1:
                    print(f"🔄 重试加载 {skill_name} ({attempt+1}/{self.max_retries}): {error_msg[:50]}")
                    time.sleep(self.retry_delay * (attempt + 1))  # 递增延迟
                else:
                    print(f"❌ 加载失败 {skill_name}: {error_msg[:100]}")

        return None
    
    def retry_failed(self) -> Dict:
        """重试所有失败的技能"""
        print(f"\n🔄 重试加载失败的技能 ({len(self.failed_skills)} 个)")

        retry_results = {}
        for skill_name in list(self.failed_skills.keys()):
            # 查找技能文件
            skill_file = Path(f"skills/{skill_name}.py")
            if skill_file.exists():
                result = self.load_skill_with_retry(skill_file)
                retry_results[skill_name] = result is not None
            else:
                # 可能在子目录中
                for subdir in Path("skills").iterdir():
                    if subdir.is_dir():
                        skill_file = subdir / f"{skill_name}.py"
                        if skill_file.exists():
                            result = self.load_skill_with_retry(skill_file)
                            retry_results[skill_name] = result is not None
                            break

        success_count = sum(1 for v in retry_results.values() if v)
        print(f"\n📊 重试结果: {success_count}/{len(retry_results)} 成功")

        return retry_results
    
    def get_failed_skills(self) -> Dict:
        """获取失败的技能列表"""
        return self.failed_skills
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "loaded": len(self.loaded_skills),
            "failed": len(self.failed_skills),
            "failed_details": self.failed_skills
        }

# 全局实例
skill_retry_loader = SkillLoaderWithRetry()
