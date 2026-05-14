#!/bin/bash
# ClawsJoy shell 日志工具

clawsjoy_log() {
    local logfile="$1"
    local service="$2"
    local level="$3"
    shift 3
    local message="$*"
    local ts
    ts="$(date '+%Y-%m-%dT%H:%M:%S%z')"
    printf '[%s] [%s] [%s] %s\n' "$ts" "$service" "$level" "$message" >> "$logfile"
}

log_info() {
    clawsjoy_log "$1" "$2" "INFO" "${@:3}"
}

log_warn() {
    clawsjoy_log "$1" "$2" "WARN" "${@:3}"
}

log_error() {
    clawsjoy_log "$1" "$2" "ERROR" "${@:3}"
}
