#!/bin/bash
BASE_URL="http://localhost:5002"

echo "=== API 测试 ==="
echo "1. 健康检查:"
curl -s $BASE_URL/health | jq '.'

echo -e "\n2. 根路径:"
curl -s $BASE_URL/ | head -c 200

echo -e "\n3. 查找可用端点:"
grep -r "@app.route" --include="*.py" scripts/ | grep -v "app.route('" | cut -d: -f2 | sort -u
