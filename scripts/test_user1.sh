#!/bin/bash

echo "=========================================="
echo "用户1 完整功能测试"
echo "=========================================="

# 1. 登录
echo "1. 登录:"
TOKEN=$(curl -k -s -X POST https://localhost:5444/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "password": "admin123"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ 登录失败"
    exit 1
fi
echo "✅ 登录成功"

# 2. 验证 Token
echo ""
echo "2. 验证 Token:"
curl -k -s -X GET https://localhost:5444/auth/verify \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 3. 保存偏好
echo ""
echo "3. 保存偏好:"
curl -k -s -X POST https://localhost:5445/preference/save \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category": "image", "preferences": {"style": "写实", "age": "中年", "expression": "坚毅"}}' | python3 -m json.tool

# 4. 加载偏好
echo ""
echo "4. 加载偏好:"
curl -k -s "https://localhost:5445/preference/load?category=image" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 5. 访问安全 API
echo ""
echo "5. 安全 API 测试:"
curl -k -s https://localhost:5446/api/secure/status \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
