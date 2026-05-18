#!/bin/bash
# ClawsJoy CLI 入口

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
log_info() { echo -e "${GREEN}[OK]${NC} $1"; }

# 写脚本
write_script() {
    local topic="$1"
    log_step "生成脚本: $topic"
    
    # 调用 Chat API
    curl -s -X POST http://localhost:8101/api/agent \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"写一个关于『$topic』的3分钟YouTube视频脚本，要求：1.开场吸引人 2.正文3-5个要点 3.结尾引导关注。直接输出脚本。\"}" \
        | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message',''))" > "output/scripts/${topic}.txt"
    
    log_info "脚本已保存: output/scripts/${topic}.txt"
}

# 制作视频
make_video() {
    local city="$1"
    local style="$2"
    log_step "制作视频: $city $style"
    
    curl -s -X POST http://localhost:8105/api/promo/make \
        -H "Content-Type: application/json" \
        -d "{\"city\":\"$city\",\"style\":\"$style\"}"
    log_info "视频生成中..."
}

# 完整流程
full_workflow() {
    local topic="$1"
    log_step "开始完整工作流: $topic"
    write_script "$topic"
    make_video "香港" "人文"
    log_info "工作流完成"
}

# 命令路由
case "$1" in
    write)  write_script "$2" ;;
    make)   make_video "$2" "$3" ;;
    full)   full_workflow "$2" ;;
    help)   echo "用法: ./clawsjoy.sh {write|make|full} [参数]" ;;
    *)      echo "未知命令: $1"; echo "用法: ./clawsjoy.sh {write|make|full} [参数]" ;;
esac
