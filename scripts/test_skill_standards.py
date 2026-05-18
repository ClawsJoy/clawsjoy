from lib.smart_config import smart_config
"""技能注册标准测试框架"""
import json
import requests
from datetime import datetime

BASE_URL = "http://smart_config.HOST:str(smart_config.get_port("gateway"))"
PASSED = 0
FAILED = 0
FAILED_LIST = []

def test_skill(skill_name, skill_type="atomic"):
    """测试单个技能"""
    global PASSED, FAILED, FAILED_LIST
    
    # 1. 检查技能是否存在
    resp = requests.get(f"{BASE_URL}/api/skills")
    if resp.status_code != 200:
        print(f"  ❌ {skill_name}: API 不可用")
        FAILED += 1
        FAILED_LIST.append(skill_name)
        return False
    
    skills = resp.json()
    if skill_type == "atomic":
        if skill_name not in skills.get("atomic", []):
            print(f"  ❌ {skill_name}: 未注册")
            FAILED += 1
            FAILED_LIST.append(skill_name)
            return False
    else:
        if skill_name not in skills.get("legacy", []):
            print(f"  ❌ {skill_name}: 未注册")
            FAILED += 1
            FAILED_LIST.append(skill_name)
            return False
    
    # 2. 测试执行
    try:
        resp = requests.post(
            f"{BASE_URL}/api/execute",
            json={"skill": skill_name, "params": {"test": True}},
            timeout=10
        )
        if resp.status_code == 200:
            result = resp.json()
            if result.get("success") is not None:
                print(f"  ✅ {skill_name}: 注册正常")
                PASSED += 1
                return True
    except Exception as e:
        pass
    
    print(f"  ❌ {skill_name}: 执行失败")
    FAILED += 1
    FAILED_LIST.append(skill_name)
    return False

def run_full_test():
    """运行完整测试"""
    global PASSED, FAILED, FAILED_LIST
    PASSED = 0
    FAILED = 0
    FAILED_LIST = []
    
    print("=" * 50)
    print("技能注册标准测试")
    print("=" * 50)
    
    # 获取技能列表
    resp = requests.get(f"{BASE_URL}/api/skills")
    if resp.status_code != 200:
        print("❌ 无法获取技能列表")
        return
    
    skills = resp.json()
    atomic_skills = skills.get("atomic", [])
    legacy_skills = skills.get("legacy", [])
    
    print(f"\n📊 待测试技能: {len(atomic_skills)} 个原子技能, {len(legacy_skills)} 个旧技能")
    print()
    
    # 测试原子技能
    print("=== 原子技能测试 ===")
    for skill in atomic_skills:
        test_skill(skill, "atomic")
    
    # 测试旧技能
    print("\n=== 旧架构技能测试 ===")
    for skill in legacy_skills[:20]:
        test_skill(skill, "legacy")
    
    # 输出报告
    print("\n" + "=" * 50)
    print("测试报告")
    print("=" * 50)
    print(f"✅ 通过: {PASSED}")
    print(f"❌ 失败: {FAILED}")
    total = PASSED + FAILED
    if total > 0:
        print(f"📊 通过率: {PASSED/total*100:.1f}%")
    else:
        print("📊 通过率: 0%")
    
    if FAILED_LIST:
        print(f"\n失败技能 ({len(FAILED_LIST)}个): {FAILED_LIST[:15]}")
        if len(FAILED_LIST) > 15:
            print(f"  ... 还有 {len(FAILED_LIST)-15} 个")
    
    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "passed": PASSED,
        "failed": FAILED,
        "failed_list": FAILED_LIST,
        "total": total
    }
    with open("logs/skill_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 报告已保存: logs/skill_test_report.json")

if __name__ == "__main__":
    run_full_test()
