#!/bin/bash
cd /mnt/d/clawsjoy

MINUTE=$(date +%M)

case $MINUTE in
    00) echo "$(date): 执行采集" >> logs/scheduler.log; python3 spiders/hk_spider.py >> logs/collect.log 2>&1 ;;
    15) echo "$(date): 执行话题" >> logs/scheduler.log; python3 skills/topic_planner.py >> logs/topic.log 2>&1 ;;
    30) 
        echo "$(date): 执行专家脚本生成" >> logs/scheduler.log
        TOPIC=$(python3 skills/topic_planner.py | python3 -c "import sys,json; print(json.load(sys.stdin).get('topic', '香港'))")
        python3 skills/expert_script_writer.py "$TOPIC" > /tmp/expert_script.txt
        ;;
    45)
        echo "$(date): 执行视频制作" >> logs/scheduler.log
        SCRIPT=$(cat /tmp/expert_script.txt 2>/dev/null)
        if [ -n "$SCRIPT" ]; then
            curl -s -X POST http://localhost:8105/api/promo/make \
                -H "Content-Type: application/json" \
                -d "{\"topic\":\"香港优才计划\",\"script\":\"$SCRIPT\"}" >> logs/video.log 2>&1
        fi
        ;;
esac
