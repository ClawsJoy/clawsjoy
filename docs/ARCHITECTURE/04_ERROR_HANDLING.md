
错误处理机制 v1.0
错误类型
类型	说明	处理策略
SKILL_NOT_FOUND	技能不存在	回退到 LLM 动态组合
TIMEOUT	执行超时	重试 2 次，失败后降级
LLM_ERROR	LLM 调用失败	切换备用模型
VALIDATION_ERROR	参数验证失败	尝试自动修复参数
降级策略
原子技能失败
    ↓
重试（最多 2 次）
    ↓
切换到备用模型
    ↓
使用简化实现（fallback）
    ↓
记录错误到知识库
自愈机制
记录失败模式到 error_knowledge 记忆

下次遇到相同问题时自动调整

定期分析错误模式并优化
