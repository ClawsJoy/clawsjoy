# 创建新文件: core/agents/builtin/self_upgrading_agent.py

#!/usr/bin/env python3
"""Self-Upgrading Agent - 具备自我升级能力的元认知智能体"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import ollama  # 使用你的Ollama

from core.lib.config_helper import get_data_root


class SelfUpgradingAgent:
    """自我升级型元认知智能体 - 不仅反思，还能改进"""

    def __init__(self, model_name: str = "qwen2.5:7b-instruct-q4_0"):
        self.model_name = model_name
        self.reflection_dir = Path(f"{get_data_root()}/metacognition")
        self.reflection_dir.mkdir(parents=True, exist_ok=True)

        self.reflections_file = self.reflection_dir / "reflections.json"
        self.improvements_file = self.reflection_dir / "improvements.json"

        self._load_data()

    def _load_data(self):
        """加载历史数据"""
        self.reflections = []
        self.improvements = []

        if self.reflections_file.exists():
            with open(self.reflections_file, "r") as f:
                self.reflections = json.load(f)
        if self.improvements_file.exists():
            with open(self.improvements_file, "r") as f:
                self.improvements = json.load(f)

    def _save_data(self):
        """保存数据"""
        with open(self.reflections_file, "w") as f:
            json.dump(self.reflections[-500:], f, indent=2, ensure_ascii=False)
        with open(self.improvements_file, "w") as f:
            json.dump(self.improvements[-200:], f, indent=2, ensure_ascii=False)

    def analyze_with_llm(self, agent_name: str, recent_logs: list) -> Dict:
        """
        使用本地Ollama模型深度分析Agent表现

        Args:
            agent_name: Agent名称
            recent_logs: 最近N次交互日志
        """

        # 统计失败模式
        failures = [log for log in recent_logs if not log.get("success", True)]
        failure_patterns = {}

        for fail in failures[-20:]:  # 分析最近20次失败
            error = fail.get("error", "unknown")
            failure_patterns[error] = failure_patterns.get(error, 0) + 1

        # 构建分析提示
        analysis_prompt = f"""
你是元认知分析专家。分析 {agent_name} 的表现：

## 性能数据
- 总交互: {len(recent_logs)}
- 成功率: {(len(recent_logs) - len(failures)) / max(len(recent_logs),1) * 100:.1f}%
- 最近失败模式: {json.dumps(failure_patterns, ensure_ascii=False)}

## 最近3次失败案例
{json.dumps(failures[-3:], indent=2, ensure_ascii=False, default=str)}

请：
1. 诊断根本原因（1句话）
2. 提出具体改进方案（修改配置参数或提示词）
3. 预估改进后成功率提升（百分比）

