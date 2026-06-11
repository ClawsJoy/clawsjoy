#!/bin/bash
# ClawsJoy v5 快速测试

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZDE2YjIwYjJjZWRjZjNjZiIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJyb2xlIjoidXNlciIsImV4cCI6MTc4MTE4MzMyMn0.2cbQMYnwasdm1cxjxtUuhJyODjaF4GyXoHdma-TZnzQ"

echo "🧪 测试 ClawsJoy v5"
echo "==================="

echo ""
echo "1. 基础对话:"
curl -s -X POST http://localhost:5002/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"你好","user_id":"test"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('  响应:', d.get('response', '')[:100])"

echo ""
echo "2. 数学计算:"
curl -s -X POST http://localhost:5002/api/v5/enhanced/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"123+456","user_id":"test"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('  结果:', d.get('response', ''))"

echo ""
echo "✅ 测试完成"
