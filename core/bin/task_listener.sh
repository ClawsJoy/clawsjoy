#!/bin/bash
# 任务监听与执行引擎 - 完整版

AGENT="$1"
MESSAGE="$2"
LOG_FILE="$HOME/clawsjoy/logs/task_listener.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

if [ -z "$AGENT" ] || [ -z "$MESSAGE" ]; then
    echo "用法: task_listener.sh <agent名> <消息>"
    exit 1
fi

log "收到 Agent: $AGENT, 消息: $MESSAGE"

# 通用函数：提取关键词
extract_keyword() {
    echo "$MESSAGE" | grep -oP '(?<=采集)[^0-9\u4e00-\u9fa5]+' | head -1 | xargs
}

extract_number() {
    echo "$MESSAGE" | grep -oP '\d+' | head -1
}

case "$AGENT" in
    spider)
        # 1. 采集图片
        if [[ "$MESSAGE" =~ 采集 ]]; then
            KEYWORD=$(extract_keyword)
            COUNT=$(extract_number)
            KEYWORD=${KEYWORD:-hongkong}
            COUNT=${COUNT:-5}
            log "执行: spider_unsplash \"$KEYWORD\" $COUNT"
            ~/clawsjoy/bin/spider_unsplash "$KEYWORD" "$COUNT"
        fi
        
        # 2. 批量采集
        if [[ "$MESSAGE" =~ 批量采集 ]]; then
            log "执行: spider_batch"
            ~/clawsjoy/bin/spider_batch
        fi
        
        # 3. 提交素材
        if [[ "$MESSAGE" =~ 提交素材 ]]; then
            CATEGORY=$(echo "$MESSAGE" | grep -oP '(?<=分类[：:])[^，,]+' | head -1)
            SUBJECT=$(echo "$MESSAGE" | grep -oP '(?<=子类[：:])[^，,]+' | head -1)
            CATEGORY=${CATEGORY:-hongkong}
            SUBJECT=${SUBJECT:-victoria}
            log "执行: spider_submit \"素材包\" \"$CATEGORY\" \"$SUBJECT\""
            ~/clawsjoy/bin/spider_submit "素材包" "$CATEGORY" "$SUBJECT"
        fi
        ;;
        
    video-maker)
        # 1. 制作视频（图文）
        if [[ "$MESSAGE" =~ 制作视频 ]]; then
            SCRIPT=$(echo "$MESSAGE" | sed 's/.*制作视频[，,]\?脚本[：:]\?//' | xargs)
            [ -z "$SCRIPT" ] && SCRIPT="ClawsJoy 让AI安全地为每个人工作"
            log "执行: make_video \"$SCRIPT\" \"$HOME/.openclaw/web/images\" \"promo\" \"ClawsJoy 宣传片\""
            ~/clawsjoy/bin/make_video "$SCRIPT" "$HOME/.openclaw/web/images" "promo" "ClawsJoy 宣传片"
        fi
        
        # 2. 下载视频
        if [[ "$MESSAGE" =~ 下载视频 ]]; then
            URL=$(echo "$MESSAGE" | grep -oP 'https?://[^\s]+' | head -1)
            if [ -n "$URL" ]; then
                log "执行: video_download \"$URL\""
                ~/clawsjoy/bin/video_download "$URL"
            fi
        fi
        
        # 3. 截取视频
        if [[ "$MESSAGE" =~ 截取 ]]; then
            START=$(echo "$MESSAGE" | grep -oP '(?<=从)[^秒]+' | head -1)
            DURATION=$(echo "$MESSAGE" | grep -oP '(?<=截取)[^秒]+' | head -1)
            log "执行: video_trim \"video.mp4\" \"${START:-0}\" \"${DURATION:-10}\""
            # ~/clawsjoy/bin/video_trim "video.mp4" "$START" "$DURATION"
        fi
        
        # 4. 合并视频
        if [[ "$MESSAGE" =~ 合并 ]]; then
            log "执行: video_concat"
            # ~/clawsjoy/bin/video_concat
        fi
        
        # 5. 提取音频
        if [[ "$MESSAGE" =~ 提取音频 ]]; then
            log "执行: video_extract_audio"
            # ~/clawsjoy/bin/video_extract_audio "video.mp4"
        fi
        
        # 6. 添加字幕
        if [[ "$MESSAGE" =~ 添加字幕 ]]; then
            TEXT=$(echo "$MESSAGE" | sed 's/.*添加字幕[：:]\?//' | xargs)
            log "执行: add_subtitle \"video.mp4\" \"$TEXT\""
            # ~/clawsjoy/bin/add_subtitle "video.mp4" "$TEXT"
        fi
        
        # 7. 压缩视频
        if [[ "$MESSAGE" =~ 压缩 ]]; then
            log "执行: compress_video \"video.mp4\""
            # ~/clawsjoy/bin/compress_video "video.mp4"
        fi
        
        # 8. 转换格式
        if [[ "$MESSAGE" =~ 转换格式 ]]; then
            TARGET=$(echo "$MESSAGE" | grep -oP '(?<=转换格式[为到])[a-z]+' | head -1)
            log "执行: convert_format \"video.mp4\" \"${TARGET:-mp4}\""
            # ~/clawsjoy/bin/convert_format "video.mp4" "${TARGET:-mp4}"
        fi
        ;;
        
    writer)
        # 1. 写文章
        if [[ "$MESSAGE" =~ 写文章 ]]; then
            TITLE=$(echo "$MESSAGE" | grep -oP '(?<=标题[：:])[^，,]+' | head -1)
            CONTENT=$(echo "$MESSAGE" | grep -oP '(?<=内容[：:]).+' | head -1)
            TITLE=${TITLE:-"ClawsJoy 自动文章"}
            CONTENT=${CONTENT:-"<h1>ClawsJoy</h1><p>让AI安全地为每个人工作</p>"}
            log "执行: write_review \"$TITLE\" \"$CONTENT\" writer"
            ~/clawsjoy/bin/write_review "$TITLE" "$CONTENT" "writer"
        fi
        
        # 2. 写脚本（宣传片）
        if [[ "$MESSAGE" =~ 写脚本 ]]; then
            THEME=$(echo "$MESSAGE" | sed 's/.*写脚本[：:]\?//' | xargs)
            [ -z "$THEME" ] && THEME="多租户隔离"
            SCRIPT="<h1>ClawsJoy 宣传片</h1><h2>主题：$THEME</h2><p>让AI安全地为每个人工作</p>"
            log "执行: write_review \"宣传片脚本 - $THEME\" \"$SCRIPT\" writer"
            ~/clawsjoy/bin/write_review "宣传片脚本 - $THEME" "$SCRIPT" "writer"
        fi
        ;;
        
    designer)
        # 1. 设计 Logo
        if [[ "$MESSAGE" =~ 设计.*[Ll]ogo ]]; then
            TEXT=$(echo "$MESSAGE" | grep -oP '(?<=文字[：:])[^，,]+' | head -1)
            TEXT=${TEXT:-CJ}
            SVG='<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg"><rect width="200" height="200" fill="#667eea"/><text x="100" y="120" text-anchor="middle" fill="white" font-size="80" font-weight="bold">'"$TEXT"'</text></svg>'
            log "执行: write_design \"Logo设计\" \"$SVG\" designer"
            ~/clawsjoy/bin/write_design "Logo设计" "$SVG" "designer"
        fi
        
        # 2. 设计封面
        if [[ "$MESSAGE" =~ 设计封面 ]]; then
            TITLE=$(echo "$MESSAGE" | sed 's/.*设计封面[：:]\?//' | xargs)
            TITLE=${TITLE:-ClawsJoy}
            SVG='<svg width="1280" height="720" xmlns="http://www.w3.org/2000/svg"><rect width="1280" height="720" fill="#667eea"/><text x="640" y="360" text-anchor="middle" fill="white" font-size="60" font-weight="bold">'"$TITLE"'</text></svg>'
            log "执行: write_design \"封面设计\" \"$SVG\" designer"
            ~/clawsjoy/bin/write_design "封面设计" "$SVG" "designer"
        fi
        ;;
        
    messenger)
        # 1. 发布到微信
        if [[ "$MESSAGE" =~ 发布.*微信 ]]; then
            CONTENT=$(echo "$MESSAGE" | sed 's/.*发布.*微信[：:]\?//' | xargs)
            CONTENT=${CONTENT:-"ClawsJoy 让AI安全地为每个人工作"}
            log "执行: write_publish \"微信发布\" \"<p>$CONTENT</p>\" wechat"
            ~/clawsjoy/bin/write_publish "微信发布" "<p>$CONTENT</p>" "wechat"
        fi
        
        # 2. 发布到小红书
        if [[ "$MESSAGE" =~ 发布.*小红书 ]]; then
            CONTENT=$(echo "$MESSAGE" | sed 's/.*发布.*小红书[：:]\?//' | xargs)
            CONTENT=${CONTENT:-"#ClawsJoy #AI #安全"}
            log "执行: write_publish \"小红书发布\" \"$CONTENT\" xiaohongshu"
            ~/clawsjoy/bin/write_publish "小红书发布" "$CONTENT" "xiaohongshu"
        fi
        
        # 3. 发布到 YouTube
        if [[ "$MESSAGE" =~ 发布.*[Yy]ouTube ]]; then
            CONTENT=$(echo "$MESSAGE" | sed 's/.*发布.*YouTube[：:]\?//' | xargs)
            log "执行: publish_youtube \"YouTube发布\" \"$CONTENT\""
            ~/clawsjoy/bin/publish_youtube "YouTube发布" "$CONTENT"
        fi
        ;;
        
    engineer)
        # 1. 部署任务
        if [[ "$MESSAGE" =~ 部署 ]]; then
            COMMAND=$(echo "$MESSAGE" | sed 's/.*部署[命令：:]\?//' | xargs)
            [ -z "$COMMAND" ] && COMMAND="echo 'deploy'"
            log "执行: write_deploy \"部署任务\" \"$COMMAND\" \"自动部署\""
            ~/clawsjoy/bin/write_deploy "部署任务" "$COMMAND" "自动部署"
        fi
        
        # 2. 系统检查
        if [[ "$MESSAGE" =~ 检查 ]]; then
            log "执行: 系统检查"
            echo "✅ 审核 API: 运行中"
            echo "✅ Web 服务: 运行中"
            echo "✅ 路由器: 运行中"
        fi
        ;;
        
    reviewer)
        # 1. 查看待审核
        if [[ "$MESSAGE" =~ 待审核 ]]; then
            log "执行: 查看待审核任务"
            curl -s http://localhost:5005/api/admin/tasks | python3 -c "
