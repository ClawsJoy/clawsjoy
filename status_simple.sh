#!/bin/bash
echo "=== ClawsJoy 状态 ==="
for port in 5002 5003 5005 5008; do
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo "✅ :$port"
    else
        echo "❌ :$port"
    fi
done
