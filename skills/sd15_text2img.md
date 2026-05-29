# SD 1.5 文生图原子技能

## 基本信息

| 属性 | 值 |
|------|-----|
| 技能名称 | `sd15_text2img` |
| 版本 | 1.0.0 |
| 类型 | atomic |
| 分类 | image |
| 作者 | ClawsJoy |
| 兼容系统 | openclaw, clawsjoy |

## 功能描述

基于 Stable Diffusion 1.5 的文本生成图像原子技能，支持中文提示词，轻量快速，适合 6GB 显存环境。

## 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `prompt` | string | ✅ | - | 图像描述提示词（支持中文） |
| `negative_prompt` | string | ❌ | "low quality, blurry" | 负面提示词 |
| `steps` | integer | ❌ | 20 | 推理步数 (1-50) |
| `width` | integer | ❌ | 512 | 图像宽度 |
| `height` | integer | ❌ | 512 | 图像高度 |
| `cfg` | float | ❌ | 7.0 | 引导系数 (1-15) |
| `output` | string | ❌ | 自动生成 | 输出路径 |

## 使用示例

### 命令行调用
```bash
python3 tools/sd15_skill.py --prompt "一只可爱的猫咪" --json
JSON 输出示例
{
  "success": true,
  "image_path": "output/sd15_1734567890.png",
  "elapsed_time": 15.2,
  "prompt": "一只可爱的猫咪"
}
环境变量
变量	默认值	说明
CLAWSJOY_SD15_PATH	/mnt/d/clawsjoy_clean/models/sd15	模型路径
CLAWSJOY_OUTPUT_DIR	/mnt/d/clawsjoy_clean/output	输出目录
CLAWSJOY_SD15_STEPS	20	默认步数
CLAWSJOY_SD15_WIDTH	512	默认宽度
CLAWSJOY_SD15_HEIGHT	512	默认高度
CLAWSJOY_SD15_CFG	7.0	默认引导系数
依赖
diffusers

torch

transformers

accelerate

注意事项
首次运行会下载模型（约 4GB）

6GB 显存可流畅运行

支持中文提示词，建议使用自然语言描述