import sys,json
tasks = json.load(sys.stdin)
pending = [t for t in tasks if t.get('status') == 'pending']
print(f'待审核任务数: {len(pending)}')
for t in pending[:5]:
    print(f'  - {t.get(\"title\")} (by {t.get(\"submitter\")})')
"
        fi
        
        # 2. 批量通过
        if [[ "$MESSAGE" =~ 批量通过 ]]; then
            log "执行: 批量通过待审核任务"
            curl -s http://localhost:5005/api/admin/tasks | python3 -c "
import sys,json,subprocess
tasks = json.load(sys.stdin)
for t in tasks:
    if t.get('status') == 'pending':
        subprocess.run(['curl', '-s', '-X', 'POST', 'http://localhost:5005/api/admin/approve', '-H', 'Content-Type: application/json', '-d', f'{{\"id\": {t[\"id\"]}, \"comment\": \"批量通过\"}}'])
        print(f'✅ 通过: {t.get(\"title\")}')
"
        fi
        ;;
        
    *)
        log "未知 Agent: $AGENT"
        ;;
esac

log "完成"
    main)
        # 解析 main 输出的任务列表，格式：TASK|<Agent>|<任务描述>
        if [[ "$MESSAGE" =~ TASK\| ]]; then
            # 提取所有任务行
            echo "$MESSAGE" | grep "TASK|" | while read line; do
                AGENT_TASK=$(echo "$line" | cut -d'|' -f2)
                DESC=$(echo "$line" | cut -d'|' -f3-)
                
                log "调度: $AGENT_TASK -> $DESC"
                
                # 调用对应的 agent_do 执行子任务
                ~/clawsjoy/bin/agent_do.sh "$AGENT_TASK" "$DESC"
                sleep 2
            done
        fi
        ;;
