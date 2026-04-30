#!/bin/bash
# Writer 自动响应 Engineer 发起的任务请求

REQUEST_DIR="$HOME/clawsjoy/requests"
OUTBOX_DIR="$HOME/clawsjoy/outbox"
PROCESSED_DIR="$REQUEST_DIR/processed"

mkdir -p "$PROCESSED_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

log "📝 Writer 检查待处理任务..."

for request in "$REQUEST_DIR"/writer_request_*.json; do
    if [ -f "$request" ]; then
        log "📋 发现任务请求: $(basename $request)"
        
        # 读取请求内容
        TITLE=$(cat "$request" | python3 -c "import sys,json; print(json.load(sys.stdin).get('title', ''))")
        TOPIC=$(cat "$request" | python3 -c "import sys,json; print(json.load(sys.stdin).get('topic', ''))")
        
        # 生成文章内容
        CONTENT="<h1>$TITLE</h1>
<h2>📖 主题背景</h2>
<p>$TOPIC</p>
<h2>🎯 ClawsJoy 解决方案</h2>
<ul>
<li>🔒 多租户隔离：您的数据绝对安全</li>
<li>🧠 Agent自动进化：越用越聪明</li>
<li>📁 文件事件驱动：AI只创作，系统执行</li>
<li>👁️ 可视听化审核：一目了然</li>
</ul>
<h2>💡 总结</h2>
<p>ClawsJoy — 让AI安全地为每个人工作，工具易上手，结果令人愉悦。</p>
<hr>
<p style='text-align:center;color:#667eea;'>由 Engineer 触发，Writer 自动生成于 $(date '+%Y-%m-%d %H:%M:%S')</p>"
        
        # 提交到审核看板
        ~/clawsjoy/bin/write_review "$TITLE" "$CONTENT" "writer_auto"
        
        # 移动已处理的请求
        mv "$request" "$PROCESSED_DIR/"
        log "✅ 已响应任务并提交审核: $TITLE"
    fi
done

log "✅ Writer 任务响应完成"
