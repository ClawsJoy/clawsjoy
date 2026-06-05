#!/bin/bash
echo "=== ClawsJoy v5 最终验证 ==="

# 1. 环境变量
echo -e "\n1. .env 文件:"
cat .env | grep -v "^#" | grep -v "^$"

# 2. 服务状态
echo -e "\n2. 服务状态:"
curl -s http://127.0.0.1:5002/health | python3 -m json.tool

# 3. 进程信息
echo -e "\n3. 进程信息:"
ps aux | grep gunicorn | grep -v grep | awk '{print "PID:",$2,"CPU:",$3"%","MEM:",$4"%"}'

# 4. 端口监听
echo -e "\n4. 端口监听:"
netstat -tlnp 2>/dev/null | grep 5002 | head -1

# 5. 功能测试
echo -e "\n5. 功能测试:"
curl -s -X POST http://127.0.0.1:5002/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "final", "message": "测试"}' | python3 -m json.tool | head -5

echo -e "\n✅ 验证完成"
