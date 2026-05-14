"""安全对齐层 - 防止有害输出"""

import re

SAFETY_PATTERNS = {
    "harmful": [
        r"如何制作危险物品",
        r"攻击.*方法",
        r"破解.*密码",
    ],
    "privacy": [
        r"获取.*他人.*信息",
        r"监控.*他人",
    ]
}

def safety_check(input_text: str, output_text: str) -> tuple:
    """检查输入输出是否安全"""
    for category, patterns in SAFETY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, input_text, re.I):
                return False, f"检测到敏感输入: {category}"
            if re.search(pattern, output_text, re.I):
                return False, f"检测到敏感输出: {category}"
    return True, "安全"
