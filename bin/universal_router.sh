#!/bin/bash
OUTBOX_DIR="$HOME/clawsjoy/outbox"
PROCESSING_DIR="$OUTBOX_DIR/processing"
DONE_DIR="$OUTBOX_DIR/done"
FAILED_DIR="$OUTBOX_DIR/failed"
LOG_DIR="$HOME/clawsjoy/logs"
LOG_FILE="$LOG_DIR/universal_router.log"
API_URL="http://localhost:5005/api/submit"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

process_file() {
    local file="$1"
    local filename=$(basename "$file")
    local temp_processing="$PROCESSING_DIR/$filename"
    
    mv "$file" "$temp_processing" 2>/dev/null || return 1
    log "📄 处理: $filename"
    
    # 支持所有文件类型
    case "$filename" in
        *.review.json|*.data.json|.video.json|*.publish.json|*.design.json|*.deploy.json|*.video.json|*.youtube.json|*.xhs.json)
            log "提交到审核 API: $filename"
            if curl -s -X POST "$API_URL" -H "Content-Type: application/json" -d @"$temp_processing" | grep -q "success"; then
                mv "$temp_processing" "$DONE_DIR/$filename"
                log "✅ 成功: $filename"
            else
                mv "$temp_processing" "$FAILED_DIR/$filename"
                log "❌ 失败: $filename"
            fi
            ;;
        *)
            log "⚠️ 未知类型: $filename"
            mv "$temp_processing" "$FAILED_DIR/$filename"
            ;;
    esac
}

mkdir -p "$OUTBOX_DIR" "$PROCESSING_DIR" "$DONE_DIR" "$FAILED_DIR" "$LOG_DIR"
log "🚀 路由器启动，监听: $OUTBOX_DIR"

inotifywait -m "$OUTBOX_DIR" -e create -e moved_to --format '%f' 2>/dev/null | while read FILENAME; do
    [ -z "$FILENAME" ] && continue
    [[ "$FILENAME" =~ ^\. ]] && continue
    FULL_PATH="$OUTBOX_DIR/$FILENAME"
    sleep 0.5
    [ -f "$FULL_PATH" ] && process_file "$FULL_PATH"
done
