#!/bin/bash
# Designer 自动预审脚本

echo "🎨 设计稿自动预审..."

curl -s http://localhost:5005/api/admin/tasks | python3 << PYEOF
import sys,json

tasks = json.load(sys.stdin)
designs = [t for t in tasks if t.get('submitter') == 'designer' and t.get('status') == 'pending']

print(f"发现 {len(designs)} 个待审核设计稿\n")

for d in designs:
    title = d.get('title', '')
    content = d.get('content', '')
    
    # 自动评分规则
    score = 60  # 基础分
    
    # SVG 检测
    if '<svg' in content and '</svg>' in content:
        score += 15
    else:
        score -= 30
    
    # 品牌色检测
    if '#667eea' in content or '667eea' in content:
        score += 10
    
    # 尺寸检测
    if 'width=' in content and 'height=' in content:
        score += 5
    
    # 文字检测
    if '<text' in content:
        score += 5
    
    # 限制分数范围
    score = max(0, min(100, score))
    
    print(f"📐 {title}")
    print(f"   SVG: {'✅' if '<svg' in content else '❌'}")
    print(f"   品牌色: {'✅' if '#667eea' in content else '❌'}")
    print(f"   建议评分: {score}/100")
    
    if score >= 80:
        print(f"   建议: ✅ 自动通过")
    elif score >= 60:
        print(f"   建议: ⏳ 需人工审核")
    else:
        print(f"   建议: ❌ 驳回")
    print()

PYEOF

echo "📋 请登录审核看板手动确认"
