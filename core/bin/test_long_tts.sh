#!/bin/bash
TEXT="香港优才计划2026年迎来重大调整。分数门槛从80分降至75分。新增金融科技、人工智能、数据科学人才清单。审批时间从6个月缩短至3个月。2025年共有3421人获批，成功率约38%。建议尽早准备申请材料。准备学历证明、工作证明、语言成绩。注意文书质量，突出个人优势。"

# 重复5次
LONG_TEXT=""
for i in {1..5}; do
    LONG_TEXT="$LONG_TEXT $TEXT"
done

echo "文本长度: ${#LONG_TEXT}"
edge-tts --text "$LONG_TEXT" --write-media /tmp/long_test.mp3 --voice zh-CN-XiaoxiaoNeural
ls -la /tmp/long_test.mp3
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /tmp/long_test.mp3
