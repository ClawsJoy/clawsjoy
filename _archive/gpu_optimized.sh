#!/bin/bash
# GPU 优化调度器
# - GPU 任务只在半点执行
# - 单任务串行，避免显存冲突
# - 执行前检查 GPU 是否空闲

cd /mnt/d/clawsjoy

TASK_DIR="/mnt/d/clawsjoy/tasks"
mkdir -p $TASK_DIR

# GPU 任务锁文件（防止并发）
GPU_LOCK="$TASK_DIR/gpu.lock"

# 检查 GPU 是否空闲
is_gpu_idle() {
    # 检查是否有 GPU 进程在运行
    if pgrep -f "ffmpeg|python.*promo_api|python.*sd" > /dev/null; then
        return 1  # GPU 忙碌
    fi
    # 检查锁文件
    if [ -f "$GPU_LOCK" ]; then
        local pid=$(cat "$GPU_LOCK" 2>/dev/null)
        if kill -0 $pid 2>/dev/null; then
            return 1  # 锁存在且进程存活
        fi
    fi
    return 0  # GPU 空闲
}

# 获取 GPU 锁
acquire_gpu_lock() {
    echo $$ > "$GPU_LOCK"
}

# 释放 GPU 锁
release_gpu_lock() {
    rm -f "$GPU_LOCK"
}

# 任务完成标记
is_task_done() { [ -f "$TASK_DIR/${1}.done" ]; }
mark_task_done() { date > "$TASK_DIR/${1}.done"; }
reset_tasks() { rm -f $TASK_DIR/*.done 2>/dev/null; }

# 每小时重置
HOUR=$(date +%H)
CURRENT_HOUR_FILE="$TASK_DIR/current_hour"
if [ -f "$CURRENT_HOUR_FILE" ]; then
    LAST_HOUR=$(cat "$CURRENT_HOUR_FILE")
else
    LAST_HOUR=""
fi

if [ "$HOUR" != "$LAST_HOUR" ]; then
    echo "$HOUR" > "$CURRENT_HOUR_FILE"
    reset_tasks
    echo "=== 新周期: $HOUR:00 ===" >> logs/gpu_scheduler.log
fi

MINUTE=$(date +%M)

# ==================== CPU 任务（整点） ====================
case $MINUTE in
    00)
        if ! is_task_done "collect"; then
            echo "$(date): [CPU] 采集资料" >> logs/gpu_scheduler.log
            python3 spiders/hk_spider.py >> logs/collect.log 2>&1
            [ $? -eq 0 ] && mark_task_done "collect"
        fi
        ;;
    15)
        if ! is_task_done "topic"; then
            if is_task_done "collect"; then
                echo "$(date): [CPU] 生成话题" >> logs/gpu_scheduler.log
                python3 skills/topic_planner/execute.py '{"category": "all"}' >> logs/topic.log 2>&1
                [ $? -eq 0 ] && mark_task_done "topic"
            fi
        fi
        ;;
    30)
        if ! is_task_done "script"; then
            if is_task_done "topic"; then
                echo "$(date): [CPU] 生成脚本" >> logs/gpu_scheduler.log
                python3 skills/script_from_data.py "香港优才计划" >> logs/script.log 2>&1
                [ $? -eq 0 ] && mark_task_done "script"
            fi
        fi
        ;;
esac

# ==================== GPU 任务（半点，智能等待） ====================
if [ "$MINUTE" -eq 45 ]; then
    if ! is_task_done "video"; then
        if is_task_done "script"; then
            # 等待 GPU 空闲（最多等 5 分钟）
            WAIT_COUNT=0
            while ! is_gpu_idle && [ $WAIT_COUNT -lt 10 ]; do
                echo "$(date): [GPU] GPU 忙碌，等待中..." >> logs/gpu_scheduler.log
                sleep 30
                WAIT_COUNT=$((WAIT_COUNT + 1))
            done
            
            if is_gpu_idle; then
                acquire_gpu_lock
                echo "$(date): [GPU] 执行视频合成" >> logs/gpu_scheduler.log
                
                # 低显存模式运行 ffmpeg
                export GPU_MEMORY_LIMIT="4G"
                curl -s -X POST http://localhost:8105/api/promo/make \
                    -H "Content-Type: application/json" \
                    -d '{"topic":"香港优才计划"}' >> logs/video.log 2>&1
                
                release_gpu_lock
                [ $? -eq 0 ] && mark_task_done "video"
            else
                echo "$(date): [GPU] GPU 超时，等待下一周期" >> logs/gpu_scheduler.log
            fi
        fi
    fi
fi

# GPU 显存监控（可选）
if [ "$MINUTE" -eq 50 ]; then
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=memory.used,memory.total --format=csv >> logs/gpu_memory.log 2>&1
    fi
fi
