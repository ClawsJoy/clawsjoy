# ClawsJoy 脚本库

## 脚本列表

| Agent | 脚本 |
|-------|------|
| Writer | write_review |
| Designer | write_design |
| Video-Maker | write_video, make_video |
| Spider | write_data |
| Messenger | write_publish |
| Engineer | write_deploy |

## 目录结构

~/clawsjoy/bin/
├── content/     # write_review
├── design/      # write_design
├── video/       # write_video, make_video
├── data/        # write_data
├── publish/     # write_publish
├── deploy/      # write_deploy
└── utils/       # 辅助工具

## 用法示例

~/clawsjoy/bin/write_review "标题" "内容" "writer"


## 视频脚本（完整版）

| 脚本 | 功能 |
|------|------|
| `make_video` | 多图轮播 + TTS + 字幕 + 标题 |
| `compress_video` | 压缩视频文件 |
| `add_subtitle` | 为视频添加字幕 |
| `video_trim` | 裁剪视频 |
| `concat_video` | 合并多个视频 |
| `extract_audio` | 提取音频（待开发） |
| `add_watermark` | 添加水印（待开发） |

## 视频脚本（完整版）

| 脚本 | 功能 |
|------|------|
| `make_video` | 多图轮播 + TTS + 字幕 + 标题 |
| `compress_video` | 压缩视频（智能跳过小文件） |
| `add_subtitle` | 为视频添加字幕 |
| `video_trim` | 裁剪视频 |
| `concat_video` | 合并多个视频 |
| `extract_audio` | 从视频提取音频 |
| `add_watermark` | 添加水印（图片/文字） |
| `convert_format` | 转换视频格式（mp4/mov/avi/gif/webm） |
| `get_video_info` | 获取视频详细信息 |
