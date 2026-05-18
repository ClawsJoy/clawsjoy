# DreamShaper 文生图原子技能

## 基本信息

| 属性 | 值 |
|------|-----|
| 技能名称 | `dreamshaper_text2img` |
| 版本 | 1.0.0 |
| 类型 | atomic |
| 分类 | image |
| 作者 | ClawsJoy |
| 兼容系统 | openclaw, clawsjoy |

## 功能描述

基于 DreamShaper XL 的高质量文本生成图像原子技能。DreamShaper 是 SDXL 的微调模型，擅长生成高质量、高细节的艺术图像，适合海报、插画、概念图等场景。

## 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `prompt` | string | ✅ | - | 图像描述提示词（推荐英文） |
| `negative_prompt` | string | ❌ | "low quality, blurry, ugly" | 负面提示词 |
| `steps` | integer | ❌ | 15 | 推理步数 (1-50) |
| `width` | integer | ❌ | 768 | 图像宽度 |
| `height` | integer | ❌ | 768 | 图像高度 |
| `cfg` | float | ❌ | 7.5 | 引导系数 (1-15) |

## 使用示例

### 命令行调用
```bash
# 基础用法
python3 tools/dreamshaper_skill.py --prompt "A beautiful sunset over mountains" --json

# 指定参数
python3 tools/dreamshaper_skill.py \
  --prompt "A cute cat wearing a tiny hat" \
  --steps 20 \
  --width 1024 \
  --height 768 \
  --cfg 8.0 \
  --json
JSON 输出示例
{
  "success": true,
  "image_path": "output/dreamshaper_1734567890.png",
  "elapsed_time": 15.2,
  "prompt": "A beautiful sunset over mountains"
}
环境变量
变量	默认值	说明
CLAWSJOY_DREAMSHAPER_PATH	/mnt/d/clawsjoy_clean/models/dreamshaper	模型路径
CLAWSJOY_OUTPUT_DIR	/mnt/d/clawsjoy_clean/output	输出目录
CLAWSJOY_DREAMSHAPER_STEPS	15	默认步数
CLAWSJOY_DREAMSHAPER_WIDTH	768	默认宽度
CLAWSJOY_DREAMSHAPER_HEIGHT	768	默认高度
CLAWSJOY_DREAMSHAPER_CFG	7.5	默认引导系数
提示词示例
风景
A breathtaking landscape of a sunset over mountains, with dramatic orange and purple clouds, reflections on a calm lake, cinematic lighting, ultra HD, 8k resolution
人物/角色
A cute 3D rendered cartoon of a chubby orange cat, wearing a tiny detective hat, holding a magnifying glass, Pixar style, pastel colors, soft lighting, blind box toy aesthetic
科幻
Concept art of a futuristic cyberpunk motorcycle with neon blue lights, parked in a rainy alley, dark moody atmosphere, highly detailed, 8k, unreal engine 5
中国风
Traditional Chinese ink wash painting, a solitary fisherman on a boat in a misty river, distant mountains fading into the fog, elegant and poetic, minimalist style
性能参考 (RTX 2060 6GB)
分辨率	步数	耗时
512x512	15	~30秒
768x768	15	~60秒
1024x1024	20	~120秒
依赖
diffusers

torch

transformers

accelerate

注意事项
首次运行会加载模型（约 10GB fp16 版本）

6GB 显存需开启 enable_model_cpu_offload()

建议使用英文提示词以获得最佳效果

生成大尺寸图片时耗时较长，请耐心等待

相关文档
DreamShaper 模型主页

Stable Diffusion XL 文档
