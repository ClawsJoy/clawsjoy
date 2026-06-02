# ClawsJoy OpenClaw 技能开发规范

## 版本信息
- 版本: 2.0.0
- 更新日期: 2026-06-02
- 适用系统: ClawsJoy v5.0+

---

## 一、概述

ClawsJoy 采用 **OpenClaw 社区规范** 管理所有原子技能。技能系统具备以下核心特性：

- **自动发现**：技能文件放入正确目录后自动注册
- **热重载**：修改技能后无需重启网关
- **向量化索引**：技能描述自动向量化，支持语义匹配
- **多租户隔离**：技能按用户隔离执行

---

## 二、技能目录结构
skills/
├── {category}/ # 分类目录
│ ├── SKILL.md # 技能元数据（必需）
│ ├── manifest.json # 技能清单（可选）
│ └── skill.py # 技能实现（必需）
├── threejs/ # 3D Web 渲染
├── gpu_safe/ # GPU 安全渲染
├── opengl/ # OpenGL 本地渲染
├── panorama/ # 360° 全景
├── image/ # 图像处理
├── video/ # 视频制作
├── audio/ # 音频处理
└── ...

### 支持的分类

| 分类 | 说明 | 分类 | 说明 |
|------|------|------|------|
| 3d | 3D 渲染 | image | 图像处理 |
| video | 视频制作 | audio | 音频处理 |
| math | 数学计算 | translate | 翻译服务 |
| file | 文件操作 | network | 网络请求 |

---

## 三、技能文件规范

### 3.1 技能实现文件 (skill.py)

