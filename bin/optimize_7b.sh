#!/bin/bash
# 6GB 显存优化配置（适配 WSL + Windows Ollama）

echo "🔧 开始优化配置..."

# 1. 设置 OpenClaw 使用 qwen2.5:7b
echo "📝 设置模型..."
openclaw config set agents.defaults.model ollama/qwen2.5:7b

# 2. 设置上下文长度（节省显存）
echo "📝 设置上下文长度..."
openclaw config set agents.defaults.num_ctx 4096

# 3. 设置最大生成 token 数
openclaw config set agents.defaults.num_predict 1024

# 4. 重启网关
echo "🔄 重启网关..."
openclaw gateway restart

# 5. 等待网关启动
sleep 5

# 6. 测试模型连通性
echo "🧪 测试模型连通性..."
curl -s -X POST http://172.21.80.1:11434/api/generate \
  -d '{"model":"qwen2.5:7b","prompt":"测试","stream":false}' \
  -H "Content-Type: application/json" | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅ 模型正常，响应:', d.get('response', '')[:50])" 2>/dev/null || echo "⚠️ 模型测试失败，请检查 Ollama"

echo ""
echo "✅ 优化完成"
echo "📊 配置: qwen2.5:7b, 上下文 4096, 最大生成 1024"
echo "💡 显存占用约 4.5-5.5GB"
