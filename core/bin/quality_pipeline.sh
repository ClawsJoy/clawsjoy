#!/bin/bash
# 质量驱动型宣传片生产流水线

LOG_FILE="$HOME/clawsjoy/logs/quality_pipeline.log"
API_URL="http://localhost:5005/api/admin"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

# 检查任务审核状态
check_approval() {
    local task_id=$1
    local min_score=$2
    
    # 获取任务状态和评分
    local result=$(curl -s "$API_URL/tasks" 2>/dev/null | python3 << PYEOF
import sys, json
try:
    tasks = json.load(sys.stdin)
    for t in tasks:
        if t.get('id') == $task_id:
            print(f"{t.get('status', 'pending')}|{t.get('score', 0)}")
            break
    else:
        print("not_found|0")
except:
    print("error|0")
PYEOF
)
    
    local status=$(echo "$result" | cut -d'|' -f1)
    local score=$(echo "$result" | cut -d'|' -f2)
    
    log "任务 $task_id 状态: $status, 评分: $score"
    
    if [ "$status" = "approved" ] && [ "$score" -ge "$min_score" ]; then
        return 0  # 通过
    elif [ "$status" = "rejected" ]; then
        return 2  # 驳回
    elif [ "$status" = "error" ] || [ "$status" = "not_found" ]; then
        return 3  # 错误
    else
        return 1  # 等待
    fi
}

# Step 1: Writer 写脚本
step1_writer() {
    log "📝 Step 1: Writer 撰写脚本..."
    
    THEME="ClawsJoy 品牌宣传片 - 第$(date +%W)期"
    
    ~/clawsjoy/bin/write_review "$THEME" "<h1>🎬 ClawsJoy 品牌宣传片</h1>
<h2>📖 让AI安全地为每个人工作</h2>
<h2>🏗️ 核心优势</h2>
<ul>
<li>🔒 多租户隔离：银行级数据安全</li>
<li>🧠 Agent自动进化：从反馈中学习</li>
<li>📁 文件事件驱动：AI只创作，系统执行</li>
<li>👁️ 可视听化审核：实时预览</li>
</ul>
<p style='color:#667eea;text-align:center;'>工具易上手，结果令人愉悦</p>" "weekly_promo"
    
    sleep 3
    # 获取最新任务ID
    local task_id=$(curl -s "$API_URL/tasks" 2>/dev/null | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
for t in tasks:
    if t.get('submitter') == 'weekly_promo' and t.get('status') == 'pending':
        print(t.get('id'))
        break
")
    echo "$task_id"
}

# Step 2: Designer 设计封面
step2_designer() {
    log "🎨 Step 2: Designer 设计封面..."
    
    ~/clawsjoy/bin/write_design "宣传片封面 - 第$(date +%W)期" '<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#667eea"/><stop offset="100%" stop-color="#764ba2"/></linearGradient></defs><rect width="800" height="400" fill="url(#g)"/><text x="400" y="200" text-anchor="middle" fill="white" font-size="40" font-weight="bold">ClawsJoy</text><text x="400" y="250" text-anchor="middle" fill="#c3d0fe" font-size="18">让AI安全地为每个人工作</text></svg>' "weekly_promo"
    
    sleep 3
    local task_id=$(curl -s "$API_URL/tasks" 2>/dev/null | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
for t in tasks:
    if t.get('submitter') == 'weekly_promo' and '封面' in t.get('title', '') and t.get('status') == 'pending':
        print(t.get('id'))
        break
")
    echo "$task_id"
}

# Step 3: Spider 采集素材
step3_spider() {
    log "🕷️ Step 3: Spider 采集素材..."
    
    ~/clawsjoy/bin/write_data "宣传素材 - 第$(date +%W)期" '{"brand":"ClawsJoy","slogan":"让AI安全地为每个人工作"}' "weekly_promo"
    
    sleep 3
    local task_id=$(curl -s "$API_URL/tasks" 2>/dev/null | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
for t in tasks:
    if t.get('submitter') == 'weekly_promo' and '素材' in t.get('title', '') and t.get('status') == 'pending':
        print(t.get('id'))
        break
")
    echo "$task_id"
}

# Step 4: Video-Maker 制作视频
step4_video() {
    log "🎬 Step 4: Video-Maker 制作视频..."
    
    ~/clawsjoy/bin/write_video "宣传片 - 第$(date +%W)期" "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "weekly_promo"
    
    sleep 3
    local task_id=$(curl -s "$API_URL/tasks" 2>/dev/null | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
for t in tasks:
    if t.get('submitter') == 'weekly_promo' and '宣传片' in t.get('title', '') and t.get('status') == 'pending':
        print(t.get('id'))
        break
")
    echo "$task_id"
}

# 等待审核
wait_for_approval() {
    local task_id=$1
    local min_score=$2
    local step_name=$3
    local max_wait=${4:-30}  # 默认等待30次（15分钟）
    
    for i in $(seq 1 $max_wait); do
        check_approval "$task_id" "$min_score"
        local result=$?
        case $result in
            0) 
                log "✅ $step_name 审核通过"
                return 0
                ;;
            2) 
                log "❌ $step_name 被驳回，需要修改后重新提交"
                return 1
                ;;
            3)
                log "⚠️ $step_name 查询错误，重试中..."
                ;;
            *)
                log "⏳ 等待 $step_name 审核... ($i/$max_wait)"
                ;;
        esac
        sleep 30
    done
    
    log "❌ $step_name 审核超时"
    return 2
}

# 主流程
main() {
    log "=========================================="
    log "🎬 质量驱动型宣传片流水线启动"
    log "=========================================="
    
    # Step 1: 脚本
    SCRIPT_ID=$(step1_writer)
    if [ -n "$SCRIPT_ID" ]; then
        log "脚本任务ID: $SCRIPT_ID"
        wait_for_approval "$SCRIPT_ID" 80 "脚本" 20
        [ $? -ne 0 ] && exit 1
    else
        log "❌ 脚本提交失败"
        exit 1
    fi
    
    # Step 2: 封面
    COVER_ID=$(step2_designer)
    if [ -n "$COVER_ID" ]; then
        log "封面任务ID: $COVER_ID"
        wait_for_approval "$COVER_ID" 80 "封面" 20
        [ $? -ne 0 ] && exit 1
    else
        log "❌ 封面提交失败"
        exit 1
    fi
    
    # Step 3: 素材
    MATERIAL_ID=$(step3_spider)
    if [ -n "$MATERIAL_ID" ]; then
        log "素材任务ID: $MATERIAL_ID"
        wait_for_approval "$MATERIAL_ID" 75 "素材" 15
        [ $? -ne 0 ] && exit 1
    else
        log "❌ 素材提交失败"
        exit 1
    fi
    
    # Step 4: 视频
    VIDEO_ID=$(step4_video)
    if [ -n "$VIDEO_ID" ]; then
        log "视频任务ID: $VIDEO_ID"
        wait_for_approval "$VIDEO_ID" 85 "视频" 30
        [ $? -ne 0 ] && exit 1
    else
        log "❌ 视频提交失败"
        exit 1
    fi
    
    log "=========================================="
    log "🎉 宣传片流水线完成！所有环节已通过审核"
    log "=========================================="
}

# 运行
main