```python
"""技能描述 - 一行说明功能"""

from typing import Dict, Any


class SkillName:
    """技能类，名称与文件名对应"""
    
    # ========== 必需属性 ==========
    name = "skill_name"           # 技能标识符（与文件名一致）
    description = "技能功能描述"   # 简要说明
    version = "1.0.0"             # 版本号
    category = "image"            # 分类（与目录名一致）
    
    # ========== 必需方法 ==========
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        技能执行入口
        
        Args:
            params: 参数字典
                - 具体参数根据技能功能定义
            
        Returns:
            dict: 必须包含 success 字段
                - {"success": True, "result": "执行结果"}
                - {"success": False, "error": "错误信息"}
        """
        param1 = params.get('param1', '')
        if not param1:
            return {"success": False, "error": "param1 is required"}
        
        try:
            result = self._do_something(param1)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _do_something(self, param):
        """私有辅助方法"""
        return f"processed: {param}"


# ========== 全局实例（必需）==========
skill = SkillName()
###3.2 关键要点
#要素	要求	说明
#类名	{SkillName}	与文件名对应，首字母大写
#属性 name	字符串	技能唯一标识，与文件名一致
#属性 description	字符串	技能功能描述
#属性 version	字符串	语义化版本号
#属性 category	字符串	必须与所在目录名一致
#方法 execute	函数	接收 params，返回 dict
#全局实例 skill	对象	skill = SkillName()
###3.3 返回值规范
#成功时：{"success": True, "result": "执行结果数据"}
#失败时：{"success": False, "error": "错误描述"}
##四、SKILL.md 元数据文件
---
name: skill_name
version: 1.0.0
description: '技能功能描述'
author: ClawsJoy
security_grade: 🟢 A
use_when: 使用场景描述
not_for: 不适用场景
category: image
---
##五、实际验证的技能示例
###5.1 3D 渲染技能 (skills/threejs/skill.py)
"""Three.js 3D 场景生成技能"""

from pathlib import Path
from typing import Dict, Any


class ThreeJSSkill:
    name = "threejs"
    description = "生成 Three.js 3D 场景 HTML 文件"
    version = "1.0.0"
    category = "3d"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        shape = params.get('shape', 'cube')
        color = params.get('color', '#ff6600')
        output_path = params.get('output', f"data/output/3d_{shape}.html")
        
        try:
            html = self._generate_html(shape, color)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(html)
            return {"success": True, "result": output_path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_html(self, shape: str, color: str) -> str:
        # 生成 Three.js HTML
        return f"<html>...</html>"


skill = ThreeJSSkill()
###5.2 GPU 安全渲染技能 (skills/gpu_safe/skill.py)
"""GPU 安全渲染技能"""

import subprocess
from pathlib import Path
from typing import Dict, Any


class GPUSafeRenderSkill:
    name = "gpu_safe_render"
    description = "使用 Blender GPU 渲染 3D 场景"
    version = "1.0.0"
    category = "3d"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        shape = params.get('shape', 'cube')
        output_path = params.get('output', f"data/output/gpu_safe/{shape}.png")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Blender 渲染脚本
        script = f"..."
        result = subprocess.run(["blender", "-b", "--python-expr", script], ...)
        
        if result.returncode == 0:
            return {"success": True, "result": output_path}
        return {"success": False, "error": "渲染失败"}


skill = GPUSafeRenderSkill()
##六、技能自动注册机制
###6.1 注册流程
技能文件放入 skills/{category}/
        ↓
SkillLoaderV3._load_all() 扫描目录
        ↓
读取 skills/{category}/skill.py
        ↓
提取技能属性 (name, description, version, category)
        ↓
记录到 self.skills 字典
        ↓
分类记录到 self.categories
        ↓
API 可调用
###6.2 热重载触发
# 方式1：API 调用
curl -X POST http://localhost:5002/api/hot_reload_skills

# 方式2：修改技能文件自动触发
# 系统会自动检测变化
###6.3 验证技能是否注册成功
# 查看技能列表
curl http://localhost:5002/api/skills | jq '.skills'

# 查看技能详情
python3 -c "
from core.lib.skill_loader_v3 import skill_loader
print('vision' in skill_loader.list_skills())
"
##七、技能调用
###7.1 API 调用
curl -X POST http://localhost:5002/api/skills/execute \
  -H "Content-Type: application/json" \
  -d '{"skill": "threejs", "params": {"shape": "cube", "color": "#ff6600"}}'
###7.2 响应格式
{
  "success": true,
  "result": "data/output/3d_cube.html",
  "skill": "threejs"
}
##八、常见问题
#Q1: 技能文件放入目录后未自动注册？
#检查清单：
#文件是否在正确的分类目录下？
#文件名是否与 name 属性一致？
#是否有 skill = ClassName() 全局实例？
#类是否有 execute 方法？
#分类目录是否在 skill_categories.yaml 中定义？
#Q2: 修改技能后不生效？
#解决方案：
# 触发技能热重载
curl -X POST http://localhost:5002/api/hot_reload_skills
#Q3: 技能执行返回"技能不存在"？
#原因： 技能未被 skill_loader 发现
#解决： 检查技能文件是否符合规范，重启服务
##九、最佳实践
#命名规范：技能名使用小写加下划线（如 image_recognition）
#错误处理：所有 execute 方法必须 try-except
#超时设置：网络请求设置合理 timeout
#文档完整：SKILL.md 必须包含参数说明
#版本管理：修改技能时更新 version 字段
##十、已测试通过的技能列表
#技能	分类	功能	测试状态
#threejs	3d	Web 3D 场景	✅
#gpu_safe	3d	Blender GPU 渲染	✅
#opengl	3d	本地 OpenGL 渲染	✅
#panorama	3d	360° 全景	✅
#vision	image	图像识别	✅
#ffmpeg_video	video	视频处理	✅
##附录：常用命令
# 查看所有技能
curl http://localhost:5002/api/skills

# 执行技能
curl -X POST http://localhost:5002/api/skills/execute \
  -H "Content-Type: application/json" \
  -d '{"skill": "threejs", "params": {"shape": "cube"}}'

# 热重载技能
curl -X POST http://localhost:5002/api/hot_reload_skills
#本规范基于 ClawsJoy v5.0 实际验证，遵循 OpenClaw 社区标准
