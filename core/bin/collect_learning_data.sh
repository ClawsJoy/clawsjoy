#!/bin/bash
# 采集系统运营过程中的学习素材

LEARNING_DIR="/mnt/d/clawsjoy/data/learning"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$LEARNING_DIR"

# 1. 采集服务状态
pm2 list > "$LEARNING_DIR/services_$TIMESTAMP.txt" 2>/dev/null

# 2. 采集最近对话（关键词学习素材）
if [ -f "logs/chat-api-out.log" ]; then
    tail -100 logs/chat-api-out.log | grep "📥 处理" > "$LEARNING_DIR/dialogs_$TIMESTAMP.txt"
else
    echo "暂无对话日志" > "$LEARNING_DIR/dialogs_$TIMESTAMP.txt"
fi

# 3. 采集错误模式
if [ -f "logs/engineer.log" ]; then
    tail -200 logs/engineer.log | grep "ERROR\|失败" > "$LEARNING_DIR/errors_$TIMESTAMP.txt"
else
    echo "暂无错误日志" > "$LEARNING_DIR/errors_$TIMESTAMP.txt"
fi

# 4. 采集 URL 发现
if [ -f "logs/spider_learn.log" ]; then
    tail -50 logs/spider_learn.log > "$LEARNING_DIR/urls_$TIMESTAMP.txt"
else
    echo "暂无爬虫日志" > "$LEARNING_DIR/urls_$TIMESTAMP.txt"
fi

# 5. 采集视频生成结果
ls -lt web/videos/*.mp4 2>/dev/null | head -5 > "$LEARNING_DIR/videos_$TIMESTAMP.txt"

echo "📊 学习数据已采集: $TIMESTAMP"
