#!/bin/bash
# Engineer 自动协调 Writer 和 Designer

LOG_FILE="$HOME/clawsjoy/logs/orchestrate.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "=========================================="
log "🔧 Engineer 自动协调任务开始"
log "=========================================="

# 1. 发起今日任务请求
log "📋 1. 发起任务请求..."
~/clawsjoy/bin/engineer_request_task.sh daily

# 2. 等待 Writer 和 Designer 响应
log "⏳ 2. 等待 Agent 响应任务..."
sleep 10

# 3. 触发 Writer 执行
log "📝 3. 触发 Writer 执行..."
~/clawsjoy/bin/writer_responder.sh

# 4. 触发 Designer 执行
log "🎨 4. 触发 Designer 执行..."
~/clawsjoy/bin/designer_responder.sh

# 5. 等待提交完成
sleep 5

# 6. 提交 Engineer 自己的部署任务
log "🔧 5. 提交 Engineer 网站部署任务..."
~/clawsjoy/bin/write_deploy "自动部署 - 更新网站内容" "~/clawsjoy/bin/website_maintain.sh && ~/clawsjoy/bin/auto_publish_to_website.sh" "Engineer 自动协调部署"

log "=========================================="
log "✅ Engineer 协调完成"
log "📋 审核看板: http://localhost:8083/review/index.html"
log "=========================================="
