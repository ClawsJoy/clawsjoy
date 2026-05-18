#!/bin/bash
cd /mnt/d/clawsjoy

# 使用 5010-5013 端口
export GATEWAY_PORT=5010
export FILE_PORT=5011
export AGENT_PORT=5012
export DOC_PORT=5013

echo "使用新端口: 5010, 5011, 5012, 5013"

# 创建临时配置文件
cat > ports_config.py << EOF
GATEWAY_PORT = $GATEWAY_PORT
FILE_PORT = $FILE_PORT
AGENT_PORT = $AGENT_PORT
DOC_PORT = $DOC_PORT
