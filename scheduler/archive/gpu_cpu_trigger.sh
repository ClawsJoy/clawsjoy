#!/bin/bash
# GPU/CPU 任务分流调度
# GPU任务：半点执行（视频合成、AI生图）
# CPU任务：整点执行（采集、脚本生成）

cd /mnt/d/clawsjoy

TASK_DIR="/mnt/d/clawsjoy/tasks"
mkdir -p $TASK_DIR

is_task_done() { [ -f "$TASK_DIR/${1}.done" ]; }
mark_task_done() { date > "$TASK_DIR/${1}.done"; }
reset_tasks() { rm -f $TASK_DIR/*.done 2>/dev/null; }

# 每小时重置任务状态
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
    echo "=== 新周期开始: $HOUR:00 ===" >> logs/scheduler.log
fi

MINUTE=$(date +%M)

# ==================== 整点任务（CPU） ====================
if [ "$MINUTE" -eq 0 ] || [ "$MINUTE" -eq 15 ] || [ "$MINUTE" -eq 30 ]; then
    
    # 00分：采集（CPU）
    if [ "$MINUTE" -eq 0 ] && ! is_task_done "collect"; then
        echo "$(date): [CPU] 执行采集" >> logs/scheduler.log
        python3 spiders/hk_spider.py >> logs/collect.log 2>&1
        [ $? -eq 0 ] && mark_task_done "collect"
    fi
    
    # 15分：话题生成（CPU）
    if [ "$MINUTE" -eq 15 ] && ! is_task_done "topic"; then
        if is_task_done "collect"; then
            echo "$(date): [CPU] 执行话题生成" >> logs/scheduler.log
            python3 skills/topic_planner/execute.py '{"category": "all"}' >> logs/topic.log 2>&1
            [ $? -eq 0 ] && mark_task_done "topic"
        else
            echo "$(date): [CPU] 等待采集..." >> logs/scheduler.log
        fi
    fi
    
    # 30分：脚本生成（CPU）
    if [ "$MINUTE" -eq 30 ] && ! is_task_done "script"; then
        if is_task_done "topic"; then
            echo "$(date): [CPU] 执行脚本生成" >> logs/scheduler.log
            python3 skills/script_from_data.py "香港优才计划" >> logs/script.log 2>&1
            [ $? -eq 0 ] && mark_task_done "script"
        else
            echo "$(date): [CPU] 等待话题..." >> logs/scheduler.log
        fi
    fi
fi

# ==================== 半点任务（GPU） ====================
if [ "$MINUTE" -eq 45 ]; then
    
    # 45分：视频合成（GPU）
    if ! is_task_done "video"; then
        if is_task_done "script"; then
            echo "$(date): [GPU] 执行视频合成" >> logs/scheduler.log
            curl -s -X POST http://localhost:8105/api/promo/make \
                -H "Content-Type: application/json" \
                -d '{"topic":"香港优才计划"}' >> logs/video.log 2>&1
            [ $? -eq 0 ] && mark_task_done "video"
        else
            echo "$(date): [GPU] 等待脚本..." >> logs/scheduler.log
        fi
    fi
fi

# 额外的 GPU 任务（半点）
# 如果需要 AI 生图，可以在这里添加
# if [ "$MINUTE" -eq 45 ]; then
#     [GPU] 执行 AI 生图任务
# fi
