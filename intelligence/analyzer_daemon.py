#!/usr/bin/env python3
"""智能分析器守护进程 - 使用统一配置"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

import json
import time
from datetime import datetime
from lib.unified_config import config
from lib.memory_simple import memory

class AnalyzerDaemon:
    def __init__(self):
        self.log_file = config.get_path('logs') / 'analyzer.log'
        self.interval = 300  # 5分钟
    
    def analyze(self):
        """执行分析"""
        outcomes = memory.recall_all(category='workflow_outcome')
        total = len(outcomes)
        success = len([o for o in outcomes if '成功' in o])
        
        # 构建有效的 JSON 对象
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": total,
            "success_count": success,
            "success_rate": round(success / total * 100, 1) if total > 0 else 0,
            "error_count": len(memory.recall_all(category='error_knowledge')),
            "decision_count": len(memory.recall_all(category='executed_decisions')),
            "user_feedback_count": len(memory.recall_all(category='user_feedback'))
        }
        
        # 存储为有效 JSON 字符串
        json_str = json.dumps(analysis, ensure_ascii=False)
        memory.remember(json_str, category='intelligence_analysis')
        
        return analysis
    
    def run(self):
        print(f"📊 智能分析器启动")
        print(f"   分析间隔: {self.interval}秒")
        print(f"   日志文件: {self.log_file}")
        
        while True:
            try:
                analysis = self.analyze()
                # 写入日志
                with open(self.log_file, 'a') as f:
                    f.write(f"{datetime.now()}: 成功率 {analysis['success_rate']:.1f}% (任务数: {analysis['total_tasks']})\n")
                print(f"✅ {datetime.now().strftime('%H:%M:%S')}: 分析完成 - 成功率 {analysis['success_rate']:.1f}% ({analysis['total_tasks']}任务)")
            except Exception as e:
                print(f"❌ 分析失败: {e}")
            
            time.sleep(self.interval)

if __name__ == "__main__":
    daemon = AnalyzerDaemon()
    daemon.run()
