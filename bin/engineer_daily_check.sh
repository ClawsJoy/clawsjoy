#!/bin/bash
# Engineer 每日巡检脚本

LOG_FILE="$HOME/clawsjoy/logs/engineer_daily.log"
API_URL="http://localhost:5005/api/admin"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "🔍 Engineer 每日巡检开始"

# 1. 检查服务状态
log "1. 检查服务状态..."
services=("review_api.py" "http.server 8083" "universal_router.sh")
for svc in "${services[@]}"; do
    if pgrep -f "$svc" > /dev/null; then
        log "   ✅ $svc 运行中"
    else
        log "   ❌ $svc 未运行，正在重启..."
        if [[ "$svc" == "review_api.py" ]]; then
            cd /home/flybo/joymate_api && nohup python3 review_api.py > /tmp/review_api.log 2>&1 &
        elif [[ "$svc" == "http.server 8083" ]]; then
            cd /home/flybo/.openclaw/web && nohup python3 -m http.server 8083 > /tmp/web_server.log 2>&1 &
        elif [[ "$svc" == "universal_router.sh" ]]; then
            nohup ~/clawsjoy/bin/universal_router.sh > /dev/null 2>&1 &
        fi
        log "   ✅ $svc 已重启"
    fi
done

# 2. 检查磁盘空间
log "2. 检查磁盘空间..."
DISK_USAGE=$(df -h /home | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    log "   ⚠️ 磁盘使用率: ${DISK_USAGE}%，需要清理"
    # 清理旧日志
    find ~/clawsjoy/logs -name "*.log" -mtime +30 -delete
    log "   ✅ 已清理30天前的日志"
else
    log "   ✅ 磁盘使用率: ${DISK_USAGE}%"
fi

# 3. 检查待审核队列
log "3. 检查待审核队列..."
PENDING=$(curl -s "$API_URL/tasks" | python3 -c "import sys,json; print(len([t for t in json.load(sys.stdin) if t.get('status')=='pending']))")
if [ "$PENDING" -gt 10 ]; then
    log "   ⚠️ 待审核任务较多: $PENDING 个"
else
    log "   ✅ 待审核任务: $PENDING 个"
fi

# 4. 运行网站维护
log "4. 运行网站维护..."
~/clawsjoy/bin/website_maintain.sh >> "$LOG_FILE" 2>&1

# 5. 发布新内容
log "5. 发布新内容到网站..."
~/clawsjoy/bin/auto_publish_to_website.sh >> "$LOG_FILE" 2>&1

log "✅ Engineer 每日巡检完成"
