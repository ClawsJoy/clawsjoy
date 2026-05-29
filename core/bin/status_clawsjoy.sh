#!/bin/bash
# ClawsJoy 服务状态脚本（配置驱动）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/settings.sh"
source "$SCRIPT_DIR/logging.sh"

PID_DIR="$CLAWSJOY_LOG_SYSTEM_DIR/pids"
STATUS_LOG="$CLAWSJOY_LOG_SYSTEM_DIR/status.log"
mkdir -p "$CLAWSJOY_LOG_SYSTEM_DIR" "$PID_DIR"

SERVICES=(
  "auth_api"
  "tenant_api"
  "billing_api"
  "task_api"
  "joymate_api"
  "coffee_api"
  "promo_api"
  "task_runner"
)

running_count=0
stale_count=0
missing_count=0
port_down_count=0

service_port() {
    case "$1" in
        "auth_api") echo "$CLAWSJOY_PORT_AUTH" ;;
        "tenant_api") echo "$CLAWSJOY_PORT_TENANT" ;;
        "billing_api") echo "$CLAWSJOY_PORT_BILLING" ;;
        "task_api") echo "$CLAWSJOY_PORT_TASK" ;;
        "joymate_api") echo "$CLAWSJOY_PORT_JOYMATE" ;;
        "coffee_api") echo "$CLAWSJOY_PORT_COFFEE" ;;
        "promo_api") echo "$CLAWSJOY_PORT_PROMO" ;;
        *) echo "" ;;
    esac
}

is_port_open() {
    local port="$1"
    python -c "import socket,sys; s=socket.socket(); s.settimeout(0.5); rc=s.connect_ex(('127.0.0.1', int(sys.argv[1]))); s.close(); sys.exit(0 if rc==0 else 1)" "$port"
}

check_service() {
    local name="$1"
    local pid_file="$PID_DIR/${name}.pid"

    if [ ! -f "$pid_file" ]; then
        echo "MISSING  $name (no pid file)"
        missing_count=$((missing_count + 1))
        return 0
    fi

    local pid
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [ -z "${pid:-}" ]; then
        echo "STALE    $name (empty pid file)"
        stale_count=$((stale_count + 1))
        return 0
    fi

    if kill -0 "$pid" >/dev/null 2>&1; then
        local port
        port="$(service_port "$name")"
        if [ -n "$port" ]; then
            if is_port_open "$port"; then
                echo "RUNNING  $name (pid=$pid, port=$port open)"
            else
                echo "RUNNING  $name (pid=$pid, port=$port closed)"
                port_down_count=$((port_down_count + 1))
            fi
        else
            echo "RUNNING  $name (pid=$pid)"
        fi
        running_count=$((running_count + 1))
    else
        echo "STALE    $name (pid=$pid not alive)"
        stale_count=$((stale_count + 1))
    fi
}

echo "ClawsJoy status"
echo "ROOT=$CLAWSJOY_ROOT"
echo "LOGS=$CLAWSJOY_LOGS_DIR"
echo "---"

for svc in "${SERVICES[@]}"; do
    check_service "$svc"
done

echo "---"
echo "summary: running=$running_count stale=$stale_count missing=$missing_count port_down=$port_down_count total=${#SERVICES[@]}"
log_info "$STATUS_LOG" "status_clawsjoy" "running=$running_count stale=$stale_count missing=$missing_count port_down=$port_down_count total=${#SERVICES[@]}"
