#!/bin/bash
# ClawsJoy 审计日志

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/settings.sh"

AUDIT_LOG="$CLAWSJOY_LOG_AUDIT_DIR/audit.log"
mkdir -p "$(dirname "$AUDIT_LOG")"

log_audit() {
    local tenant_id=$1
    local action=$2
    local detail=$3
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"tenant\":\"$tenant_id\",\"action\":\"$action\",\"detail\":\"$detail\"}" >> "$AUDIT_LOG"
}

# 使用示例
# log_audit "tenant_1" "task_submit" "promo"
