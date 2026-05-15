#!/bin/bash
echo "🔧 ClawsJoy 一键修复脚本"
echo "========================="

# 1. 启动数据看板 API
echo "1. 启动数据看板..."
cd /home/flybo/joymate_api
pkill -f stats_api.py 2>/dev/null
nohup python3 stats_api.py > /tmp/stats_api.log 2>&1 &
echo "   ✅ 数据看板 API 已启动 (端口 5006)"

# 2. 启动每周宣传片定时任务（如果未配置）
if ! crontab -l 2>/dev/null | grep -q "weekly_promo.sh"; then
    echo "2. 配置每周宣传片..."
    (crontab -l 2>/dev/null; echo "0 9 * * 1 /home/flybo/clawsjoy/bin/weekly_promo.sh >> /home/flybo/clawsjoy/logs/weekly_promo.log 2>&1") | crontab -
    echo "   ✅ 每周宣传片已配置（每周一 9:00）"
else
    echo "2. 每周宣传片已配置 ✅"
fi

# 3. 修复视频预览
echo "3. 修复视频预览..."
# 重启 Web 服务
pkill -f "http.server 8083"
cd ~/.openclaw/web
nohup python3 -m http.server 8083 > /tmp/web_server.log 2>&1 &
echo "   ✅ Web 服务已重启"

# 4. 查看状态
echo ""
echo "========================="
echo "✅ 修复完成！"
echo ""
echo "访问地址:"
echo "  📋 审核看板: http://localhost:8083/review/index.html"
echo "  📊 数据看板: http://localhost:8083/dashboard/index.html"
echo "  🔧 部署预览: http://localhost:8083/preview/deploy.html"
echo ""
echo "定时任务:"
crontab -l | grep -E "weekly|cleanup" | head -3
