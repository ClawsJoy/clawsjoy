#!/bin/bash
# ClawsJoy 开发环境启动脚本 - 支持热重载

cd /home/flybo/clawsjoy_clean

# 设置环境变量
export PYTHONPATH=/home/flybo/clawsjoy_clean
export FLASK_ENV=development
export FLASK_DEBUG=1

echo "🚀 启动 ClawsJoy 开发环境 (热重载模式)"
echo "================================================"

# 启动旧版增强服务 (带热重载)
echo "📡 启动旧版增强服务 - 端口 5002 (热重载)..."
gunicorn -w 2 -k gevent \
    --bind 0.0.0.0:5002 \
    --reload \
    --reload-extra-file core/agents/ \
    --reload-extra-file lib/ \
    --reload-extra-file config/ \
    --timeout 120 \
    --access-logfile logs/dev_access.log \
    --error-logfile logs/dev_error.log \
    agent_gateway_enhanced:app \
    --daemon

sleep 3

# 启动 v5.0 服务 (带热重载)
echo "🧪 启动 v5.0 测试服务 - 端口 5003 (热重载)..."
gunicorn -w 2 -k gevent \
    --bind 0.0.0.0:5003 \
    --reload \
    --reload-extra-file core/v5/ \
    --timeout 120 \
    agent_gateway_v5_complete_fixed:app \
    --daemon

sleep 3

echo ""
echo "✅ 服务已启动 (热重载已启用)"
echo ""
echo "📊 服务状态:"
echo "   旧版: http://localhost:5002 (代码修改自动重载)"
echo "   v5.0: http://localhost:5003 (代码修改自动重载)"
echo ""
echo "📋 监控目录:"
echo "   - core/agents/"
echo "   - core/v5/"
echo "   - lib/"
echo "   - config/"
echo ""
echo "🛑 停止服务: ./stop_dev.sh"
echo "📋 查看日志: tail -f logs/dev_error.log"
