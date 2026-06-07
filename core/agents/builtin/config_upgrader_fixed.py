#!/usr/bin/env python3
"""配置升级器 - 修复版，添加超时和中断处理"""

import json
import re
import shutil
import signal
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import ollama
import yaml


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("LLM调用超时")


class ConfigUpgraderFixed:
    """配置升级器 - 增强版，带超时控制"""

    def __init__(self, model_name: str = "qwen2.5:7b", timeout_seconds: int = 30):
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self.upgrade_log = Path("data/upgrades/upgrade_history.json")
        self.upgrade_log.parent.mkdir(parents=True, exist_ok=True)
        self._load_history()

    def _load_history(self):
        if self.upgrade_log.exists():
            with open(self.upgrade_log, "r") as f:
                self.history = json.load(f)
        else:
            self.history = []

    def _save_history(self):
        with open(self.upgrade_log, "w") as f:
            json.dump(self.history[-500:], f, indent=2, ensure_ascii=False)

    def _get_current_config_summary(self, agent_name: str) -> str:
        """获取当前配置摘要"""
        config_file = Path(f"agents/{agent_name}/config.yaml")
        if not config_file.exists():
            return "未找到配置文件"

        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            return f"配置文件解析失败: {e}"

        agent_cfg = config.get("agent", {})
        llm_cfg = agent_cfg.get("llm", {})

        return f"""
- 模型: {llm_cfg.get('model', 'unknown')}
- 温度: {llm_cfg.get('temperature', 0.7)}
- max_tokens: {llm_cfg.get('max_tokens', 1024)}
"""

    def _call_llm_with_timeout(self, prompt: str) -> Optional[str]:
        """带超时的LLM调用"""
        import threading

        result = [None]
        error = [None]

        def worker():
            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.1, "num_predict": 500},
                )
                result[0] = response["message"]["content"]
            except Exception as e:
                error[0] = e

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.timeout_seconds)

        if thread.is_alive():
            print(f"   ⏰ LLM调用超时 ({self.timeout_seconds}秒)，使用默认策略")
            return None

        if error[0]:
            print(f"   ⚠️ LLM调用失败: {error[0]}")
            return None

        return result[0]

    def _extract_json_from_response(self, text: str) -> Optional[Dict]:
        """从LLM响应中提取JSON"""
        if not text:
            return None

        try:
            return json.loads(text)
        except:
            pass

        json_pattern = r"```json\s*([\s\S]*?)\s*```"
        match = re.search(json_pattern, text)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass

        brace_pattern = r"\{[\s\S]*\}"
        match = re.search(brace_pattern, text)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass

        return None

    def analyze_performance(self, agent_name: str, logs: List[Dict]) -> Dict:
        """分析Agent性能并生成优化建议"""

        total = len(logs)
        if total == 0:
            return {"has_issue": False, "message": "无日志数据", "success_rate": 1.0}

        successes = sum(1 for log in logs if log.get("success", False))
        success_rate = successes / total if total > 0 else 1.0

        failures = [log for log in logs if not log.get("success", False)]
        failure_types = {}
        for fail in failures:
            error = fail.get("error", "unknown")
            failure_types[error] = failure_types.get(error, 0) + 1

        config_summary = self._get_current_config_summary(agent_name)

        # 简化的提示词
        analysis_prompt = f"""分析 {agent_name} 的性能。

当前配置: {config_summary}

性能数据:
- 总交互: {total}
- 成功率: {success_rate:.1%}
- 失败类型: {json.dumps(failure_types, ensure_ascii=False)}

只输出JSON，格式:
{{"has_issue": true/false, "suggestions": {{"temperature": 数字或null, "max_tokens": 数字或null}}}}
"""

        # 使用超时调用
        response_text = self._call_llm_with_timeout(analysis_prompt)

        if response_text:
            result = self._extract_json_from_response(response_text)
            if result:
                result["success_rate"] = success_rate
                result["total_interactions"] = total
                return result

        # 默认分析（不依赖LLM）
        print(f"   📊 使用默认分析策略")
        return {
            "has_issue": success_rate < 0.7,
            "success_rate": success_rate,
            "total_interactions": total,
            "suggestions": {
                "temperature": 0.8 if success_rate < 0.7 else None,
                "max_tokens": 2048 if "timeout" in str(failure_types) else None,
            },
        }

    def apply_upgrade(self, agent_name: str, suggestions: Dict) -> bool:
        """应用升级建议"""

        config_file = Path(f"agents/{agent_name}/config.yaml")
        if not config_file.exists():
            return False

        has_changes = any(v is not None for v in suggestions.values())
        if not has_changes:
            return False

        backup_file = config_file.with_suffix(".yaml.bak")
        shutil.copy2(config_file, backup_file)

        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            if "agent" not in config:
                config["agent"] = {}
            if "llm" not in config["agent"]:
                config["agent"]["llm"] = {}

            llm_cfg = config["agent"]["llm"]
            changes_made = []

            if suggestions.get("temperature") is not None:
                old = llm_cfg.get("temperature", 0.7)
                new = float(suggestions["temperature"])
                if abs(old - new) > 0.05:
                    llm_cfg["temperature"] = new
                    changes_made.append(f"temperature: {old} → {new}")

            if suggestions.get("max_tokens") is not None:
                old = llm_cfg.get("max_tokens", 1024)
                new = int(suggestions["max_tokens"])
                if new != old:
                    llm_cfg["max_tokens"] = new
                    changes_made.append(f"max_tokens: {old} → {new}")

            if not changes_made:
                return False

            with open(config_file, "w") as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

            print(f"   ✅ 已应用: {', '.join(changes_made)}")
            return True

        except Exception as e:
            print(f"   ❌ 升级失败: {e}")
            shutil.copy2(backup_file, config_file)
            return False

    def upgrade_agent(
        self, agent_name: str, logs: List[Dict], auto_apply: bool = False
    ) -> Dict:
        """完整的升级流程"""

        print(
            f"   📈 当前成功率: {len([l for l in logs if l.get('success')])}/{len(logs)}"
        )

        analysis = self.analyze_performance(agent_name, logs)
        success_rate = analysis.get("success_rate", 1.0)

        if not analysis.get("has_issue"):
            return {
                "upgraded": False,
                "reason": f"性能正常 ({success_rate:.1%})",
                "success_rate_before": success_rate,
            }

        suggestions = analysis.get("suggestions", {})
        has_valid = any(v for v in suggestions.values() if v)

        if not has_valid:
            return {
                "upgraded": False,
                "reason": "无有效改进建议",
                "success_rate_before": success_rate,
            }

        if not auto_apply:
            print(f"   📋 建议: {suggestions}")
            return {
                "upgraded": False,
                "reason": "手动模式",
                "suggestions": suggestions,
                "success_rate_before": success_rate,
            }

        applied = self.apply_upgrade(agent_name, suggestions)

        record = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "success_rate_before": success_rate,
            "suggestions": suggestions,
            "applied": applied,
        }

        self.history.append(record)
        self._save_history()

        return {
            "upgraded": applied,
            "success_rate_before": success_rate,
            "suggestions": suggestions,
        }


if __name__ == "__main__":
    upgrader = ConfigUpgraderFixed(timeout_seconds=15)

    # 测试
    logs = [{"success": i % 2 == 0} for i in range(100)]
    result = upgrader.upgrade_agent("chat_agent", logs, auto_apply=True)
    print(json.dumps(result, indent=2))
