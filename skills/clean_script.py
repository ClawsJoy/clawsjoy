#!/usr/bin/env python3
import re
import sys

def clean(text):
    # 移除各种标记符号
    text = re.sub(r'\*\*+', '', text)      # **bold**
    text = re.sub(r'__+', '', text)        # __underline__
    text = re.sub(r'#{3,}', '', text)      # ###
    text = re.sub(r'\[[^\]]*\]', '', text) # [xxx]
    text = re.sub(r'[Kk]', '', text)       # 单独的 K
    text = re.sub(r'\n{3,}', '\n\n', text) # 多余换行
    return text.strip()

if __name__ == '__main__':
    content = sys.stdin.read()
    print(clean(content))
