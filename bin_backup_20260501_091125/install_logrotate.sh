#!/bin/bash
# 安装 ClawsJoy logrotate 配置（需要 sudo 权限）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONF_SRC="$PROJECT_ROOT/ops/logrotate/clawsjoy.conf"
CONF_DST="/etc/logrotate.d/clawsjoy"

if [ ! -f "$CONF_SRC" ]; then
    echo "配置文件不存在: $CONF_SRC"
    exit 1
fi

if ! command -v logrotate >/dev/null 2>&1; then
    echo "未检测到 logrotate，请先安装。"
    exit 1
fi

sudo cp "$CONF_SRC" "$CONF_DST"
echo "已安装: $CONF_DST"
echo "可执行测试: sudo logrotate -d $CONF_DST"
