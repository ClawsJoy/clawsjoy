from lib.smart_config import smart_config
"""测试已迁移的技能"""
import requests
import json

BASE_URL = "http://smart_config.HOST:str(smart_config.get_port("gateway"))"

def test_skill(skill_name, params, expected_success=True):
    """测试单个技能"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/skills/atomic/{skill_name}",
            json=params,
            timeout=10
        )
        result = resp.json()
        success = result.get("success", False)
        
        if success == expected_success:
            print(f"  ✅ {skill_name}: 成功")
            return True
        else:
            print(f"  ❌ {skill_name}: 失败 - {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"  ❌ {skill_name}: 异常 - {e}")
        return False

# 测试数学技能
print("\n📐 测试数学技能:")
test_skill("add", {"a": 10, "b": 20})
test_skill("multiply", {"a": 5, "b": 6})
test_skill("divide", {"a": 100, "b": 4})
test_skill("subtract", {"a": 50, "b": 20})

# 测试文本技能
print("\n📝 测试文本技能:")
test_skill("script_generator", {"topic": "测试"})
test_skill("text_summarizer", {"text": "这是一段很长的文本内容用于测试摘要功能。", "max_length": 20})
test_skill("keyword_extractor", {"text": "上海北京广州深圳"})
test_skill("translate", {"text": "Hello", "target": "zh"})

# 测试音频技能
print("\n🔊 测试音频技能:")
test_skill("audio_generator", {"text": "测试音频"})

# 测试视频技能
print("\n🎬 测试视频技能:")
test_skill("video_composer", {"duration": 5})

# 测试图像技能
print("\n🖼️ 测试图像技能:")
test_skill("compress", {"image_path": "test.jpg"})

print("\n" + "="*50)
