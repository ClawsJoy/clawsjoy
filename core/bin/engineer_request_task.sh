#!/bin/bash
# Engineer 发起任务请求 - 向 Writer/Designer 索要素材

REQUEST_DIR="$HOME/clawsjoy/requests"
mkdir -p "$REQUEST_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

case "$1" in
    writer)
        # 向 Writer 索要品牌文章
        TITLE="$2"
        TOPIC="$3"
        DEADLINE="${4:-今日}"
        
        cat > "$REQUEST_DIR/writer_request_$(date +%Y%m%d_%H%M%S).json" << EOF
{
  "type": "request",
  "from": "engineer",
  "to": "writer",
  "task": "write_article",
  "title": "$TITLE",
  "topic": "$TOPIC",
  "deadline": "$DEADLINE",
  "requirements": {
    "format": "HTML",
    "min_words": 300,
    "style": "专业+科技感",
    "keywords": ["ClawsJoy", "AI", "安全", "隔离"]
  },
  "created_at": "$(date -Iseconds)"
}
EOF
        log "✅ 已向 Writer 发起任务请求: $TITLE"
        ;;
    
    designer)
        # 向 Designer 索要设计稿
        TITLE="$2"
        TYPE="$3"
        DEADLINE="${4:-今日}"
        
        cat > "$REQUEST_DIR/designer_request_$(date +%Y%m%d_%H%M%S).json" << EOF
{
  "type": "request",
  "from": "engineer",
  "to": "designer",
  "task": "create_design",
  "title": "$TITLE",
  "design_type": "$TYPE",
  "deadline": "$DEADLINE",
  "requirements": {
    "format": "SVG",
    "colors": ["#667eea", "#764ba2", "#f59e0b"],
    "style": "科技感+简洁",
    "size": "1280x720"
  },
  "created_at": "$(date -Iseconds)"
}
EOF
        log "✅ 已向 Designer 发起任务请求: $TITLE"
        ;;
    
    daily)
        # 每日常规任务请求
        log "📋 Engineer 发起每日任务请求..."
        
        # 请求 Writer 写今日品牌文章
        ~/clawsjoy/bin/engineer_request_task.sh writer "ClawsJoy 今日品牌动态" "$(date +%Y年%m月%d日) 品牌最新动态" "今日"
        
        # 请求 Designer 设计今日宣传图
        ~/clawsjoy/bin/engineer_request_task.sh designer "ClawsJoy 今日宣传图" "social_media" "今日"
        
        log "✅ 每日任务请求已发送"
        ;;
    
    status)
        # 查看任务请求状态
        echo "=== 待处理的任务请求 ==="
        for f in "$REQUEST_DIR"/*.json; do
            if [ -f "$f" ]; then
                echo "📋 $(basename $f)"
                cat "$f" | python3 -m json.tool | head -15
                echo "---"
            fi
        done
        ;;
    
    *)
        echo "用法: engineer_request_task.sh {writer|designer|daily|status} [参数]"
        echo ""
        echo "示例:"
        echo "  engineer_request_task.sh writer '品牌文章标题' '文章主题' '今日'"
        echo "  engineer_request_task.sh designer '宣传图标题' 'social_media' '今日'"
        echo "  engineer_request_task.sh daily"
        echo "  engineer_request_task.sh status"
        ;;
esac
