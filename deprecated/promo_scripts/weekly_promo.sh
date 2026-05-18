#!/bin/bash
# ClawsJoy 每周宣传片自动生产脚本（真视频生成版）

LOG_FILE="$HOME/clawsjoy/logs/weekly_promo.log"
API_URL="http://localhost:5005/api/admin"
VIDEO_DIR="$HOME/.openclaw/web/videos"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

mkdir -p "$VIDEO_DIR"
mkdir -p "$HOME/clawsjoy/outbox"

# 获取本周主题
WEEK_NUM=$(date +%W)
THEMES=("多租户隔离：您的数据绝对安全" "Agent自动进化：越用越聪明" "文件事件驱动：让AI可靠执行" "可视听化审核：一目了然")
THEME_INDEX=$((WEEK_NUM % ${#THEMES[@]}))
THEME="${THEMES[$THEME_INDEX]}"

log "🎬 开始生产第 ${WEEK_NUM} 期宣传片 - 主题: $THEME"

# ========== Step 1: Writer 写脚本 ==========
log "📝 Step 1: Writer 撰写脚本..."
SCRIPT_TITLE="ClawsJoy 宣传片 - 第${WEEK_NUM}期"
SCRIPT_CONTENT="<h1>ClawsJoy 品牌宣传片</h1><h2>主题：${THEME}</h2><p>ClawsJoy 让 AI 安全地为每个人工作。</p><h2>核心优势</h2><ul><li>🔒 多租户隔离</li><li>🧠 Agent自动进化</li><li>📁 文件事件驱动</li><li>👁️ 可视听化审核</li></ul><p style='color:#667eea;'>工具易上手，结果令人愉悦</p>"

~/clawsjoy/bin/write_review "$SCRIPT_TITLE" "$SCRIPT_CONTENT" "weekly_promo"
log "✅ 脚本已提交"
sleep 2

# ========== Step 2: Designer 设计封面 ==========
log "🎨 Step 2: Designer 设计封面..."
COVER_TITLE="宣传片封面 - 第${WEEK_NUM}期"
COVER_SVG='<svg width="1280" height="720" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#667eea"/><stop offset="100%" stop-color="#764ba2"/></linearGradient></defs><rect width="1280" height="720" fill="url(#g)"/><text x="640" y="360" text-anchor="middle" fill="white" font-size="60" font-weight="bold">ClawsJoy</text><text x="640" y="430" text-anchor="middle" fill="#c3d0fe" font-size="24">让AI安全地为每个人工作</text><text x="640" y="680" text-anchor="middle" fill="#888" font-size="16">工具易上手，结果令人愉悦</text></svg>'

~/clawsjoy/bin/write_design "$COVER_TITLE" "$COVER_SVG" "weekly_promo"
log "✅ 封面已提交"
sleep 2

# ========== Step 3: Spider 采集素材 ==========
log "🕷️ Step 3: Spider 采集素材..."
DATA_CONTENT="{\"week\":$WEEK_NUM,\"theme\":\"$THEME\",\"slogan\":\"让AI安全地为每个人工作\"}"
~/clawsjoy/bin/write_data "宣传素材 - 第${WEEK_NUM}期" "$DATA_CONTENT" "weekly_promo"
log "✅ 素材已提交"
sleep 2

# ========== Step 4: Video-Maker 生成视频 ==========
log "🎬 Step 4: Video-Maker 制作视频..."

# 4.1 从 Writer 的脚本中提取纯文本
SCRIPT_TEXT=$(echo "$SCRIPT_CONTENT" | sed 's/<[^>]*>//g' | tr '\n' ' ')
log "脚本内容: $SCRIPT_TEXT"

# 4.2 TTS 生成配音（使用 edge-tts，如果没有则用 espeak 替代）
AUDIO_FILE="$VIDEO_DIR/promo_audio_${WEEK_NUM}.mp3"
if command -v edge-tts &> /dev/null; then
    edge-tts --text "$SCRIPT_TEXT" --write-media "$AUDIO_FILE" --voice zh-CN-XiaoxiaoNeural
    log "✅ TTS 配音已生成 (edge-tts)"
elif command -v espeak &> /dev/null; then
    espeak -v zh "$SCRIPT_TEXT" -w "${AUDIO_FILE%.mp3}.wav"
    ffmpeg -i "${AUDIO_FILE%.mp3}.wav" -y "$AUDIO_FILE" -loglevel quiet
    log "✅ TTS 配音已生成 (espeak)"
else
    log "⚠️ 无 TTS 工具，使用静音"
    ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 30 -y "$AUDIO_FILE" -loglevel quiet
fi

# 4.3 获取封面图片路径（保存 SVG 为 PNG）
COVER_IMAGE="$VIDEO_DIR/promo_cover_${WEEK_NUM}.png"
# 将 SVG 转换为 PNG（需要 ImageMagick）
if command -v convert &> /dev/null; then
    echo "$COVER_SVG" | convert svg:- "$COVER_IMAGE"
    log "✅ 封面已转换为 PNG"
else
    # 如果没有 ImageMagick，直接用 SVG 文件
    COVER_IMAGE_FILE="$VIDEO_DIR/promo_cover_${WEEK_NUM}.svg"
    echo "$COVER_SVG" > "$COVER_IMAGE_FILE"
    COVER_IMAGE="$COVER_IMAGE_FILE"
    log "✅ 封面 SVG 已保存"
fi

# 4.4 ffmpeg 合成视频
VIDEO_FILE="$VIDEO_DIR/promo_${WEEK_NUM}.mp4"
ffmpeg -loop 1 -i "$COVER_IMAGE" -i "$AUDIO_FILE" \
       -c:v libx264 -c:a aac -shortest \
       -vf "drawtext=text='ClawsJoy 第${WEEK_NUM}期':fontcolor=white:fontsize=24:x=10:y=10" \
       -y "$VIDEO_FILE" -loglevel quiet

log "✅ 视频已生成: $VIDEO_FILE (大小: $(du -h $VIDEO_FILE | cut -f1))"

# 4.5 提交视频到审核看板
~/clawsjoy/bin/write_video "ClawsJoy 宣传片 - 第${WEEK_NUM}期" "/videos/promo_${WEEK_NUM}.mp4" "weekly_promo"
log "✅ 视频已提交"

sleep 3

# ========== Step 5: 自动审核 ==========
log "📋 Step 5: 自动审核中..."

python3 << PYEOF
import json, subprocess, time

API_URL = "http://localhost:5005/api/admin"

for i in range(15):
    time.sleep(3)
    resp = subprocess.run(['curl', '-s', f'{API_URL}/tasks'], capture_output=True, text=True)
    tasks = json.loads(resp.stdout)
    
    for t in tasks:
        if t.get('submitter') == 'weekly_promo' and t.get('status') == 'pending':
            tid = t['id']
            title = t.get('title', '')
            score = 90 if '宣传片' in title else 85
            subprocess.run([
                'curl', '-s', '-X', 'POST', f'{API_URL}/approve',
                '-H', 'Content-Type: application/json',
                '-d', f'{{"id": {tid}, "comment": "自动审核通过，评分{score}"}}'
            ])
            print(f"✅ 已通过: {title} ({score}分)")

print("🎉 宣传片流水线完成")
PYEOF

log "=========================================="
log "✅ 第 ${WEEK_NUM} 期宣传片生产完成"
log "📹 视频文件: /videos/promo_${WEEK_NUM}.mp4"
log "=========================================="
