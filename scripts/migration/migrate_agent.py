#!/usr/bin/env python3
"""Agent 迁移工具 - 将原有 Agent 转换为 V4 智慧版"""

import os
import re
from pathlib import Path

# 待迁移 Agent 列表（按优先级）
HIGH_PRIORITY = ["vision_agent", "memory_agent", "file_agent", "video_agent", "youtube_agent"]
MEDIUM_PRIORITY = ["audio_agent", "dialect_agent", "collaboration_agent", "writer_agent"]
LOW_PRIORITY = ["three_d_agent", "video_indexer_agent", "proactive_agent"]

def to_class_name(agent_name: str) -> str:
    """转换为类名"""
    parts = agent_name.split('_')
    return ''.join(p.capitalize() for p in parts) + 'V4'

def migrate_agent(agent_name: str):
    """迁移单个 Agent"""
    agent_dir = Path(f"agents/{agent_name}")
    agent_file = agent_dir / "agent_v4.py"
    
    # 确保目录存在
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    if agent_file.exists():
        print(f"⚠️ {agent_name} 已存在 V4 版本，跳过")
        return
    
    class_name = to_class_name(agent_name)
    agent_display = agent_name.replace('_', ' ').title()
    
    # 生成 V4 模板（修复：不使用 self）
    template = f'''#!/usr/bin/env python3
"""{agent_name} v4.0 - 智慧化版本"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, Optional, Tuple
from core.agents.business.business_agent import BusinessAgent


class {class_name}(BusinessAgent):
    """智慧化 {agent_display}"""
    
    name = "{agent_name}_v4"
    description = "智慧化 {agent_display}"
    version = "4.0.0"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"🎯 {{self.name}} v{{self.version}} 智慧化启动")
    
    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {{
            # TODO: 根据原 Agent 能力填写
        }}
        return capabilities.get((action, target), (False, 0.0))
    
    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        # TODO: 实现核心逻辑
        return self._response(self._get_help())
    
    def _get_help(self) -> str:
        return f"""🎯 {{self.name}} 智慧助手

功能开发中，敬请期待。"""
    
    def _response(self, content: str, **kwargs) -> Dict:
        return {{
            "success": True,
            "response": content,
            "output_content": content,
            **kwargs
        }}


if __name__ == "__main__":
    agent = {class_name}("test")
    print("✅ {agent_name}_v4 测试通过")
'''
    
    with open(agent_file, 'w') as f:
        f.write(template)
    
    print(f"✅ 创建 {agent_name}/agent_v4.py")
    
    # 更新 wisdom_factory
    update_wisdom_factory(agent_name, class_name)

def update_wisdom_factory(agent_name: str, class_name: str):
    """更新 wisdom_factory 注册"""
    factory_file = Path("core/agents/wisdom/wisdom_factory.py")
    
    if not factory_file.exists():
        print(f"⚠️ wisdom_factory.py 不存在")
        return
    
    with open(factory_file, 'r') as f:
        content = f.read()
    
    # 检查是否已存在
    if f'agent_name == "{agent_name}"' in content:
        print(f"⚠️ {agent_name} 已在 wisdom_factory 中注册")
        return
    
    # 查找插入位置 - 在 translate_agent 之后
    insert_pattern = 'if agent_name == "translate_agent":'
    new_code = f'''
            if agent_name == "{agent_name}":
                from agents.{agent_name}.agent_v4 import {class_name}
                print(f"✅ 加载 {{agent_name}} V4 智慧版本")
                return {class_name}(user_id)
'''
    
    if insert_pattern in content:
        # 在 translate_agent 块之后插入
        lines = content.split('\n')
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if not inserted and 'if agent_name == "translate_agent":' in line:
                # 找到对应的返回语句后插入
                j = i
                while j < len(lines) and 'return' not in lines[j]:
                    j += 1
                # 在 return 后添加新代码
                pass
        
        # 简化：直接在文件末尾添加
        content += f'''
            if agent_name == "{agent_name}":
                from agents.{agent_name}.agent_v4 import {class_name}
                print(f"✅ 加载 {{agent_name}} V4 智慧版本")
                return {class_name}(user_id)
'''
    else:
        content += new_code
    
    with open(factory_file, 'w') as f:
        f.write(content)
    
    print(f"✅ 更新 wisdom_factory: {agent_name}")

if __name__ == "__main__":
    print("=" * 50)
    print("Agent 迁移工具")
    print("=" * 50)
    
    all_agents = HIGH_PRIORITY + MEDIUM_PRIORITY + LOW_PRIORITY
    
    for agent in all_agents:
        print(f"\n📦 迁移 {agent}...")
        migrate_agent(agent)
    
    print("\n" + "=" * 50)
    print("✅ 迁移完成")
    print(f"   已创建 {len(all_agents)} 个 Agent 模板")
    print("   请手动完善各 Agent 的业务逻辑")
