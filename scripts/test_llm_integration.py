#!/usr/bin/env python3
"""LLM 集成测试"""

import sys
import json
import requests
sys.path.insert(0, '/mnt/d/clawsjoy_clean')

from lib.llm_config import llm_config
from lib.config_loader import config

def test_llm():
    print("=" * 60)
    print("LLM 集成测试")
    print("=" * 60)
    
    # 1. 配置检查
    print("\n1. LLM 配置:")
    url = llm_config.get_ollama_url()
    model = llm_config.get_ollama_model()
    print(f"   URL: {url}")
    print(f"   模型: {model}")
    
    # 2. 连接测试
    print("\n2. 连接测试:")
    try:
        # 测试 Ollama 连接
        resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            print(f"   ✅ Ollama 连接成功，可用模型: {len(models)} 个")
        else:
            print(f"   ⚠️ Ollama 响应异常: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
    
    print("\n✅ LLM 集成测试完成")

if __name__ == "__main__":
    test_llm()
