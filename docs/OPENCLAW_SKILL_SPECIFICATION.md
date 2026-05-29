# ClawsJoy OpenClaw 技能开发规范

## 版本信息
- 版本: 1.0.0
- 更新日期: 2026-05-27
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
├── {category}/ # 分类目录（如 image, math, video）
│ ├── SKILL.md # 技能元数据（必需）
│ ├── manifest.json # 技能清单（可选）
│ └── {skill_name}.py # 技能实现（必需）
├── audio/ # 音频处理
├── image/ # 图像处理
├── math/ # 数学计算
├── video/ # 视频制作
└── ...

### 支持的分类（来自 config/skill_categories.yaml）

| 分类 | 说明 | 分类 | 说明 |
|------|------|------|------|
| audio | 音频处理 | image | 图像处理 |
| math | 数学计算 | video | 视频制作 |
| translate | 翻译服务 | course | 课程学习 |
| file | 文件操作 | network | 网络请求 |
| ... | ... | ... | ... |


## 三、技能文件规范

### 3.1 技能实现文件 ({skill_name}.py)

```python
"""技能描述 - 一行说明功能"""

import requests  # 按需导入
from pathlib import Path


class SkillName:
    """技能类，名称与文件名对应"""
    
    # ========== 必需属性 ==========
    name = "skill_name"           # 技能标识符（与文件名一致）
    description = "技能功能描述"   # 简要说明
    version = "1.0.0"             # 版本号
    category = "image"            # 分类（与目录名一致）
    
    # ========== 必需方法 ==========
    def execute(self, params: dict) -> dict:
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
        # 1. 参数提取与验证
        param1 = params.get('param1', '')
        if not param1:
            return {"success": False, "error": "param1 is required"}
        
        # 2. 业务逻辑实现
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

# Skill Name

## 参数
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| param1 | string | 是 | 参数说明 |

## 返回值
| 字段 | 类型 | 描述 |
|------|------|------|
| success | boolean | 是否成功 |
| result | string | 执行结果 |

## 示例
```json
{"skill": "skill_name", "params": {"param1": "value"}}

---

## 五、manifest.json 清单文件（可选）

```json
{
  "name": "skill_name",
  "type": "atomic",
  "version": "1.0.0",
  "description": "技能功能描述",
  "category": "image",
  "author": "ClawsJoy",
  "input_schema": {
    "param1": {"type": "string", "required": true, "description": "参数说明"}
  },
  "output_schema": {
    "success": {"type": "boolean"},
    "result": {"type": "string"}
  }
}
##六、技能示例
###6.1 加法技能 (skills/math/add.py)
"""加法技能"""

class AddSkill:
    name = "add"
    description = "两数相加"
    version = "1.0.0"
    category = "math"
    
    def execute(self, params: dict) -> dict:
        a = params.get('a', 0)
        b = params.get('b', 0)
        return {"success": True, "result": a + b}

skill = AddSkill()
###6.2 图像识别技能 (skills/image/vision.py)
"""图像识别技能 - 使用 moondream 模型"""

import base64
import requests
from pathlib import Path


class VisionSkill:
    name = "vision"
    description = "图像识别，使用 moondream 模型"
    version = "1.0.0"
    category = "image"
    
    def execute(self, params: dict) -> dict:
        image_path = params.get('image_path', '')
        prompt = params.get('prompt', '描述这张图片')
        
        if not image_path:
            return {"success": False, "error": "image_path required"}
        
        path = Path(image_path)
        if not path.exists():
            return {"success": False, "error": f"Image not found: {image_path}"}
        
        with open(path, 'rb') as f:
            img_base64 = base64.b64encode(f.read()).decode()
        
        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "moondream:1.8b",
                    "prompt": prompt,
                    "images": [img_base64],
                    "stream": False
                },
                timeout=60
            )
            
            if resp.status_code == 200:
                return {
                    "success": True,
                    "result": resp.json().get('response', ''),
                    "image": str(path)
                }
            return {"success": False, "error": f"API error: {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


skill = VisionSkill()
##七、技能自动注册机制
###7.1 注册流程
#技能文件放入 skills/{category}/
        ↓
#SkillLoaderV3._load_all() 扫描目录
        ↓
#读取 skills/{category}/*.py
        ↓
#提取技能名称（文件名）
        ↓
#记录到 self.skills 字典
        ↓
#分类记录到 self.categories
        ↓
API 可调用
###7.2 热重载触发
# 方式1：API 调用
curl -X POST http://localhost:5002/api/hot_reload_skills

# 方式2：修改配置文件自动触发
# 修改 config/skill_categories.yaml 会自动触发重载
###7.3 验证技能是否注册成功
# 查看技能列表
curl http://localhost:5002/api/skills | jq '.skills | contains(["vision"])'

# 查看技能详情
python3 -c "
from lib.skill_loader_v3 import skill_loader
print('vision' in skill_loader.list_skills())
"
##八、技能调用
###8.1 API 调用
curl -X POST http://localhost:5002/api/skills/execute \
  -H "Content-Type: application/json" \
  -d '{"skill": "vision", "params": {"image_path": "/path/to/image.jpg"}}'
###8.2 响应格式
{
  "success": true,
  "result": {
    "success": true,
    "result": "识别结果描述",
    "image": "/path/to/image.jpg"
  },
  "skill": "vision"
}
##九、常见问题
###Q1: 技能文件放入目录后未自动注册？
#检查清单：
#文件是否在正确的分类目录下？

#文件名是否与 name 属性一致？

#是否有 skill = ClassName() 全局实例？

#类是否有 execute 方法？

#分类目录是否在 skill_categories.yaml 中定义？
###Q2: 修改技能后不生效？
#解决方案：
# 触发技能热重载
curl -X POST http://localhost:5002/api/hot_reload_skills

# 或重启网关
pkill -f gunicorn && gunicorn -w 2 -k gevent --bind 0.0.0.0:5002 agent_gateway_enhanced:app --daemon
###Q3: 技能执行返回"技能不存在"？
#原因： 技能未被 skill_registry_v2 注册

#解决：
from lib.skill_registry_v2 import skill_registry
skill_registry.register("vision", "image", "1.0.0")
###Q4: 技能执行报错 "execute() takes 1 positional argument but 2 were given"？
#原因： 技能是函数形式，不是类实例

#解决： 使用类形式，末尾创建 skill = ClassName() 实例
##十、最佳实践
#命名规范：技能名使用小写加下划线（如 image_recognition）

#错误处理：所有 execute 方法必须 try-except

#超时设置：网络请求设置合理 timeout

#文档完整：SKILL.md 必须包含参数说明

#版本管理：修改技能时更新 version 字段
##十一、技能与向量化系统集成
#技能创建后会自动被向量化系统索引：
# 技能描述被向量化用于语义搜索
skills = skill_recommender.recommend("识别图片内容", n=3)
# 返回: ['vision', 'image_recognition', ...]
##附录：常用命令
# 查看所有技能
curl http://localhost:5002/api/skills | jq '.skills'

# 执行技能
curl -X POST http://localhost:5002/api/skills/execute \
  -H "Content-Type: application/json" \
  -d '{"skill": "add", "params": {"a": 1, "b": 2}}'

# 技能语义推荐
curl -X POST http://localhost:5002/api/skills/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "图片识别"}'

# 热重载技能
curl -X POST http://localhost:5002/api/hot_reload_skills
#本规范基于 ClawsJoy v5.0 实际验证，遵循 OpenClaw 社区标准
