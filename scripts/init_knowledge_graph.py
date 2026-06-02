#!/usr/bin/env python3
"""初始化知识图谱数据"""

import sys
sys.path.insert(0, '/home/flybo/clawsjoy_v5')

from engine.knowledge import knowledge_engine

def init_knowledge_graph():
    """初始化知识图谱"""
    print("📚 开始构建知识图谱...")
    
    # ========== 1. 概念层 ==========
    concepts = [
        # 编程语言
        ("Python", "编程语言", {"用途": "AI、数据科学、Web开发"}),
        ("Java", "编程语言", {"用途": "企业级应用、Android"}),
        ("JavaScript", "编程语言", {"用途": "Web前端、Node.js"}),
        ("Go", "编程语言", {"用途": "云原生、微服务"}),
        
        # AI/ML 概念
        ("机器学习", "AI领域", {"子领域": "监督学习、无监督学习、强化学习"}),
        ("深度学习", "AI领域", {"子领域": "CNN、RNN、Transformer"}),
        ("大语言模型", "AI领域", {"示例": "GPT、Claude、Llama"}),
        
        # 框架
        ("Flask", "Web框架", {"特点": "轻量级、灵活"}),
        ("FastAPI", "Web框架", {"特点": "高性能、自动文档"}),
        ("Django", "Web框架", {"特点": "全栈、内置ORM"}),
        
        # 数据库
        ("MySQL", "数据库", {"类型": "关系型"}),
        ("PostgreSQL", "数据库", {"类型": "关系型、高级特性"}),
        ("Redis", "数据库", {"类型": "内存缓存"}),
        ("MongoDB", "数据库", {"类型": "文档型"}),
        
        # 系统概念
        ("容器", "技术概念", {"代表": "Docker"}),
        ("编排", "技术概念", {"代表": "Kubernetes"}),
        ("微服务", "架构风格", {"特点": "独立部署、技术异构"}),
        
        # ClawsJoy 相关
        ("ClawsJoy", "系统", {"类型": "AI智能体系统"}),
        ("原子引擎", "ClawsJoy组件", {"作用": "可复用智能核心"}),
        ("语义理解", "原子引擎", {"功能": "意图识别、实体提取"}),
        ("用户画像", "原子引擎", {"功能": "偏好学习、个性化"}),
        ("主动学习", "原子引擎", {"功能": "不确定性评估"}),
        ("知识图谱", "原子引擎", {"功能": "概念关联、推理"}),
    ]
    
    for name, category, props in concepts:
        node_id = knowledge_engine.add_concept(name, {"category": category, **props})
        print(f"  ✅ 添加概念: {name} ({category})")
    
    # ========== 2. 关系层 ==========
    relations = [
        # is_a 关系
        ("Python", "编程语言", "is_a"),
        ("Java", "编程语言", "is_a"),
        ("JavaScript", "编程语言", "is_a"),
        ("Flask", "Web框架", "is_a"),
        ("FastAPI", "Web框架", "is_a"),
        ("Django", "Web框架", "is_a"),
        ("机器学习", "AI领域", "is_a"),
        ("深度学习", "AI领域", "is_a"),
        ("大语言模型", "AI领域", "is_a"),
        
        # part_of 关系
        ("语义理解", "原子引擎", "part_of"),
        ("用户画像", "原子引擎", "part_of"),
        ("主动学习", "原子引擎", "part_of"),
        ("知识图谱", "原子引擎", "part_of"),
        
        # related_to 关系
        ("Python", "机器学习", "related_to"),
        ("Python", "Flask", "related_to"),
        ("Python", "FastAPI", "related_to"),
        ("深度学习", "大语言模型", "related_to"),
        ("Redis", "缓存", "related_to"),
        ("容器", "Docker", "related_to"),
        ("编排", "Kubernetes", "related_to"),
        
        # used_for 关系
        ("Flask", "Web开发", "used_for"),
        ("FastAPI", "API开发", "used_for"),
        ("MySQL", "数据存储", "used_for"),
        ("Redis", "缓存加速", "used_for"),
        
        # 原子引擎能力关系
        ("语义理解", "意图识别", "capable_of"),
        ("语义理解", "实体提取", "capable_of"),
        ("用户画像", "偏好学习", "capable_of"),
        ("主动学习", "不确定性评估", "capable_of"),
        ("知识图谱", "概念关联", "capable_of"),
        ("知识图谱", "推理", "capable_of"),
    ]
    
    # 获取节点ID映射
    node_map = {}
    for node in knowledge_engine.nodes.values():
        node_map[node.name] = node.id
    
    for src_name, tgt_name, relation in relations:
        if src_name in node_map and tgt_name in node_map:
            knowledge_engine.add_relation(node_map[src_name], node_map[tgt_name], relation)
            print(f"  ✅ 添加关系: {src_name} → {tgt_name} ({relation})")
        else:
            print(f"  ⚠️ 跳过关系: {src_name} → {tgt_name} (节点不存在)")
    
    # ========== 3. 规则层 ==========
    rules = [
        ("代码帮助规则", "用户想写代码", "调用 code_agent"),
        ("天气查询规则", "用户问天气", "调用天气API或返回模拟数据"),
        ("名字记忆规则", "用户说'我叫XXX'", "记住用户名字并存储到画像"),
        ("偏好学习规则", "用户说'我喜欢XXX'", "记录到用户画像"),
        ("主动询问规则", "意图置信度<0.5", "主动询问用户确认"),
    ]
    
    for name, condition, action in rules:
        knowledge_engine.add_rule(name, condition, action)
        print(f"  ✅ 添加规则: {name}")
    
    # ========== 4. 统计 ==========
    stats = knowledge_engine.get_stats()
    print(f"\n📊 知识图谱统计:")
    print(f"   总节点数: {stats['total_nodes']}")
    print(f"   总关系数: {stats['total_edges']}")
    print(f"   节点类型分布: {dict(stats['node_types'])}")

if __name__ == "__main__":
    init_knowledge_graph()
