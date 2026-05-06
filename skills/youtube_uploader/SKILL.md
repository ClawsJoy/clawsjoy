---
name: clawsjoy-youtube-upload
description: 自动上传视频到 YouTube
version: 1.0.0
parameters:
  - name: topic
    type: string
    description: 视频主题
    required: false
    default: "香港优才计划"
  - name: privacy
    type: string
    description: 隐私状态 (public/unlisted/private)
    default: "unlisted"
---

# YouTube 上传 Skill

自动将最新生成的视频上传到 YouTube。

## 使用示例

```python
execute_skill("clawsjoy-youtube-upload", {
    "topic": "香港优才计划",
    "privacy": "public"
})
