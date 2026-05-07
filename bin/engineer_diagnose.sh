#!/bin/bash
# 工程师 Agent 自动诊断

echo "🔧 工程师 Agent 诊断报告"
echo "========================="

# 检查服务
for svc in agent-api chat-api promo-api; do
    if pm2 list | grep -q "$svc.*online"; then
        echo "✅ $svc: 正常"
    else
        echo "❌ $svc: 异常"
        # 根据学到的知识给出建议
        echo "   📚 建议: 检查日志 'pm2 logs $svc --lines 20'"
    fi
done

# 检查端口
echo ""
echo "📡 端口状态:"
for port in 18103 18109 8108 18083; do
    if ss -tlnp | grep -q ":$port"; then
        echo "  ✅ 端口 $port: 监听中"
    else
        echo "  ❌ 端口 $port: 未监听"
    fi
done

# 检查 Docker
echo ""
if docker ps 2>/dev/null | grep -q clawsjoy-web; then
    echo "✅ Docker: 运行中"
else
    echo "❌ Docker: 未运行 (建议: sudo service docker start)"
fi

echo ""
echo "📚 工程师知识库已加载，可诊断常见问题"
