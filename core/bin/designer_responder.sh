#!/bin/bash
# Designer 自动响应 Engineer 发起的任务请求

REQUEST_DIR="$HOME/clawsjoy/requests"
OUTBOX_DIR="$HOME/clawsjoy/outbox"
PROCESSED_DIR="$REQUEST_DIR/processed"

mkdir -p "$PROCESSED_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

log "🎨 Designer 检查待处理任务..."

for request in "$REQUEST_DIR"/designer_request_*.json; do
    if [ -f "$request" ]; then
        log "📋 发现任务请求: $(basename $request)"
        
        TITLE=$(cat "$request" | python3 -c "import sys,json; print(json.load(sys.stdin).get('title', ''))")
        
        # 生成 SVG 设计
        SVG_CONTENT='<svg width="1280" height="720" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1a1a2e"/>
      <stop offset="100%" stop-color="#16213e"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#667eea"/>
      <stop offset="100%" stop-color="#764ba2"/>
    </linearGradient>
  </defs>
  <rect width="1280" height="720" fill="url(#bgGrad)"/>
  <g transform="translate(640, 300)">
    <circle cx="0" cy="0" r="60" fill="url(#accentGrad)"/>
    <text x="0" y="15" text-anchor="middle" fill="white" font-size="50" font-weight="bold">CJ</text>
  </g>
  <text x="640" y="420" text-anchor="middle" fill="white" font-size="42" font-weight="bold">ClawsJoy</text>
  <text x="640" y="470" text-anchor="middle" fill="#c3d0fe" font-size="22">让AI安全地为每个人工作</text>
  <text x="640" y="680" text-anchor="middle" fill="#888" font-size="14">工具易上手，结果令人愉悦</text>
</svg>'
        
        # 提交到审核看板
        ~/clawsjoy/bin/write_design "$TITLE" "$SVG_CONTENT" "designer_auto"
        
        # 移动已处理的请求
        mv "$request" "$PROCESSED_DIR/"
        log "✅ 已响应任务并提交审核: $TITLE"
    fi
done

log "✅ Designer 任务响应完成"
