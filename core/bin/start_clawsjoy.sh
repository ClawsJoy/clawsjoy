#!/bin/bash
# ClawsJoy 统一启动脚本（配置驱动）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 可选加载本地环境变量文件（不提交到仓库）
if [ -f "$SCRIPT_DIR/.env" ]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.env"
fi

# 加载统一默认配置（仅在变量未设置时填充）
# shellcheck disable=SC1091
source "$SCRIPT_DIR/settings.sh"
source "$SCRIPT_DIR/logging.sh"

PID_DIR="$CLAWSJOY_LOG_SYSTEM_DIR/pids"
START_LOG="$CLAWSJOY_LOG_SYSTEM_DIR/startup.log"
mkdir -p "$CLAWSJOY_LOG_APP_DIR" "$CLAWSJOY_LOG_SYSTEM_DIR" "$PID_DIR"

start_service() {
    local name="$1"
    local cmd="$2"
    local pid_file="$PID_DIR/${name}.pid"
    local out_file="$CLAWSJOY_LOG_APP_DIR/${name}.log"

    if [ -f "$pid_file" ]; then
        local old_pid
        old_pid="$(cat "$pid_file" 2>/dev/null || true)"
        if [ -n "${old_pid:-}" ] && kill -0 "$old_pid" >/dev/null 2>&1; then
            log_info "$START_LOG" "start_clawsjoy" "$name 已在运行 (pid=$old_pid)"
            return 0
        fi
    fi

    nohup bash -lc "$cmd" >>"$out_file" 2>&1 &
    local new_pid=$!
    echo "$new_pid" > "$pid_file"
    log_info "$START_LOG" "start_clawsjoy" "启动 $name (pid=$new_pid)"
}

log_info "$START_LOG" "start_clawsjoy" "启动 ClawsJoy 服务"
log_info "$START_LOG" "start_clawsjoy" "ROOT=$CLAWSJOY_ROOT"
log_info "$START_LOG" "start_clawsjoy" "LOGS=$CLAWSJOY_LOGS_DIR"

start_service "auth_api" "python3 \"$SCRIPT_DIR/auth_api.py\""
start_service "tenant_api" "python3 \"$SCRIPT_DIR/tenant_api.py\""
start_service "billing_api" "python3 \"$SCRIPT_DIR/billing_api.py\""
start_service "task_api" "python3 \"$SCRIPT_DIR/task_api.py\""
start_service "joymate_api" "python3 \"$SCRIPT_DIR/joymate_api.py\""
start_service "coffee_api" "python3 \"$SCRIPT_DIR/coffee_api.py\""
start_service "promo_api" "python3 \"$SCRIPT_DIR/promo_api.py\""
start_service "task_runner" "bash \"$SCRIPT_DIR/task_runner.sh\""

log_info "$START_LOG" "start_clawsjoy" "启动完成。日志目录: $CLAWSJOY_LOGS_DIR"
