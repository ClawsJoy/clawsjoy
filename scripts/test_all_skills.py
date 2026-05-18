from lib.smart_config import smart_config
"""测试所有已迁移技能"""
import requests
import json
import sys

BASE_URL = "http://smart_config.HOST:str(smart_config.get_port("gateway"))"
passed = 0
failed = 0
failed_list = []

def test_skill(skill_name, params, expected_success=True):
    global passed, failed, failed_list
    try:
        resp = requests.post(
            f"{BASE_URL}/api/skills/atomic/{skill_name}",
            json=params,
            timeout=10
        )
        result = resp.json()
        success = result.get("success", False)
        
        if success == expected_success:
            print(f"  ✅ {skill_name}")
            passed += 1
            return True
        else:
            print(f"  ❌ {skill_name}: {result.get('error', '未知错误')}")
            failed += 1
            failed_list.append(skill_name)
            return False
    except Exception as e:
        print(f"  ❌ {skill_name}: 异常 - {e}")
        failed += 1
        failed_list.append(skill_name)
        return False

# 获取技能列表
resp = requests.get(f"{BASE_URL}/api/skills")
skills_data = resp.json()
atomic_skills = skills_data.get("atomic", [])

print(f"\n📊 发现 {len(atomic_skills)} 个原子技能\n")

# 测试数学技能
print("📐 测试数学技能:")
for skill in ["add", "subtract", "multiply", "divide", "power", "mod", "sqrt", "abs"]:
    if skill in atomic_skills:
        if skill == "sqrt":
            test_skill(skill, {"a": 16})
        elif skill == "abs":
            test_skill(skill, {"a": -5})
        else:
            test_skill(skill, {"a": 10, "b": 5})

# 测试文本技能
print("\n📝 测试文本技能:")
for skill in ["script_generator", "text_summarizer", "keyword_extractor", "translate", 
              "reverse", "to_upper", "to_lower", "trim", "json_parser"]:
    if skill in atomic_skills:
        if skill == "script_generator":
            test_skill(skill, {"topic": "测试"})
        elif skill == "text_summarizer":
            test_skill(skill, {"text": "这是一段测试文本", "max_length": 10})
        elif skill == "keyword_extractor":
            test_skill(skill, {"text": "上海北京广州"})
        elif skill == "translate":
            test_skill(skill, {"text": "Hello", "target": "zh"})
        elif skill == "json_parser":
            test_skill(skill, {"data": '{"test": "ok"}', "operation": "parse"})
        else:
            test_skill(skill, {"text": "Test"})

# 测试图像技能
print("\n🖼️ 测试图像技能:")
for skill in ["compress", "remove_bg", "spider", "image_resize", "image_rotate", "image_filter"]:
    if skill in atomic_skills:
        test_skill(skill, {"image_path": "test.jpg"})

# 测试视频技能
print("\n🎬 测试视频技能:")
for skill in ["video_composer", "add_subtitles", "video_uploader", "video_info", "video_trim", "video_merge"]:
    if skill in atomic_skills:
        test_skill(skill, {"video_path": "test.mp4"})

# 测试音频技能
print("\n🔊 测试音频技能:")
for skill in ["audio_generator"]:
    if skill in atomic_skills:
        test_skill(skill, {"text": "测试"})

# 测试网络技能
print("\n🌐 测试网络技能:")
for skill in ["youtube_uploader", "http_get", "http_post", "download_file"]:
    if skill in atomic_skills:
        if skill == "http_get":
            test_skill(skill, {"url": "https://httpbin.org/get"})
        else:
            test_skill(skill, {"url": "https://httpbin.org/post", "data": {"test": 1}})

# 输出统计
print("\n" + "="*50)
print(f"📊 测试结果: ✅ {passed} 通过, ❌ {failed} 失败")
if failed_list:
    print(f"失败技能: {failed_list}")
print("="*50)

# 保存结果
with open("logs/skill_test_results.json", "w") as f:
    json.dump({"passed": passed, "failed": failed, "failed_list": failed_list}, f)
