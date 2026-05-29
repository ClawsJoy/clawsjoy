# 临时修复：确保 recall API 支持空查询
# 当前 lib/memory.py 的 recall 方法已经支持，问题在调用方式

# 正确调用方式：
curl -X POST http://localhost:5002/api/v5/memory/recall \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "query": "茶", "n": 10}'

# 而不是传空字符串
