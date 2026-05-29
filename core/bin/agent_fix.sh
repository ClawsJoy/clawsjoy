#!/bin/bash
# Agent 自动修复脚本 - 会记住学到的修复方法

FIX_LOG="/mnt/d/clawsjoy/logs/agent_fixes.log"
MEMORY_FILE="/mnt/d/clawsjoy/data/agent_memory.json"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$FIX_LOG"
    echo "$1"
}

# 检查并修复 agent-api
if ! pm2 list | grep -q "agent-api.*online"; then
    log "🔧 agent-api 异常，执行修复..."
    pm2 delete agent-api 2>/dev/null
    cd /mnt/d/clawsjoy/bin
    pm2 start agent_api.py --interpreter python3 --name agent-api -- --port 18103
    pm2 save
    log "✅ agent-api 已修复"
fi

# 检查并修复 web (Docker 容器)
if ! docker ps | grep -q clawsjoy-web; then
    log "🔧 web 容器异常，执行修复..."
    docker restart clawsjoy-web 2>/dev/null || docker-compose -f /mnt/d/clawsjoy/docker-compose.yml up -d web
    log "✅ web 已修复"
fi

# 检查并修复 promo-api
if ! pm2 list | grep -q "promo-api.*online"; then
    log "🔧 promo-api 异常，执行修复..."
    cd /mnt/d/clawsjoy/bin
    pm2 restart promo-api 2>/dev/null || pm2 start promo_api.py --name promo-api -- --port 8108
    pm2 save
    log "✅ promo-api 已修复"
fi

log "========== 本轮修复完成 =========="
