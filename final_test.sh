#!/bin/bash
echo "=========================================="
echo "ClawsJoy v5 完整功能测试"
echo "=========================================="

BASE="http://127.0.0.1:5002"
PASS=0
FAIL=0

test_api() {
    local name=$1
    local cmd=$2
    echo -n "测试: $name ... "
    if eval "$cmd" 2>/dev/null | grep -q '"success": true\|"status": "healthy"'; then
        echo "✅ 通过"
        ((PASS++))
    else
        echo "❌ 失败"
        ((FAIL++))
    fi
}

# 1. 基础服务
test_api "健康检查" "curl -s $BASE/health"

# 2. 聊天功能
test_api "聊天功能" "curl -s -X POST $BASE/api/v5/enhanced/chat -H 'Content-Type: application/json' -d '{\"user_id\":\"t1\",\"message\":\"你好\"}'"

# 3. 计算功能
test_api "计算功能" "curl -s -X POST $BASE/api/v5/enhanced/chat -H 'Content-Type: application/json' -d '{\"user_id\":\"t1\",\"message\":\"1+2\"}'"

# 4. 缓存功能
echo -n "测试: 缓存功能 ... "
curl -s -X POST $BASE/api/v5/enhanced/chat -H 'Content-Type: application/json' -d '{"user_id":"c1","message":"测试"}' > /dev/null
if curl -s -X POST $BASE/api/v5/enhanced/chat -H 'Content-Type: application/json' -d '{"user_id":"c1","message":"测试"}' | grep -q '"cached": true'; then
    echo "✅ 通过"
    ((PASS++))
else
    echo "❌ 失败"
    ((FAIL++))
fi

# 5. 记忆功能
test_api "记忆存储" "curl -s -X POST $BASE/api/v5/memory/remember -H 'Content-Type: application/json' -d '{\"user_id\":\"m1\",\"fact\":\"测试记忆\"}'"
test_api "记忆检索" "curl -s -X POST $BASE/api/v5/memory/recall -H 'Content-Type: application/json' -d '{\"user_id\":\"m1\"}'"

echo "=========================================="
echo "测试结果: 通过 $PASS, 失败 $FAIL"
echo "=========================================="
