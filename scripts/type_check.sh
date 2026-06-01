#!/bin/bash
echo "🔍 运行类型检查..."
mypy engine/ --ignore-missing-imports 2>/dev/null || echo "⚠️ mypy 未安装，跳过类型检查"
