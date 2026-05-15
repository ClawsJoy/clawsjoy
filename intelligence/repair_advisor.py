"""智能修复建议器 - 根据错误提供修复建议"""
import json
from pathlib import Path
from collections import defaultdict
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class RepairAdvisor:
    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
        
    def load_knowledge_base(self):
        """加载修复知识库"""
        return {
            'port_in_use': {
                'pattern': 'Address already in use|port.*already in use',
                'solution': '停止占用端口的进程: lsof -i :端口号, kill -9 PID',
                'cmd': "pkill -f 'python' && sleep 2"
            },
            'import_error': {
                'pattern': 'ModuleNotFoundError|ImportError',
                'solution': '安装缺失的依赖: pip install 模块名',
                'cmd': "pip install flask flask_cors requests psutil"
            },
            'memory_error': {
                'pattern': 'MemoryError|out of memory',
                'solution': '清理缓存或增加内存',
                'cmd': "sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true"
            },
            'connection_refused': {
                'pattern': 'Connection refused|Failed to connect',
                'solution': '检查服务是否启动，端口是否正确',
                'cmd': "./stable_start.sh"
            }
        }
    
    def analyze_error(self, error_text):
        """分析错误并提供修复建议"""
        import re
        
        for error_type, info in self.knowledge_base.items():
            if re.search(info['pattern'], error_text, re.I):
                return {
                    'error_type': error_type,
                    'solution': info['solution'],
                    'command': info.get('cmd', ''),
                    'confidence': 0.8
                }
        
        return {
            'error_type': 'unknown',
            'solution': '查看日志获取更多信息',
            'command': 'tail -50 logs/*.log',
            'confidence': 0.3
        }
    
    def suggest_fix(self, log_file='logs/gateway.log'):
        """根据日志建议修复"""
        log_path = Path(log_file)
        if not log_path.exists():
            return None
        
        content = log_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')[-50:]  # 最后50行
        
        suggestions = []
        for line in lines:
            if 'Error' in line or 'error' in line or 'fail' in line:
                advice = self.analyze_error(line)
                if advice['error_type'] != 'unknown':
                    suggestions.append(advice)
        
        return suggestions

if __name__ == "__main__":
    advisor = RepairAdvisor()
    suggestions = advisor.suggest_fix()
    
    print("🔧 智能修复建议")
    print("=" * 40)
    if suggestions:
        for s in suggestions[:3]:
            print(f"\n❌ 错误类型: {s['error_type']}")
            print(f"💡 解决方案: {s['solution']}")
            if s['command']:
                print(f"🔧 修复命令: {s['command']}")
    else:
        print("✅ 未发现明显错误")
