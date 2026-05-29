#!/bin/bash
# 规则执行器 v3 - 真正从 LEARNINGS.md 读取风格/颜色/平台

TENANT="$1"
TASK_TYPE="$2"
CITY="$3"

# 从各 Agent 的 LEARNINGS.md 提取规则
get_rule() {
  local agent=$1
  local key=$2
  grep -i "$key" ~/.openclaw/agents/$agent/evolution/LEARNINGS.md 2>/dev/null | tail -1 | cut -d: -f2- | xargs
}

STYLE=$(get_rule "designer" "风格")
COLOR=$(get_rule "designer" "颜色")
PLATFORM=$(get_rule "messenger" "平台")
KEYWORD=$(get_rule "spider" "关键词")

# 默认值
STYLE=${STYLE:-现代感}
COLOR=${COLOR:-#667eea}
PLATFORM=${PLATFORM:-wechat}
KEYWORD=${KEYWORD:-$CITY}
KEYWORD=${KEYWORD:-hongkong}

case "$TASK_TYPE" in
  "spider")
    ~/clawsjoy/bin/spider_unsplash "$KEYWORD" 5
    ;;
  "design")
    ~/clawsjoy/bin/write_design "${CITY}封面" "<svg><rect fill='$COLOR'/><text>$CITY</text></svg>" designer
    ;;
  "video")
    ~/clawsjoy/bin/make_video "$STYLE" "$HOME/.openclaw/web/images" "promo" "${CITY}宣传片"
    ;;
  "publish")
    ~/clawsjoy/bin/write_publish "${CITY}宣传片完成" "<p>${CITY}视频已生成</p>" "$PLATFORM"
    ;;
  *)
    echo "用法: rule_executor.sh <租户> <task_type> <city>"
    ;;
esac
