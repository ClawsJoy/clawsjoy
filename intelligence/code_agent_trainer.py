"""Code Agent 培养系统 - 从我们的对话中学习"""
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_enhanced import brain as brain_core

class CodeAgentTrainer:
    """培养 Code Agent - 理解意图、补全命令、纠错"""
    
    def __init__(self):
        self.conversation_log = Path("logs/conversation_training.json")
        self.command_patterns = self.load_command_patterns()
        self.intent_history = []
        
        print("\n" + "="*60)
        print("🤖 Code Agent 培养系统")
        print("="*60)
        print("学习来源: 我们每天的对话 (~20万 token/天)")
        print("能力目标: 理解意图 | 补全命令 | 智能纠错")
        print("="*60)
    
    def load_command_patterns(self):
        """加载命令模式"""
        patterns = {
            # 意图识别模式
            'intents': {
                'fix_port': [r'端口.*冲突', r'port.*in use', r'5002.*占用'],
                'restart_service': [r'重启.*服务', r'restart.*service', r'服务.*挂了'],
                'check_status': [r'检查.*状态', r'status', r'查看.*服务'],
                'install_deps': [r'安装.*依赖', r'pip install', r'缺少.*模块'],
                'view_logs': [r'查看.*日志', r'tail.*log', r'日志.*错误'],
                'kill_process': [r'杀死.*进程', r'kill.*pid', r'杀掉.*端口'],
                'code_suggest': [r'代码.*建议', r'优化.*代码', r'重构'],
                'debug': [r'调试', r'bug', r'报错', r'error']
            },
            # 命令补全模板
            'completions': {
                'fix_port': 'fuser -k {port}/tcp',
                'restart_gateway': 'python3 agent_gateway_web.py',
                'restart_agent': 'python3 multi_agent_service_v2.py',
                'restart_doc': 'python3 doc_generator.py',
                'check_port': 'lsof -i:{port}',
                'view_log': 'tail -f logs/{service}.log',
                'kill_pid': 'kill -9 {pid}'
            },
            # 纠错规则
            'corrections': {
                'pythn': 'python',
                'grep': 'grep',
                'staus': 'status',
                'restart': 'restart',
                'kille': 'kill'
            }
        }
        return patterns
    
    def learn_from_conversation(self, user_input, assistant_response):
        """从对话中学习"""
        # 提取用户意图
        intent = self.extract_intent(user_input)
        
        # 提取命令
        commands = self.extract_commands(assistant_response)
        
        # 提取错误和解决方案
        errors = self.extract_errors(user_input, assistant_response)
        
        # 存储学习记录
        learning = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input[:500],
            'assistant_response': assistant_response[:500],
            'intent': intent,
            'commands': commands,
            'errors': errors
        }
        
        self.intent_history.append(learning)
        
        # 保存到文件
        existing = []
        if self.conversation_log.exists():
            with open(self.conversation_log, 'r') as f:
                existing = json.load(f)
        
        existing.append(learning)
        # 保留最近1000条
        if len(existing) > 1000:
            existing = existing[-1000:]
        
        with open(self.conversation_log, 'w') as f:
            json.dump(existing, f, indent=2)
        
        # 同步到大脑
        brain_core.record_experience(
            agent="code_agent_trainer",
            action=f"learn_intent_{intent}",
            result={"commands_found": len(commands)},
            context=user_input[:200]
        )
        
        return learning
    
    def extract_intent(self, text):
        """提取用户意图"""
        text_lower = text.lower()
        
        for intent, patterns in self.command_patterns['intents'].items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        return 'unknown'
    
    def extract_commands(self, text):
        """提取命令"""
        commands = []
        # 匹配 bash 命令
        cmd_pattern = r'`([^`]+)`|\$ ([^\n]+)|^[a-z]+ .*?$'
        matches = re.findall(cmd_pattern, text, re.MULTILINE)
        for match in matches:
            cmd = match[0] or match[1]
            if cmd and len(cmd) < 200:
                commands.append(cmd.strip())
        return commands
    
    def extract_errors(self, user_input, assistant_response):
        """提取错误和解决方案"""
        errors = []
        
        # 常见的错误模式
        error_patterns = [
            (r'Address already in use', 'port_conflict'),
            (r'ModuleNotFoundError', 'missing_dependency'),
            (r'Connection refused', 'service_down'),
            (r'Timeout', 'timeout'),
            (r'Permission denied', 'permission')
        ]
        
        for pattern, error_type in error_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                errors.append({
                    'type': error_type,
                    'pattern': pattern,
                    'solution_found': 'fix' in assistant_response.lower()
                })
        
        return errors
    
    def suggest_completion(self, partial_command):
        """根据部分命令建议补全"""
        partial_lower = partial_command.lower()
        suggestions = []
        
        for key, template in self.command_patterns['completions'].items():
            if key.startswith(partial_lower) or partial_lower.startswith(key[:3]):
                suggestions.append({
                    'command': template,
                    'confidence': 0.8,
                    'description': f'补全: {key}'
                })
        
        # 从历史对话中搜索
        if self.conversation_log.exists():
            with open(self.conversation_log, 'r') as f:
                history = json.load(f)
            
            for record in history[-50:]:  # 最近50条
                for cmd in record.get('commands', []):
                    if partial_lower in cmd.lower() and cmd not in [s['command'] for s in suggestions]:
                        suggestions.append({
                            'command': cmd,
                            'confidence': 0.6,
                            'description': '来自历史对话'
                        })
        
        return suggestions[:5]
    
    def correct_command(self, command):
        """纠正错误命令"""
        words = command.split()
        corrected_words = []
        
        for word in words:
            if word in self.command_patterns['corrections']:
                corrected_words.append(self.command_patterns['corrections'][word])
            else:
                corrected_words.append(word)
        
        corrected = ' '.join(corrected_words)
        
        if corrected != command:
            return {
                'original': command,
                'corrected': corrected,
                'fixed': True
            }
        
        return {'original': command, 'corrected': command, 'fixed': False}
    
    def predict_intent(self, text):
        """预测用户意图"""
        intent = self.extract_intent(text)
        confidence = 0.9 if intent != 'unknown' else 0.3
        
        return {
            'intent': intent,
            'confidence': confidence,
            'suggested_action': self.get_suggested_action(intent)
        }
    
    def get_suggested_action(self, intent):
        """根据意图推荐行动"""
        actions = {
            'fix_port': '执行: fuser -k {port}/tcp',
            'restart_service': '执行: 重启相关服务',
            'check_status': '执行: curl localhost:5002/health',
            'view_logs': '执行: tail -f logs/gateway.log',
            'kill_process': '执行: kill -9 {pid}',
            'code_suggest': '分析代码并提供建议'
        }
        return actions.get(intent, '继续分析')
    
    def show_stats(self):
        """显示训练统计"""
        if not self.conversation_log.exists():
            print("暂无训练数据")
            return
        
        with open(self.conversation_log, 'r') as f:
            history = json.load(f)
        
        # 统计意图分布
        intent_counts = defaultdict(int)
        for record in history:
            intent_counts[record.get('intent', 'unknown')] += 1
        
        print("\n📊 Code Agent 训练统计")
        print("="*40)
        print(f"总训练样本: {len(history)}")
        print("\n意图分布:")
        for intent, count in sorted(intent_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {intent}: {count}")

if __name__ == "__main__":
    trainer = CodeAgentTrainer()
    
    # 测试
    print("\n测试意图识别:")
    test_inputs = [
        "端口5002被占用了，怎么办",
        "帮我重启网关服务",
        "查看一下日志",
        "代码有bug需要调试"
    ]
    
    for inp in test_inputs:
        intent = trainer.predict_intent(inp)
        print(f"\n输入: {inp}")
        print(f"意图: {intent['intent']} (置信度 {intent['confidence']:.0%})")
        print(f"建议: {intent['suggested_action']}")
    
    trainer.show_stats()
