from lib.smart_config import smart_config
#!/usr/bin/env python3
"""大脑监控与学习报告"""

import json
from datetime import datetime

def generate_report():
    try:
        with open('data/brain_v2.json', 'r') as f:
            brain = json.load(f)
    except Exception as e:
        print(f"❌ 无法读取 brain_v2.json: {e}")
        return
    
    # 直接从 experiences 计算
    experiences = brain.get('experiences', [])
    total = len(experiences)
    success = sum(1 for e in experiences if e.get('reward', 0) > 0)
    rate = (success / total * 100) if total > 0 else 0
    
    kg_count = len(brain.get('knowledge_graph', []))
    analogies = len(brain.get('analogies', []))
    
    print("=" * 50)
    print(f"ClawsJoy 大脑监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    print(f"\n📊 学习统计:")
    print(f"   总经验: {total} 条")
    print(f"   成功: {success} 次 ({rate:.1f}%)")
    print(f"   知识图谱: {kg_count} 节点")
    print(f"   类比库: {analogies} 条")
    
    print(f"\n🎯 健康度评估:")
    health = min(100, int(rate * 1.2))
    if health >= 70:
        print(f"   🟢 健康度: {health}% (良好)")
    elif health >= 40:
        print(f"   🟡 健康度: {health}% (一般)")
    else:
        print(f"   🔴 健康度: {health}% (需改进)")
    
    print("\n✅ 大脑监控完成")

if __name__ == "__main__":
    generate_report()
