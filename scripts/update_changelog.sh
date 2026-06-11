#!/bin/bash
# 自动更新 CHANGELOG

cd "$(dirname "$0")/.."

# 获取最新 commit
LATEST_COMMIT=$(git log -1 --pretty=%s)
LATEST_DATE=$(date +%Y-%m-%d)

# 检查是否需要更新
if grep -q "## \[$(date +%Y.%m.%d)" CHANGELOG.md 2>/dev/null; then
    echo "今天已更新过"
    exit 0
fi

# 在文件开头添加新条目
sed -i "3i\\
## [$(date +%Y.%m.%d)] - $LATEST_DATE\\
\\
### 更新\\
- $LATEST_COMMIT\\
" CHANGELOG.md

echo "✅ CHANGELOG 已更新"
