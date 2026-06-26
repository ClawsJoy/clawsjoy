---
name: tts_dubbing
version: 1.0.0
description: '漫剧分镜对白自动配音，使用EdgeTTS免费语音合成'
author: ClawsJoy
security_grade: 🟢 A
use_when: 配音, 对白配音, 语音合成, TTS
not_for: 音乐生成, 音效
---

# tts_dubbing

## When to Run
- 用户需要对漫剧分镜对白进行配音
- 批量生成角色语音文件

## Workflow
1. 加载分镜对白列表
2. 根据角色匹配语音（林浩→云希男声，无名→晓晓女声）
3. EdgeTTS合成MP3
4. 保存到 data/voice_output/

## Voices
- 林浩: zh-CN-YunxiNeural (沉稳男声)
- 无名: zh-CN-XiaoxiaoNeural (温柔女声)
- 艾丽卡: zh-CN-XiaoyiNeural (活泼女声)

## Changelog
### v1.0.0 (2026-06-26)
- 初始版本，支持3角色
