import re
import sys

def deep_clean(text):
    # 移除所有特殊标记
    patterns = [
        r'#{3,}',           # ###
        r'\*{3,}',          # ***
        r'={3,}',           # ===
        r'AA|BB|CC|DD',     # AA BB
        r'\[.*?\]',         # [xxx]
        r'【.*?】',         # 【xxx】
        r'[\x00-\x08\x0b\x0c\x0e-\x1f]',  # 控制字符
    ]
    for p in patterns:
        text = re.sub(p, '', text, flags=re.MULTILINE)
    
    # 修复换行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

if __name__ == "__main__":
    content = sys.stdin.read()
    print(deep_clean(content))
