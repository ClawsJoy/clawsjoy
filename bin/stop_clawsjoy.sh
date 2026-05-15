#!/bin/bash
# ClawsJoy 统一停止脚本（配置驱动）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/settings.sh"
source "$SCRIPT_DIR/logging.sh"

PID_DIR="$CLAWSJOY_LOG_SYSTEM_DIR/pids"
STOP_LOG="$CLAWSJOY_LOG_SYSTEM_DIR/shutdown.log"
mkdir -p "$CLAWSJOY_LOG_SYSTEM_DIR" "$PID_DIR"

stop_service() {
    local name="$1"
    local pid_file="$PID_DIR/${name}.pid"

    if [ ! -f "$pid_file" ]; then
        log_warn "$STOP_LOG" "stop_clawsjoy" "$name 未找到 pid 文件，跳过"
        return 0
    fi

    local pid
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [ -z "${pid:-}" ]; then
        log_warn "$STOP_LOG" "stop_clawsjoy" "$name pid 文件为空，删除并跳过"
        rm -f "$pid_file"
        return 0
    fi

    if ! kill -0 "$pid" >/dev/null 2>&1; then
        log_warn "$STOP_LOG" "stop_clawsjoy" "$name 进程不存在(pid=$pid)，清理 pid 文件"
        rm -f "$pid_file"
        return 0
    fi

    kill "$pid" >/dev/null 2>&1 || true

    local i
    for i in 1 2 3 4 5; do
        if ! kill -0 "$pid" >/dev/null 2>&1; then
            log_info "$STOP_LOG" "stop_clawsjoy" "已停止 $name (pid=$pid)"
            rm -f "$pid_file"
            return 0
        fi
        sleep 1
    done

    log_warn "$STOP_LOG" "stop_clawsjoy" "$name 未在超时内退出，执行强制终止(pid=$pid)"
    kill -9 "$pid" >/dev/null 2>&1 || true
    rm -f "$pid_file"
    log_info "$STOP_LOG" "stop_clawsjoy" "已强制停止 $name (pid=$pid)"
}

log_info "$STOP_LOG" "stop_clawsjoy" "开始停止 ClawsJoy 服务"

# 先停消费侧，再停 API 侧，尽量减少在停机过程中产生新任务。
stop_service "task_runner"
stop_service "promo_api"
stop_service "coffee_api"
stop_service "joymate_api"
stop_service "task_api"
stop_service "billing_api"
stop_service "tenant_api"
stop_service "auth_api"

log_info "$STOP_LOG" "stop_clawsjoy" "停止流程完成"
