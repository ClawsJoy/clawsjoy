import sys
sys.path.insert(0, '/home/flybo/clawsjoy_v5')

from engine.atomic.atomic_engine_v25 import AtomicEngineV25
import json

# 创建引擎
engine = AtomicEngineV25()

# 测试各个 handler
test_cases = [
    ("chat", {"raw_input": "你好", "action": "chat", "user_id": "test"}),
    ("code", {"raw_input": "写一个函数", "action": "code", "user_id": "test"}),
    ("translate", {"raw_input": "翻译 hello 成中文", "action": "translate", "user_id": "test"}),
]

for name, data in test_cases:
    print(f"\n=== 测试 {name} ===")
    try:
        result = engine.process(data)
        # 尝试序列化
        json.dumps(result)
        print(f"✅ {name} 可以序列化")
        print(f"   返回字段: {list(result.keys())}")
    except Exception as e:
        print(f"❌ {name} 序列化失败: {e}")
        print(f"   返回内容: {result}")
