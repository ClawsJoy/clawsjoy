"""自我改进引擎 - 根据元认知结果改进自身"""

import subprocess
import requests
from datetime import datetime
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain
from agents.core.metacognition import metacog

class SelfImprover:
    def __init__(self):
        self.improvement_history = []
    
    def identify_improvements(self):
        """识别需要改进的地方"""
        improvements = []
        
        # 1. 检查大脑效率
        brain_stats = brain.get_stats()
        if brain_stats['success_rate'] < 0.7:
            improvements.append({
                "area": "brain",
                "issue": "成功率偏低",
                "suggestions": ["增加训练数据", "优化Q表参数"]
            })
        
        # 2. 检查技能使用率
        from skills.skill_interface import skill_registry
        skill_count = len(skill_registry.get_skill_names())
        if skill_count > 50:
            improvements.append({
                "area": "skills",
                "issue": "技能数量多但可能低效",
                "suggestions": ["清理未使用技能", "合并相似技能"]
            })
        
        # 3. 检查系统健康
        import subprocess
        result = subprocess.run("df -h / | tail -1 | awk '{print $5}'", 
                                shell=True, capture_output=True, text=True)
        usage = result.stdout.strip().replace('%', '')
        if usage.isdigit() and int(usage) > 80:
            improvements.append({
                "area": "system",
                "issue": f"磁盘使用率 {usage}%",
                "suggestions": ["清理日志", "清理临时文件", "压缩备份"]
            })
        
        return improvements
    
    def execute_improvement(self, improvement):
        """执行改进"""
        area = improvement['area']
        suggestions = improvement['suggestions']
        
        print(f"🔧 改进 {area}: {improvement['issue']}")
        
        if area == "system":
            if "清理日志" in str(suggestions):
                subprocess.run("find /mnt/d/clawsjoy/logs -name '*.log' -mtime +7 -delete", shell=True)
                print("   ✅ 已清理旧日志")
            
            if "清理临时文件" in str(suggestions):
                subprocess.run("find /mnt/d/clawsjoy/tmp -type f -mtime +1 -delete 2>/dev/null", shell=True)
                print("   ✅ 已清理临时文件")
        
        elif area == "brain":
            # 触发大脑训练
            subprocess.run("cd /mnt/d/clawsjoy && python3 agent_core/brain_train.py", shell=True)
            print("   ✅ 已触发大脑训练")
        
        brain.record_experience(
            agent="self_improver",
            action=f"执行改进: {area}",
            result={"success": True},
            context=improvement['issue']
        )
        
        return True
    
    def improve(self):
        """执行自我改进"""
        print("\n" + "="*50)
        print("🔧 自我改进周期")
        print("="*50)
        
        improvements = self.identify_improvements()
        
        if not improvements:
            print("✅ 无需要改进的地方")
            return {"improved": False}
        
        print(f"📋 发现 {len(improvements)} 个改进点")
        
        results = []
        for imp in improvements:
            success = self.execute_improvement(imp)
            results.append({"improvement": imp, "success": success})
            
            # 记录历史
            self.improvement_history.append({
                "timestamp": datetime.now().isoformat(),
                "area": imp['area'],
                "issue": imp['issue'],
                "success": success
            })
        
        return {"improved": True, "results": results}
    
    def get_stats(self):
        return {
            "total_improvements": len(self.improvement_history),
            "recent": self.improvement_history[-5:] if self.improvement_history else []
        }

self_improver = SelfImprover()

if __name__ == '__main__':
    result = self_improver.improve()
    print(f"\n结果: {result}")
