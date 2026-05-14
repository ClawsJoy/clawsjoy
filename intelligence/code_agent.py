"""Code Agent - 智能命令行助手"""
import readline
import sys
from pathlib import Path
sys.path.insert(0, '/mnt/d/clawsjoy')

from intelligence.code_agent_trainer import CodeAgentTrainer

class CodeAgent:
    """智能命令行助手"""
    
    def __init__(self):
        self.trainer = CodeAgentTrainer()
        self.command_history = []
        
        print("\n" + "="*60)
        print("🤖 Code Agent 已启动")
        print("="*60)
        print("功能: 意图理解 | 命令补全 | 智能纠错")
        print("输入命令，或输入 'exit' 退出")
        print("="*60)
    
    def process_input(self, user_input):
        """处理用户输入"""
        print(f"\n💭 分析: {user_input}")
        
        # 1. 预测意图
        intent = self.trainer.predict_intent(user_input)
        print(f"🎯 意图: {intent['intent']} (置信度 {intent['confidence']:.0%})")
        
        # 2. 建议行动
        print(f"💡 建议: {intent['suggested_action']}")
        
        # 3. 命令补全建议
        words = user_input.split()
        if len(words) > 0 and len(words[0]) > 2:
            suggestions = self.trainer.suggest_completion(words[0])
            if suggestions:
                print(f"\n📝 补全建议:")
                for s in suggestions[:3]:
                    print(f"   {s['command']} ({s['description']})")
        
        # 4. 记录学习
        self.trainer.learn_from_conversation(user_input, "助手响应")
        
        return intent
    
    def run(self):
        """运行交互式"""
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() == 'exit':
                    print("再见!")
                    break
                
                if not user_input:
                    continue
                
                self.process_input(user_input)
                
            except KeyboardInterrupt:
                print("\n\n再见!")
                break
            except Exception as e:
                print(f"错误: {e}")

if __name__ == "__main__":
    agent = CodeAgent()
    agent.run()
