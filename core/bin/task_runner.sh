#!/bin/bash
# ClawsJoy 任务执行器（持久化版）

set -uo pipefail

# 加载统一配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/settings.sh"
source "$SCRIPT_DIR/logging.sh"

QUEUE_DIR="$CLAWSJOY_TASK_QUEUE_DIR"
DONE_DIR="$CLAWSJOY_TENANTS_DIR/done"
PROCESSING_DIR="$CLAWSJOY_TENANTS_DIR/processing"
FAILED_DIR="$CLAWSJOY_TENANTS_DIR/failed"
LOG_FILE="$CLAWSJOY_LOG_RUNNER_DIR/task_runner.log"
AUDIT_LOG_FILE="$CLAWSJOY_LOG_AUDIT_DIR/audit.log"
SERVICE_NAME="task_runner"

log() {
    log_info "$LOG_FILE" "$SERVICE_NAME" "$*"
}

log_warn_msg() {
    log_warn "$LOG_FILE" "$SERVICE_NAME" "$*"
}

log_error_msg() {
    log_error "$LOG_FILE" "$SERVICE_NAME" "$*"
}

requeue_processing_tasks() {
    local f filename target
    shopt -s nullglob
    for f in "$PROCESSING_DIR"/*.json; do
        filename="$(basename "$f")"
        target="$QUEUE_DIR/$filename"
        if mv "$f" "$target"; then
            log "退出回滚: $filename -> queue"
        else
            log_error_msg "退出回滚失败: $f"
        fi
    done
    shopt -u nullglob
}

on_shutdown() {
    local signal_name="$1"
    log_warn_msg "收到 $signal_name，开始回滚 processing 任务"
    requeue_processing_tasks
    log "清理完成，任务执行器退出"
    exit 0
}

ensure_runtime() {
    mkdir -p "$QUEUE_DIR" "$DONE_DIR" "$PROCESSING_DIR" "$FAILED_DIR" "$(dirname "$LOG_FILE")" "$(dirname "$AUDIT_LOG_FILE")"

    if ! command -v jq >/dev/null 2>&1; then
        log_error_msg "启动失败: 缺少依赖 jq"
        exit 1
    fi
}

log_audit() {
    local tenant="$1"
    local action="$2"
    local detail="$3"
    mkdir -p "$(dirname "$AUDIT_LOG_FILE")"
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"tenant\":\"$tenant\",\"action\":\"$action\",\"detail\":\"$detail\"}" >> "$AUDIT_LOG_FILE"
}

mark_failed() {
    local processing_file="$1"
    local filename="$2"
    local reason="$3"
    local failed_target="$FAILED_DIR/$filename"

    log_error_msg "任务失败: $filename | $reason"
    if mv "$processing_file" "$failed_target"; then
        log_warn_msg "已移动到失败目录: $failed_target"
    else
        log_error_msg "移动失败文件失败: $processing_file -> $failed_target"
    fi
}

execute_task() {
    local task_file="$1"
    local task_type="$2"

    case "$task_type" in
        "promo")
            "$CLAWSJOY_ROOT/bin/make_video" "宣传片" "/root/.openclaw/web/images/" "/tmp/promo.mp4" "宣传片" 2>&1 | tee -a "$LOG_FILE"
            return "${PIPESTATUS[0]}"
            ;;
        "spider")
            local keyword
            keyword="$(jq -r '.params.keyword // empty' "$task_file" 2>/dev/null)"
            if [ -z "$keyword" ]; then
                log_warn_msg "spider 任务缺少 params.keyword"
                return 2
            fi
            "$CLAWSJOY_ROOT/bin/spider_unsplash" "$keyword" 3 2>&1 | tee -a "$LOG_FILE"
            return "${PIPESTATUS[0]}"
            ;;
        code_generation|code_review|debug)
            local prompt
            prompt="$(jq -r '.prompt // empty' "$task_file" 2>/dev/null)"
            if [ -z "$prompt" ]; then
                log_warn_msg "$task_type 任务缺少 prompt"
                return 2
            fi

            if command -v claude >/dev/null 2>&1; then
                claude -p "$prompt" 2>&1 | tee -a "$LOG_FILE"
                return "${PIPESTATUS[0]}"
            fi

            openclaw infer model run --model ollama/qwen2.5:3b --prompt "$prompt" 2>&1 | tee -a "$LOG_FILE"
            return "${PIPESTATUS[0]}"
            ;;
        *)
            log_warn_msg "未知任务类型: $task_type"
            return 3
            ;;
    esac
}

process_task_file() {
    local queue_file="$1"
    local filename processing_file tenant_id task_type rc

    filename="$(basename "$queue_file")"
    processing_file="$PROCESSING_DIR/$filename"

    if ! mv "$queue_file" "$processing_file"; then
        log_error_msg "无法移动任务到 processing: $queue_file"
        return 1
    fi

    log "开始处理任务: $filename"

    tenant_id="$(jq -r '.tenant_id // "unknown"' "$processing_file" 2>/dev/null)"
    task_type="$(jq -r '.task_type // empty' "$processing_file" 2>/dev/null)"

    if [ -z "$task_type" ]; then
        mark_failed "$processing_file" "$filename" "缺少 task_type 或 JSON 非法"
        log_audit "$tenant_id" "task_failed" "invalid_task_type"
        return 1
    fi

    log_audit "$tenant_id" "task_start" "$task_type"
    execute_task "$processing_file" "$task_type"
    rc=$?

    if [ "$rc" -ne 0 ]; then
        mark_failed "$processing_file" "$filename" "执行返回码=$rc"
        log_audit "$tenant_id" "task_failed" "$task_type:rc=$rc"
        return "$rc"
    fi

    if mv "$processing_file" "$DONE_DIR/$filename"; then
        log "完成: $filename"
        log_audit "$tenant_id" "task_end" "$task_type"
        return 0
    fi

    mark_failed "$processing_file" "$filename" "完成后移动到 done 失败"
    log_audit "$tenant_id" "task_failed" "$task_type:move_done_failed"
    return 1
}

main_loop() {
    log "任务执行器启动（持久化版）"
    while true; do
        for task_file in "$QUEUE_DIR"/*.json; do
            [ -f "$task_file" ] || continue
            process_task_file "$task_file"
        done
        sleep 5
    done
}

ensure_runtime
trap 'on_shutdown SIGINT' INT
trap 'on_shutdown SIGTERM' TERM
main_loop

# 错误重试函数
retry_command() {
    local max_retries=3
    local retry_count=0
    local cmd="$1"
    
    while [ $retry_count -lt $max_retries ]; do
        if eval "$cmd"; then
            return 0
        fi
        retry_count=$((retry_count + 1))
        echo "⚠️ 命令失败，重试 $retry_count/$max_retries"
        sleep 2
    done
    return 1
}

# 进程健康检查
check_process() {
    local process_name="$1"
    if pgrep -f "$process_name" > /dev/null; then
        return 0
    else
        echo "❌ 进程 $process_name 未运行"
        return 1
    fi
}

# 定期健康检查（添加到主循环）
# check_process "auth_api"
