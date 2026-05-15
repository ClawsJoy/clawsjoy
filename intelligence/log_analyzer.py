"""智能日志分析器 - 自动分析日志发现异常模式"""
import re
import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class LogAnalyzer:
    def __init__(self):
        self.log_dir = Path("logs")
        self.patterns = {
            'error': re.compile(r'error|exception|failed|fail|crash', re.I),
            'warning': re.compile(r'warning|warn|deprecated', re.I),
            'success': re.compile(r'success|completed|ok|✅', re.I),
            'port': re.compile(r'port[:\s]+(\d+)', re.I),
        }
        
    def analyze(self, log_file):
        """分析单个日志文件"""
        log_path = self.log_dir / log_file
        if not log_path.exists():
            return None
            
        content = log_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        
        analysis = {
            'file': log_file,
            'total_lines': len(lines),
            'errors': [],
            'warnings': [],
            'port_issues': [],
            'summary': {}
        }
        
        for i, line in enumerate(lines):
            if self.patterns['error'].search(line):
                analysis['errors'].append({'line': i+1, 'text': line[:100]})
            if self.patterns['warning'].search(line):
                analysis['warnings'].append({'line': i+1, 'text': line[:100]})
            
            port_match = self.patterns['port'].search(line)
            if port_match and 'already in use' in line:
                analysis['port_issues'].append(port_match.group(1))
        
        analysis['summary'] = {
            'error_count': len(analysis['errors']),
            'warning_count': len(analysis['warnings']),
            'port_conflicts': len(set(analysis['port_issues']))
        }
        
        return analysis
    
    def analyze_all(self):
        """分析所有日志"""
        results = {}
        for log_file in ['gateway.log', 'file.log', 'agent.log', 'doc.log', 'smart_core.log']:
            result = self.analyze(log_file)
            if result:
                results[log_file] = result
        return results
    
    def generate_report(self):
        """生成分析报告"""
        results = self.analyze_all()
        
        print("\n📊 智能日志分析报告")
        print("=" * 50)
        
        total_errors = 0
        for file, analysis in results.items():
            print(f"\n📄 {file}:")
            print(f"   行数: {analysis['total_lines']}")
            print(f"   错误: {analysis['summary']['error_count']}")
            print(f"   警告: {analysis['summary']['warning_count']}")
            total_errors += analysis['summary']['error_count']
            
            # 显示最近的错误
            if analysis['errors']:
                print(f"   最近错误: {analysis['errors'][-1]['text'][:60]}...")
        
        # 健康评分
        health_score = max(0, 100 - total_errors * 5)
        print(f"\n🏥 日志健康度: {health_score}/100")
        
        return results

if __name__ == "__main__":
    analyzer = LogAnalyzer()
    analyzer.generate_report()