以JSON格式输出：
{{"root_cause": "...", "improvement": {{"type": "config|prompt", "key": "...", "new_value": "..."}}, "expected_gain": 数字}}
"""

        try:
            # 调用本地Ollama
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": analysis_prompt}],
                options={"temperature": 0.3, "num_predict": 500},
            )

            result = json.loads(response["message"]["content"])
            return result
        except Exception as e:
            print(f"⚠️ LLM分析失败: {e}")
            return {"root_cause": "unknown", "improvement": None, "expected_gain": 0}

    def apply_improvement(self, agent_name: str, improvement: Dict) -> bool:
        """
        应用改进到目标Agent配置文件

        Args:
            agent_name: Agent名称（如chat_agent, code_agent）
            improvement: 改进建议
        """

        # 查找Agent配置文件
        config_paths = [
            Path(f"agents/{agent_name}/config.yaml"),
            Path(f"agents/{agent_name}/config.yml"),
            Path(f"agents/{agent_name}/config.json"),
        ]

        config_file = None
        for path in config_paths:
            if path.exists():
                config_file = path
                break

        if not config_file:
            print(f"⚠️ 未找到 {agent_name} 的配置文件")
            return False

        # 备份原配置
        backup_file = config_file.with_suffix(".yaml.bak")
        shutil.copy2(config_file, backup_file)

        try:
            # 根据改进类型应用
            imp_type = improvement.get("type", "config")

            if imp_type == "config":
                # 修改配置参数
                return self._modify_config(config_file, improvement)
            elif imp_type == "prompt":
                # 修改提示词（需要额外处理）
                return self._modify_prompt(agent_name, improvement)

            return False

        except Exception as e:
            print(f"❌ 应用改进失败: {e}")
            # 恢复备份
            shutil.copy2(backup_file, config_file)
            return False

    def _modify_config(self, config_file: Path, improvement: Dict) -> bool:
        """修改YAML/JSON配置文件"""
        import yaml

        key = improvement.get("key", "")
        new_value = improvement.get("new_value", "")

        # 读取配置
        with open(config_file, "r") as f:
            if config_file.suffix == ".json":
                config = json.load(f)
            else:
                config = yaml.safe_load(f)

        # 修改配置（支持点号路径，如 "agent.temperature"）
        keys = key.split(".")
        target = config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = new_value

        # 写回
        with open(config_file, "w") as f:
            if config_file.suffix == ".json":
                json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(config, f, allow_unicode=True)

        print(f"✅ 已修改 {config_file}: {key} = {new_value}")
        return True

    def _modify_prompt(self, agent_name: str, improvement: Dict) -> bool:
        """修改Agent的系统提示词"""
        agent_file = Path(f"agents/{agent_name}/agent.py")

        if not agent_file.exists():
            return False

        # 备份
        backup_file = agent_file.with_suffix(".py.bak")
        shutil.copy2(agent_file, backup_file)

        # 这里可以修改提示词字符串
        # 简化版：记录需要手动修改
        print(f"📝 建议手动修改 {agent_file} 中的提示词")
        return True

    def should_upgrade(self, agent_name: str, success_rate: float) -> bool:
        """判断是否需要升级"""
        # 检查最近的改进记录
        recent_improvements = [
            imp
            for imp in self.improvements
            if imp.get("agent") == agent_name
            and imp.get("timestamp", "").startswith(datetime.now().strftime("%Y-%m-%d"))
        ]

        # 每天最多升级3次
        if len(recent_improvements) >= 3:
            return False

        # 成功率低于70%需要升级
        return success_rate < 0.7

    def upgrade_agent(self, agent_name: str, recent_logs: list) -> Dict:
        """
        完整的升级流程

        Returns:
            {"upgraded": bool, "changes": dict, "expected_gain": float}
        """

        # 1. 计算当前成功率
        successes = sum(1 for log in recent_logs if log.get("success", True))
        success_rate = successes / max(len(recent_logs), 1)

        # 2. 判断是否需要升级
        if not self.should_upgrade(agent_name, success_rate):
            return {"upgraded": False, "reason": f"成功率{success_rate:.1%}不需要升级"}

        # 3. 使用LLM深度分析
        analysis = self.analyze_with_llm(agent_name, recent_logs)

        if not analysis.get("improvement"):
            return {"upgraded": False, "reason": "LLM未提出改进方案"}

        # 4. 应用改进
        success = self.apply_improvement(agent_name, analysis["improvement"])

        # 5. 记录改进
        improvement_record = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "success_rate_before": success_rate,
            "root_cause": analysis.get("root_cause", ""),
            "improvement": analysis["improvement"],
            "expected_gain": analysis.get("expected_gain", 0),
            "applied": success,
        }

        self.improvements.append(improvement_record)
        self._save_data()

        return {
            "upgraded": success,
            "changes": analysis["improvement"],
            "expected_gain": analysis.get("expected_gain", 0),
            "success_rate_before": success_rate,
        }


# 使用示例
if __name__ == "__main__":
    # 测试
    upgrader = SelfUpgradingAgent(model_name="qwen2.5:7b-instruct-q4_0")

    # 模拟chat_agent的日志
    mock_logs = [
        {"success": True, "input": "你好", "output": "你好"},
        {"success": False, "input": "复杂问题", "error": "timeout"},
        {"success": False, "input": "另一个问题", "error": "unknown"},
    ] * 10

    result = upgrader.upgrade_agent("chat_agent", mock_logs)
    print(json.dumps(result, indent=2, ensure_ascii=False))
