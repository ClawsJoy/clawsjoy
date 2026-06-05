#!/usr/bin/env python3
"""核心流程分析"""

import re

print("=" * 60)
print("ClawsJoy v5 核心流程分析")
print("=" * 60)

# 1. 请求处理流程
print("\n📥 1. 请求处理流程")
print("   HTTP Request")
print("       ↓")
print("   Flask Route (@app.route)")
print("       ↓")
print("   @rate_limit (限流检查)")
print("       ↓")
print("   @monitor_performance (性能监控)")
print("       ↓")
print("   desensitizer.desensitize (数据脱敏)")
print("       ↓")
print("   response_cache.get (缓存检查)")
print("       ↓")
print("   semantic_engine.understand (语义理解)")
print("       ↓")
print("   OrchestratorV6.smart_route (智能路由)")
print("       ↓")
print("   Agent.process (业务处理)")
print("       ↓")
print("   save_memory (记忆存储)")
print("       ↓")
print("   response_cache.set (缓存存储)")
print("       ↓")
print("   JSON Response")

# 2. 智能路由流程
print("\n🎯 2. 智能路由流程 (四引擎)")
print("   ┌─────────────────────────────────────┐")
print("   │         OrchestratorV6               │")
print("   │  ┌─────────┐ ┌─────────┐ ┌─────────┐│")
print("   │  │   LLM   │→│ Vector  │→│ Config  ││")
print("   │  │ Engine  │ │ Engine  │ │ Engine  ││")
print("   │  └─────────┘ └─────────┘ └─────────┘│")
print("   │              ↓                       │")
print("   │         ┌─────────┐                  │")
print("   │         │  Rule   │                  │")
print("   │         │ Engine  │                  │")
print("   │         └─────────┘                  │")
print("   └─────────────────────────────────────┘")
print("                   ↓")
print("           返回 Agent 名称")

# 3. 缓存策略
print("\n💾 3. 缓存策略 (LRU + TTL)")
print("   - 最大容量: 500 条")
print("   - TTL: 1800 秒 (30分钟)")
print("   - 命中率: 动态统计")
print("   - 淘汰策略: LRU")

# 4. 限流策略
print("\n🚦 4. 限流策略 (滑动窗口)")
print("   - 默认限制: 60 次/分钟")
print("   - 窗口大小: 60 秒")
print("   - 超限响应: 429")
