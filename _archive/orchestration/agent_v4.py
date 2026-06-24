#!/usr/bin/env python3
"""Orchestrator v5.0 - 智能任务编排器

改进：
- 三层Agent发现（wisdom_factory → registry → 动态导入）
- 并发执行子任务
- 完整的23个Agent覆盖
- 错误恢复与降级
- 结果聚合增强
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.agents.business.business_agent import BusinessAgent


class OrchestratorV4(BusinessAgent):
    """任务编排器 v5.0"""

    name = "orchestrator"
    description = "智慧任务编排器"
    version = "5.0.0"

    # 完整的Agent类型 → Agent名映射
    SPECIALIST_AGENTS = {
        # 对话
        "chat": "chat_agent",
        # 代码
        "code": "code_agent", "debug": "code_agent", "review": "code_agent",
        # 分析
        "analysis": "analysis_agent", "data": "analysis_agent",
        # 写作
        "writer": "writer_agent", "write": "writer_agent",
        "comic": "comic_writer_agent",
        # 翻译
        "translate": "translate_agent",
        # 计算
        "calculator": "calculator_agent", "calc": "calculator_agent", "math": "calculator_agent",
        # 视觉
        "vision": "vision_agent", "image": "vision_agent", "picture": "vision_agent",
        # 视频
        "video": "video_agent", "video_index": "video_indexer_agent",
        # 音频
        "audio": "audio_agent", "voice": "audio_agent", "tts": "audio_agent",
        # 3D
        "3d": "three_d_agent", "three_d": "three_d_agent",
        # 导演
        "director": "director_agent",
        # 记忆
        "memory": "memory_agent",
        # 方言
        "dialect": "dialect_agent",
        # 协作
        "collaboration": "collaboration_agent", "collab": "collaboration_agent",
        # 决策
        "decision": "decision_agent",
        # 执行
        "executor": "executor_agent", "execute": "executor_agent",
        # 文件
        "file": "file_agent",
        # 管家
        "butler": "butler_agent",
        # 主动服务
        "proactive": "proactive_agent",
        # YouTube
        "youtube": "youtube_agent", "youtube_agent": "youtube_agent",
    }

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._session_id = None
        self._agent_cache = {}
        print(f"🎯 Orchestrator v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.9)

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if context and "session_id" in context:
            self._session_id = context["session_id"]
        return super().process(user_input, context)

    # ====================================================================
    #  核心编排
    # ====================================================================

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        print(f"[Orchestrator] 编排: {user_input[:80]}...")

        task_type = self._identify_task_type(user_input)

        # 单Agent委托
        if task_type in self.SPECIALIST_AGENTS:
            agent_name = self.SPECIALIST_AGENTS[task_type]
            print(f"[Orchestrator] → {agent_name}")
            result = self._delegate_to_agent(agent_name, user_input)
            return self._format_response(result, agent_name)

        # 复杂任务：分解 + 并行执行
        if task_type == "complex":
            subtasks = self._decompose_task(user_input)
            if len(subtasks) == 1:
                result = self._delegate_to_agent(subtasks[0]["agent"], subtasks[0]["description"])
                return self._format_response(result, subtasks[0]["agent"])

            results = self._execute_subtasks_parallel(subtasks)
            merged = self._merge_results(results)
            return self._format_response(merged, "orchestrator")

        # 降级
        result = self._delegate_to_agent("chat_agent", user_input)
        return self._format_response(result, "chat_agent")

    # ====================================================================
    #  任务识别（覆盖23个Agent）
    # ====================================================================

    def _identify_task_type(self, user_input: str) -> str:
        t = user_input.lower()

        # 记忆
        if any(kw in t for kw in ["记住", "回忆", "忘记", "记忆", "记得"]):
            return "memory"
        # 方言
        if any(kw in t for kw in ["方言"]):
            return "dialect"
        # 计算
        if any(kw in t for kw in ["计算", "等于", "加", "减", "乘", "除", "算", "数学"]):
            return "calculator"
        # 翻译
        if any(kw in t for kw in ["翻译", "translate"]):
            return "translate"
        # YouTube
        if any(kw in t for kw in ["youtube", "油管", "频道"]):
            return "youtube"
        # 视频
        if any(kw in t for kw in ["视频分析", "分析视频", "视频索引"]):
            return "video_index"
        if any(kw in t for kw in ["视频", "剪辑", "制作视频", "短视频"]):
            return "video"
        # 3D
        if any(kw in t for kw in ["3d", "三维", "建模"]):
            return "3d"
        # 漫画
        if any(kw in t for kw in ["漫画", "连环画"]):
            return "comic"
        # 图像
        if any(kw in t for kw in ["生成图", "画图", "画画", "图像", "图片"]):
            return "image"
        if any(kw in t for kw in ["识图", "看图"]):
            return "vision"
        # 音频
        if any(kw in t for kw in ["音频", "配音", "语音", "tts"]):
            return "audio"
        # 导演
        if any(kw in t for kw in ["导演", "电影", "剧本", "拍摄"]):
            return "director"
        # 代码调试
        if any(kw in t for kw in ["调试", "debug", "修bug", "报错", "修复代码"]):
            return "debug"
        # 代码审查
        if any(kw in t for kw in ["审查代码", "review", "深度审查"]):
            return "review"
        # 代码生成
        if any(kw in t for kw in ["代码", "编程", "写函数", "算法", "写一个"]):
            return "code"
        # 文件操作
        if any(kw in t for kw in ["文件", "读取", "写入", "保存"]):
            return "file"
        # 管家
        if any(kw in t for kw in ["管家", "待办", "提醒", "日程"]):
            return "butler"
        # 主动建议
        if any(kw in t for kw in ["主动", "建议", "推荐"]):
            return "proactive"
        # 协作
        if any(kw in t for kw in ["协作", "分配任务", "并行"]):
            return "collaboration"
        # 分析
        if any(kw in t for kw in ["分析", "统计", "趋势", "数据", "报告"]):
            return "analysis"
        # 写作
        if any(kw in t for kw in ["写小说", "创作小说", "写故事", "写文章", "撰写", "写作", "写"]):
            return "writer"
        # 决策
        if any(kw in t for kw in ["决策", "决定", "选择"]):
            return "decision"

        # 复杂任务检测（多个动作词）
        action_words = ["分析", "生成", "发送", "创建", "写", "计算", "翻译",
                        "搜索", "整理", "比较", "总结"]
        complex_connectors = ["并且", "同时", "然后", "之后", "接着", "先", "再", "最后",
                             "第一步", "第二步", "首先", "其次"]
        action_count = sum(1 for aw in action_words if aw in t)
        has_connector = any(kw in t for kw in complex_connectors)
        if action_count >= 2 or has_connector:
            return "complex"

        return "chat"

    # ====================================================================
    #  任务分解
    # ====================================================================

    def _decompose_task(self, task: str) -> List[Dict]:
        """将复杂任务拆分为子任务序列"""
        # 按连接词拆分
        parts = re.split(r'然后|接着|之后|再|；|;|第一步|第二步|第三步|首先|其次|最后', task)
        subtasks = []
        for i, part in enumerate(parts, 1):
            part = part.strip()
            if not part:
                continue
            task_type = self._identify_task_type(part)
            agent_name = self.SPECIALIST_AGENTS.get(task_type, "chat_agent")
            subtasks.append({
                "id": i,
                "description": part,
                "agent": agent_name,
                "task_type": task_type,
                "depends_on": [i - 1] if i > 1 else []
            })

        # 只有一个子任务？不用复杂模式
        if len(subtasks) <= 1:
            task_type = self._identify_task_type(task)
            agent_name = self.SPECIALIST_AGENTS.get(task_type, "chat_agent")
            return [{"id": 1, "description": task, "agent": agent_name,
                     "task_type": task_type, "depends_on": []}]

        return subtasks

    # ====================================================================
    #  执行引擎
    # ====================================================================

    def _delegate_to_agent(self, agent_name: str, user_input: str) -> Dict:
        """委托给指定Agent"""
        agent = self._get_agent(agent_name)
        if not agent:
            return {"success": False, "response": f"Agent '{agent_name}' 不可用",
                    "error": f"AgentNotFound: {agent_name}"}

        try:
            context = {"session_id": self._session_id, "user_id": self.user_id}
            if hasattr(agent, 'process'):
                return agent.process(user_input, context)
            elif hasattr(agent, 'handle'):
                return agent.handle(user_input)
            elif hasattr(agent, 'handle_json'):
                return agent.handle_json(user_input)
            else:
                return {"success": False, "response": f"Agent '{agent_name}' 无可用方法"}
        except Exception as e:
            return {"success": False, "response": f"执行失败: {e}", "error": str(e)}

    def _execute_subtasks_parallel(self, subtasks: List[Dict]) -> List[Dict]:
        """并发执行子任务（尊重依赖关系）"""
        results = []
        completed = set()

        # 分离无依赖和有依赖的任务
        independent = [t for t in subtasks if not t.get("depends_on")]
        dependent = [t for t in subtasks if t.get("depends_on")]

        # 并行执行无依赖任务
        if independent:
            with ThreadPoolExecutor(max_workers=min(8, len(independent))) as executor:
                futures = {
                    executor.submit(
                        self._delegate_to_agent, t["agent"], t["description"]
                    ): t for t in independent
                }
                for future in as_completed(futures):
                    t = futures[future]
                    try:
                        result = future.result(timeout=120)
                    except Exception as e:
                        result = {"success": False, "response": f"超时: {e}"}
                    results.append({
                        "id": t["id"],
                        "agent": t["agent"],
                        "success": result.get("success", False),
                        "output": result.get("response", result.get("output_content", "")),
                        "raw": result,
                    })
                    if result.get("success"):
                        completed.add(t["id"])

        # 执行有依赖的任务（依赖已满足）
        for t in dependent:
            deps = t.get("depends_on", [])
            if all(d in completed for d in deps):
                result = self._delegate_to_agent(t["agent"], t["description"])
                results.append({
                    "id": t["id"],
                    "agent": t["agent"],
                    "success": result.get("success", False),
                    "output": result.get("response", result.get("output_content", "")),
                    "raw": result,
                })
            else:
                results.append({
                    "id": t["id"],
                    "agent": t["agent"],
                    "success": False,
                    "output": f"依赖未满足: {deps}",
                })

        # 按id排序
        results.sort(key=lambda x: x["id"])
        return results

    def _merge_results(self, results: List[Dict]) -> Dict:
        """聚合多个子任务的结果"""
        if not results:
            return {"success": False, "response": "无结果"}
        if len(results) == 1:
            return {
                "success": results[0].get("success", False),
                "response": results[0].get("output", ""),
                "output_content": results[0].get("output", ""),
            }

        success_count = sum(1 for r in results if r.get("success"))
        outputs = []
        for r in results:
            agent = r.get("agent", "unknown")
            output = r.get("output", "")
            if output:
                outputs.append(f"## {agent}\n\n{output[:500]}")

        return {
            "success": success_count > 0,
            "response": "\n\n".join(outputs) if outputs else "所有子任务均无输出",
            "output_content": "\n\n".join(outputs),
            "subtask_results": results,
            "summary": f"完成 {success_count}/{len(results)} 个子任务",
        }

    # ====================================================================
    #  响应格式化
    # ====================================================================

    def _format_response(self, result: Dict, agent_name: str) -> Dict:
        response = result.get("response", result.get("output_content", "任务完成"))
        return {
            "success": result.get("success", True),
            "response": response,
            "output_content": response,
            "agent": self.name,
            "executed_by": agent_name,
            "subtask_results": result.get("subtask_results"),
            "summary": result.get("summary"),
        }

    # ====================================================================
    #  Agent 发现（三层降级）
    # ====================================================================

    def _get_agent(self, agent_name: str):
        """三层降级获取Agent实例"""
        cache_key = f"{agent_name}:{self.user_id}"
        if cache_key in self._agent_cache:
            return self._agent_cache[cache_key]

        agent = (
            self._from_wisdom(agent_name)
            or self._from_registry(agent_name)
            or self._from_import(agent_name)
        )

        if agent:
            self._agent_cache[cache_key] = agent
        else:
            print(f"[Orchestrator] ⚠️ 无法获取Agent: {agent_name}")
        return agent

    def _from_wisdom(self, agent_name: str):
        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            return wisdom_factory.get_wisdom_agent(agent_name, self.user_id)
        except Exception:
            return None

    def _from_registry(self, agent_name: str):
        try:
            from core.lib.agent_registry import agent_registry
            cls = agent_registry.get(agent_name)
            return cls(self.user_id) if cls else None
        except Exception:
            return None

    def _from_import(self, agent_name: str):
        try:
            mod = __import__(f"agents.{agent_name}.agent_v4", fromlist=["*"])
            for attr in dir(mod):
                if attr.endswith("V4") and hasattr(getattr(mod, attr), 'process'):
                    return getattr(mod, attr)(self.user_id)
            for attr in dir(mod):
                if "Agent" in attr and hasattr(getattr(mod, attr), 'process'):
                    return getattr(mod, attr)(self.user_id)
        except ImportError:
            pass
        return None

    # ====================================================================
    #  统计与辅助
    # ====================================================================

    def get_stats(self) -> Dict:
        return {
            "agent": self.name,
            "version": self.version,
            "cached_agents": len(self._agent_cache),
            "cached_names": list(self._agent_cache.keys()),
        }

    def clear_cache(self):
        self._agent_cache.clear()

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


# ====================================================================
#  测试
# ====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("OrchestratorV4 测试 (v5.0)")
    print("=" * 60)

    agent = OrchestratorV4("test")

    tests = [
        "帮我写一段Python排序代码",
        "翻译hello到中文",
        "分析一下这些数据",
        "记住我的密码是123456",
        "方言开心怎么说",
        "你好",
    ]

    for t in tests:
        print(f"\n📥 {t}")
        result = agent.process(t)
        print(f"   成功: {result.get('success')}")
        print(f"   执行者: {result.get('executed_by', 'N/A')}")
        print(f"   响应: {result.get('response', '')[:200]}")
        print(f"   摘要: {result.get('summary', 'N/A')}")

    print(f"\n📊 统计: {agent.get_stats()}")
    print("\n✅ OrchestratorV4 测试完成")
