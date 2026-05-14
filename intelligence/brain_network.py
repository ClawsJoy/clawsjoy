"""ClawsJoy 大脑神经网络 - 不依赖LLM的核心决策"""
import json
import numpy as np
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_enhanced import brain as brain_core

class BrainNeuralNetwork:
    """大脑神经网络 - 基于经验和知识图谱的决策系统"""
    
    def __init__(self):
        self.weights = self.load_or_init_weights()
        self.decision_history = []
        self.confidence_threshold = 0.7  # 低于此阈值才调用LLM
        
        print("\n" + "="*60)
        print("🧠 ClawsJoy 大脑神经网络初始化")
        print("="*60)
        print(f"📊 经验数量: {brain_core.get_stats().get('total_experiences', 0)}")
        print(f"🔗 知识节点: {brain_core.get_stats().get('knowledge_graph_nodes', 0)}")
        print(f"⚖️ 决策阈值: {self.confidence_threshold}")
        print("="*60)
    
    def load_or_init_weights(self):
        """加载或初始化神经网络权重"""
        weights_file = Path("data/brain_weights.json")
        
        if weights_file.exists():
            with open(weights_file, 'r') as f:
                return json.load(f)
        
        # 初始化权重（基于经验学习）
        return {
            'fault_recognition': defaultdict(lambda: 0.5),
            'strategy_selection': defaultdict(lambda: defaultdict(lambda: 0.5)),
            'success_prediction': defaultdict(lambda: 0.5)
        }
    
    def save_weights(self):
        """保存权重"""
        weights_file = Path("data/brain_weights.json")
        with open(weights_file, 'w') as f:
            json.dump(self.weights, f, indent=2)
    
    def recognize_fault(self, fault_type, context):
        """大脑识别故障类型（神经网络推理）"""
        # 从经验中搜索相似故障
        experiences = brain_core.knowledge.get('experiences', [])
        
        similar_faults = []
        for exp in experiences[-100:]:  # 最近100条
            if fault_type in exp.get('action', ''):
                success = exp.get('result', {}).get('success', False)
                weight = self.weights['fault_recognition'].get(fault_type, 0.5)
                
                similar_faults.append({
                    'success': success,
                    'weight': weight,
                    'context': exp.get('context', '')
                })
        
        if similar_faults:
            # 计算置信度
            confidence = sum(f['weight'] for f in similar_faults if f['success']) / len(similar_faults)
            return min(0.95, max(0.3, confidence))
        
        return 0.5  # 未知故障，中等置信度
    
    def select_strategy(self, fault_type, previous_attempts):
        """大脑选择修复策略（基于知识图谱）"""
        # 从知识图谱查找关联
        knowledge_graph = brain_core.knowledge.get('knowledge_graph', [])
        
        strategies = {
            'port_in_use': ['kill_port', 'change_port', 'wait'],
            'connection_refused': ['restart', 'check_service', 'wait'],
            'timeout': ['increase_timeout', 'restart', 'optimize'],
            'memory_error': ['clean_cache', 'restart', 'increase_memory'],
            'process_killed': ['restart', 'check_resources', 'monitor']
        }
        
        available = strategies.get(fault_type, ['restart'])
        
        # 计算每个策略的得分
        strategy_scores = []
        for strategy in available:
            # 从知识图谱查找策略成功率
            score = self.weights['strategy_selection'][fault_type][strategy]
            
            # 排除已失败的策略
            if strategy in previous_attempts:
                score *= 0.3
            
            strategy_scores.append((strategy, score))
        
        # 按得分排序
        strategy_scores.sort(key=lambda x: x[1], reverse=True)
        
        return strategy_scores[0][0] if strategy_scores else 'restart'
    
    def predict_success(self, fault_type, strategy):
        """预测修复成功率"""
        base_rate = self.weights['success_prediction'].get(fault_type, 0.5)
        strategy_modifier = self.weights['strategy_selection'][fault_type].get(strategy, 0.5)
        
        prediction = (base_rate + strategy_modifier) / 2
        return min(0.95, max(0.1, prediction))
    
    def learn_from_outcome(self, fault_type, strategy, success, duration):
        """从结果中学习，更新神经网络权重"""
        # 更新故障识别权重
        current = self.weights['fault_recognition'].get(fault_type, 0.5)
        delta = 0.1 if success else -0.05
        self.weights['fault_recognition'][fault_type] = min(0.95, max(0.05, current + delta))
        
        # 更新策略选择权重
        current_strategy = self.weights['strategy_selection'][fault_type].get(strategy, 0.5)
        delta_strategy = 0.15 if success else -0.1
        self.weights['strategy_selection'][fault_type][strategy] = min(0.95, max(0.05, current_strategy + delta_strategy))
        
        # 更新成功率预测权重
        current_pred = self.weights['success_prediction'].get(fault_type, 0.5)
        delta_pred = (0.1 if success else -0.05) * (1 / (1 + duration/10))
        self.weights['success_prediction'][fault_type] = min(0.95, max(0.05, current_pred + delta_pred))
        
        # 记录到大脑核心
        brain_core.record_experience(
            agent="brain_network",
            action=f"learn_{fault_type}_{strategy}",
            result={"success": success, "duration": duration},
            context=f"weight_updated_{self.weights['strategy_selection'][fault_type][strategy]:.2f}"
        )
        
        self.save_weights()
        
        return self.weights['strategy_selection'][fault_type][strategy]
    
    def decide(self, fault_type, context, previous_attempts=None):
        """大脑决策主入口"""
        previous_attempts = previous_attempts or []
        
        # 1. 大脑神经网络推理
        fault_confidence = self.recognize_fault(fault_type, context)
        strategy = self.select_strategy(fault_type, previous_attempts)
        success_prediction = self.predict_success(fault_type, strategy)
        
        decision = {
            'fault_type': fault_type,
            'strategy': strategy,
            'confidence': fault_confidence,
            'predicted_success_rate': success_prediction,
            'source': 'brain_neural_network'
        }
        
        # 2. 如果置信度低于阈值，考虑LLM辅助
        if fault_confidence < self.confidence_threshold:
            decision['llm_assisted'] = True
            decision['source'] = 'brain_network_with_llm'
        
        return decision
    
    def show_network_stats(self):
        """显示神经网络统计"""
        print("\n" + "="*60)
        print("🧠 大脑神经网络统计")
        print("="*60)
        
        print("\n故障识别权重:")
        for fault, weight in list(self.weights['fault_recognition'].items())[:5]:
            bar = "█" * int(weight * 20)
            print(f"  {fault}: {bar} {weight:.2f}")
        
        print("\n策略选择权重:")
        for fault, strategies in list(self.weights['strategy_selection'].items())[:3]:
            print(f"  {fault}:")
            for strategy, weight in list(strategies.items())[:3]:
                bar = "█" * int(weight * 20)
                print(f"    {strategy}: {bar} {weight:.2f}")

if __name__ == "__main__":
    network = BrainNeuralNetwork()
    
    # 测试决策
    test_faults = ['connection_refused', 'port_in_use', 'timeout']
    
    for fault in test_faults:
        print(f"\n{'='*40}")
        print(f"测试故障: {fault}")
        decision = network.decide(fault, {})
        print(f"策略: {decision['strategy']}")
        print(f"置信度: {decision['confidence']:.2f}")
        print(f"预测成功率: {decision['predicted_success_rate']:.2f}")
        print(f"来源: {decision['source']}")
    
    network.show_network_stats()
