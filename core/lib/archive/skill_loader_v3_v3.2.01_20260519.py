from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""技能加载器 V3 - 支持分类目录结构"""
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Optional
from core.lib.unified_config import unified_config
from core.lib.unified_config import unified_config
sys.path.insert(0, str(Path(__file__).parent.parent))

class SkillLoaderV3:
    """统一技能加载器 - 支持分类目录"""
    
    CATEGORIES = {
        'core': '核心调度',
        'math': '数学计算',
        'image': '图像处理',
        'video': '视频制作',
        'text': '文本处理',
        'audio': '音频处理',
        'network': '网络服务',
        'memory': '记忆系统',
        'self_heal': '自愈系统',
        'tools': '工具集',
        'wrappers': '包装器'
    }
    
    def __init__(self):
        self.skills = {}
        # 从配置文件加载分类
        import yaml
        from pathlib import Path
        config_file = Path(__file__).parent.parent / "config/skill_categories.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = unified_config.get('skill_categories', {})
                self.CATEGORIES = config.get('categories', {})
        else:
            # 默认分类（硬编码后备）
            self.CATEGORIES = {
                "core": "核心调度",
                "math": "数学计算",
                "image": "图像处理",
                "video": "视频制作",
                "text": "文本处理",
                "audio": "音频处理",
                "network": "网络服务",
                "memory": "记忆系统",
                "self_heal": "自愈系统",
                "tools": "工具集",
                "wrappers": "包装器",
            }
        self.categories = {cat: [] for cat in self.CATEGORIES.keys()}
        self._load_all()

    def _load_all(self):
        """加载所有分类目录中的技能"""
        for cat_dir in self.CATEGORIES.keys():
            cat_path = Path(f"skills/{cat_dir}")
            if not cat_path.exists():
                continue
            
            for py_file in cat_path.glob("*.py"):
                if py_file.stem == '__init__':
                    continue
                skill_name = py_file.stem
                self.categories[cat_dir].append(skill_name)
                self.skills[skill_name] = {
                    'name': skill_name,
                    'category': cat_dir,
                    'category_name': self.CATEGORIES[cat_dir],
                    'file': str(py_file),
                    'path': f"skills.{cat_dir}.{skill_name}"
                }
        
        print(f"✅ 技能加载器 V3 已初始化")
        print(f"   总技能: {len(self.skills)} 个")
        for cat, skills in self.categories.items():
            if skills:
                print(f"   {self.CATEGORIES[cat]}: {len(skills)} 个")
    
    def get_skill(self, name: str):
        info = self.skills.get(name)
        if not info:
            return None
        try:
            module = importlib.import_module(info['path'])
            if hasattr(module, 'skill'):
                return module.skill
        except Exception as e:
            print(f"加载技能 {name} 失败: {e}")
        return None
    
    def execute(self, name: str, params: Dict) -> Dict:
        skill = self.get_skill(name)
        if skill:
            try:
                return skill.execute(params)
            except Exception as e:
                return {"success": False, "error": str(e)}
        return {"success": False, "error": f"技能不存在: {name}"}
    
    def list_skills(self, category: str = None) -> List[str]:
        if category and category in self.categories:
            return self.categories[category]
        return list(self.skills.keys())
    
    def get_categories(self) -> Dict:
        return {
            cat: {'name': self.CATEGORIES[cat], 'count': len(skills), 'skills': skills}
            for cat, skills in self.categories.items() if skills
        }

skill_loader = SkillLoaderV3()

__version__ = "3.2.1"
__version_date__ = "2026-05-19"
__version_author__ = "ClawsJoy"
__changelog__ = "改为从 config/skill_categories.yaml 读取分类，配置驱动"
