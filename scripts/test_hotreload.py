#!/usr/bin/env python3
"""测试配置热重载是否工作"""

import sys
import tempfile
import time
from pathlib import Path

import yaml


def test_hotreload():
    """测试热重载机制"""
    config_path = Path("config/keywords.yaml")

    if not config_path.exists():
        print("❌ config/keywords.yaml 不存在")
        return False

    # 备份原配置
    original = config_path.read_text()

    try:
        # 添加测试标记
        config = yaml.safe_load(original)
        config["_test_timestamp"] = time.time()
        config_path.write_text(yaml.dump(config))

        print("⏳ 等待配置监听器检测 (3秒)...")
        time.sleep(3)

        # 验证是否生效
        sys.path.insert(0, str(Path.cwd()))
        from core.lib.unified_config import unified_config

        loaded = unified_config.get("_test_timestamp", None)

        if loaded:
            print(f"✅ 热重载工作正常 (检测到: {loaded})")
            return True
        else:
            print("❌ 热重载失败: 配置未重新加载")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 恢复配置
        config_path.write_text(original)
        print("📁 配置已恢复")


def test_lazy_reload():
    """测试懒重载机制 - 直接调用"""
    print("\n📌 测试懒重载机制...")
    try:
        from core.lib.config_auto_watcher import config_auto_watcher

        config_auto_watcher.trigger_reload()
        print("✅ 懒重载触发成功")
        return True
    except Exception as e:
        print(f"⚠️ 懒重载测试: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("热重载测试")
    print("=" * 50)

    success = test_hotreload()
    test_lazy_reload()

    sys.exit(0 if success else 1)
