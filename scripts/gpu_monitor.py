#!/usr/bin/env python3
"""GPU 内存监控"""

import subprocess
import json

def get_gpu_memory():
    """获取 GPU 内存使用"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            used, total = result.stdout.strip().split(',')
            return {
                'used_mb': int(used),
                'total_mb': int(total),
                'used_gb': int(used) / 1024,
                'total_gb': int(total) / 1024,
                'free_gb': (int(total) - int(used)) / 1024,
                'usage_percent': int(used) / int(total) * 100
            }
    except:
        pass
    return None

def main():
    gpu_info = get_gpu_memory()
    if gpu_info:
        print(f"GPU 显存使用: {gpu_info['used_gb']:.1f}GB / {gpu_info['total_gb']:.1f}GB ({gpu_info['usage_percent']:.1f}%)")
        if gpu_info['free_gb'] < 0.5:
            print("⚠️ 显存不足！建议使用 CPU offloading")
        else:
            print(f"✅ 可用显存: {gpu_info['free_gb']:.1f}GB")
    else:
        print("ℹ️ 未检测到 GPU，使用 CPU 模式")

if __name__ == "__main__":
    main()
