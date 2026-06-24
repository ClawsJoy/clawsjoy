#!/usr/bin/env python3
"""验证 Intent Router - 第四批：小孩子式提问"""

from core.agents.cortex import agent_cortex

print("=" * 60)
print("验证 Intent Router (user_id=demo) - 小孩子测试")
print("=" * 60)

USER_ID = "demo"

# 先存一些基础数据
agent_cortex.process("我叫小明", USER_ID)
agent_cortex.process("记住宠物=狗狗", USER_ID)
agent_cortex.process("记住最喜欢的颜色=蓝色", USER_ID)
agent_cortex.process("记住年龄=8", USER_ID)
agent_cortex.process("记住最好的朋友=小红", USER_ID)

test_cases = [
    # === 变着花样问名字 ===
    ("我叫什么呀", "recall", "小明"),
    ("你还记得我叫啥不", "recall", "小明"),
    ("我是谁来着", "recall", "小明"),
    ("我的名字呢", "recall", "小明"),
    ("你知道我是谁吗", "recall", "小明"),

    # === 变着花样问宠物 ===
    ("我的宠物是什么", "recall", "狗狗"),
    ("我家有啥动物", "recall", "狗狗"),
    ("狗狗还是猫猫", "recall", "狗狗"),
    ("我养了什么", "recall", "狗狗"),

    # === 变着花样问颜色 ===
    ("我喜欢什么颜色", "recall", "蓝色"),
    ("什么颜色最好看", "recall", "蓝色"),
    ("那个颜色是啥来着", "recall", "蓝色"),

    # === 数字相关 ===
    ("我几岁了", "recall", "8"),
    ("我多大", "recall", "8"),
    ("我今年几岁", "recall", "8"),

    # === 朋友相关 ===
    ("我最好的朋友是谁", "recall", "小红"),
    ("谁是我的好朋友", "recall", "小红"),
    ("小红是谁呀", "recall", "小红"),

    # === 重复问同一个问题（测试缓存一致性） ===
    ("我叫什么呀", "recall", "小明"),
    ("我叫什么呀", "recall", "小明"),
    ("我叫什么呀", "recall", "小明"),

    # === 突然改答案 ===
    ("我其实叫大壮", "identity", "大壮"),
    ("我叫什么呀", "recall", "大壮"),
    ("不对我叫铁柱", "identity", "铁柱"),
    ("我叫什么呀", "recall", "铁柱"),
    ("算了还是叫小明吧", "identity", "小明"),
    ("我叫什么呀", "recall", "小明"),

    # === 闲聊夹杂 ===
    ("今天好开心", "chat", None),
    ("对了我的宠物是什么", "recall", "狗狗"),
    ("哈哈真好玩", "chat", None),
    ("那我几岁了", "recall", "8"),

    # === 记新东西 ===
    ("帮我记住我最喜欢的玩具是积木", "memory", "积木"),
    ("我最喜欢的玩具是什么", "recall", "积木"),
    ("我有啥玩具", "recall", "积木"),
]

for i, (user_input, expected_action, expected_value) in enumerate(test_cases, 1):
    print(f"\n--- 测试 {i}: {user_input} ---")
    result = agent_cortex.process(user_input, USER_ID)
    actual_action = result.get('intent', '')
    actual_response = result.get('response', '')
    print(f"  action: {actual_action} (期望: {expected_action})")
    print(f"  response: {actual_response}")

    if expected_action is None:
        print("  ✅ 不做断言")
        continue

    action_ok = actual_action == expected_action
    value_ok = (expected_value is None) or (expected_value in actual_response)

    if action_ok and value_ok:
        print("  ✅ 通过")
    else:
        if not action_ok:
            print(f"  ❌ action 期望 {expected_action}，实际 {actual_action}")
        if not value_ok:
            print(f"  ❌ 期望包含: {expected_value}")
