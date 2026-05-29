#!/bin/bash
# 智能触发器：每小时触发，未完成的任务继续执行

cd /mnt/d/clawsjoy

TASK_DIR="/mnt/d/clawsjoy/tasks"
mkdir -p $TASK_DIR

# 检查任务是否完成
is_task_done() {
    local task=$1
    [ -f "$TASK_DIR/${task}.done" ]
}

# 标记任务完成
mark_task_done() {
    local task=$1
    date > "$TASK_DIR/${task}.done"
}

# 获取当前小时（用于判断是否开始新周期）
HOUR=$(date +%H)
CURRENT_HOUR_FILE="$TASK_DIR/current_hour"

# 检查是否是新的小时
if [ -f "$CURRENT_HOUR_FILE" ]; then
    LAST_HOUR=$(cat "$CURRENT_HOUR_FILE")
else
    LAST_HOUR=""
fi

# 新小时，重置任务状态（但保留已完成的任务）
if [ "$HOUR" != "$LAST_HOUR" ]; then
    echo "$HOUR" > "$CURRENT_HOUR_FILE"
    # 不清除已完成标记，只清理未完成的
    echo "=== 新周期开始: $HOUR:00 ===" >> logs/trigger.log
fi

# 根据分钟数执行或继续未完成的任务
MINUTE=$(date +%M)

case $MINUTE in
    00)
        if ! is_task_done "collect"; then
            echo "$(date): 执行采集" >> logs/trigger.log
            python3 spiders/hk_spider.py >> logs/collect.log 2>&1
            if [ $? -eq 0 ]; then
                mark_task_done "collect"
                echo "$(date): 采集完成" >> logs/trigger.log
            fi
        else
            echo "$(date): 采集已完成，跳过" >> logs/trigger.log
        fi
        ;;
    15)
        if ! is_task_done "topic"; then
            # 检查依赖
            if is_task_done "collect"; then
                echo "$(date): 执行话题生成" >> logs/trigger.log
                python3 skills/topic_planner/execute.py '{"category": "all"}' >> logs/topic.log 2>&1
                if [ $? -eq 0 ]; then
                    mark_task_done "topic"
                    echo "$(date): 话题生成完成" >> logs/trigger.log
                fi
            else
                echo "$(date): 等待采集完成..." >> logs/trigger.log
            fi
        else
            echo "$(date): 话题已完成，跳过" >> logs/trigger.log
        fi
        ;;
    30)
        if ! is_task_done "script"; then
            if is_task_done "topic"; then
                echo "$(date): 执行脚本生成" >> logs/trigger.log
                python3 skills/script_from_data.py "香港优才计划" >> logs/script.log 2>&1
                if [ $? -eq 0 ]; then
                    mark_task_done "script"
                    echo "$(date): 脚本生成完成" >> logs/trigger.log
                fi
            else
                echo "$(date): 等待话题生成完成..." >> logs/trigger.log
            fi
        else
            echo "$(date): 脚本已完成，跳过" >> logs/trigger.log
        fi
        ;;
    45)
        if ! is_task_done "video"; then
            if is_task_done "script"; then
                echo "$(date): 执行视频制作" >> logs/trigger.log
                curl -s -X POST http://localhost:8105/api/promo/make \
                    -H "Content-Type: application/json" \
                    -d '{"topic":"香港优才计划"}' >> logs/video.log 2>&1
                if [ $? -eq 0 ]; then
                    mark_task_done "video"
                    echo "$(date): 视频制作完成" >> logs/trigger.log
                fi
            else
                echo "$(date): 等待脚本生成完成..." >> logs/trigger.log
            fi
        else
            echo "$(date): 视频已完成，跳过" >> logs/trigger.log
        fi
        ;;
esac
