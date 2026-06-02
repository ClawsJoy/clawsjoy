#!/bin/bash
echo "=== ClawsJoy v5 诊断报告 ==="
echo "时间: $(date)"
echo ""

echo "1. 服务状态:"
if curl -s http://localhost:5002/health > /dev/null; then
    echo "   ✅ 服务运行中"
    curl -s http://localhost:5002/health
else
    echo "   ❌ 服务未响应"
fi

echo -e "\n2. 进程信息:"
pgrep -f gunicorn > /dev/null && echo "   ✅ Gunicorn 运行中" || echo "   ❌ Gunicorn 未运行"

echo -e "\n3. 端口监听:"
netstat -tlnp 2>/dev/null | grep 5002 > /dev/null && echo "   ✅ 端口 5002 监听中" || echo "   ❌ 端口 5002 未监听"

echo -e "\n4. 磁盘使用:"
df -h /home/flybo/clawsjoy_v5 | tail -1

echo -e "\n5. Git 状态:"
git status --short | wc -l | xargs echo "   未提交文件数:"

echo -e "\n6. 环境检查:"
echo "   Python: $(python3 --version)"
echo "   WSL: $(uname -r)"

echo -e "\n7. 安全警告:"
if grep -r "GOCSPX" . --include="*.py" 2>/dev/null; then
    echo "   ⚠️  发现硬编码 Google 密钥"
fi
if grep -r "clawsjoy-production-secret-key" . --include="*.py" 2>/dev/null; then
    echo "   ⚠️  发现硬编码 JWT 密钥"
fi

echo -e "\n=== 诊断完成 ==="
