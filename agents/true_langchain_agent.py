#!/usr/bin/env python3
"""
真正的学习型运维 Agent - 基于 LangChain + 向量数据库
支持：LLM推理 + 长期记忆 + 相似问题匹配
"""

import subprocess
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

# LangChain 核心
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class TrueLangChainOpsAgent:
    def __init__(self):
        # 路径配置
        self.project_root = Path("/mnt/d/clawsjoy")
        self.memory_dir = self.project_root / "data" / "agent_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 LLM（使用你的 qwen2.5:7b）
        self.llm = Ollama(
            model="qwen2.5:7b",  # 你已安装的模型
            temperature=0.3,      # 低温度保证可靠性
            num_ctx=4096,         # 上下文窗口
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )
        
        # 初始化向量化模型（用于相似问题搜索）
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text:latest"  # 你已安装
        )
        
        # 初始化向量数据库（存储历史解决方案）
        self.vector_db = self._init_vector_db()
        
        # 经验记忆（结构化存储）
        self.experience_memory = self._load_experiences()
        
        # 学习统计
        self.stats = self._load_stats()
        
        print("🧠 智能运维 Agent 初始化完成")
        print(f"   LLM: qwen2.5:7b")
        print(f"   向量数据库: Chroma (存储 {len(self.vector_db.get()['ids']) if self.vector_db else 0} 条记录)")
        print(f"   经验记忆: {len(self.experience_memory)} 条")
    
    def _init_vector_db(self) -> Chroma:
        """初始化向量数据库"""
        persist_dir = self.memory_dir / "chroma_db"
        
        # 如果已有数据，加载它
        if persist_dir.exists() and list(persist_dir.glob("*.parquet")):
            return Chroma(
                persist_directory=str(persist_dir),
                embedding_function=self.embeddings
            )
        
        # 否则创建新数据库
        return Chroma(
            persist_directory=str(persist_dir),
            embedding_function=self.embeddings
        )
    
    def _load_experiences(self) -> List[Dict]:
        """加载经验记忆"""
        exp_file = self.memory_dir / "experiences.json"
        if exp_file.exists():
            with open(exp_file) as f:
                return json.load(f)
        return []
    
    def _save_experiences(self):
        """保存经验记忆"""
        exp_file = self.memory_dir / "experiences.json"
        with open(exp_file, 'w') as f:
            json.dump(self.experience_memory, f, indent=2, ensure_ascii=False)
    
    def _load_stats(self) -> Dict:
        """加载统计信息"""
        stats_file = self.memory_dir / "stats.json"
        if stats_file.exists():
            with open(stats_file) as f:
                return json.load(f)
        return {"total_fixes": 0, "success_fixes": 0, "skills": {}}
    
    def _save_stats(self):
        """保存统计信息"""
        stats_file = self.memory_dir / "stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def observe(self) -> Dict:
        """观察系统状态"""
        state = {}
        
        # 检查 PM2 服务
        result = subprocess.run("pm2 list", shell=True, capture_output=True, text=True)
        output = result.stdout
        
        services = ["agent-api", "chat-api", "promo-api", "health-api", "joymate-api"]
        for svc in services:
            if svc in output:
                if "errored" in output:
                    state[svc] = {"status": "errored", "need_fix": True}
                elif "online" in output:
                    state[svc] = {"status": "online", "need_fix": False}
                elif "stopped" in output:
                    state[svc] = {"status": "stopped", "need_fix": True}
                else:
                    state[svc] = {"status": "unknown", "need_fix": True}
            else:
                state[svc] = {"status": "not_found", "need_fix": True}
        
        # 检查 Docker 容器
        result = subprocess.run("docker ps -a", shell=True, capture_output=True, text=True)
        containers = ["clawsjoy-web", "clawsjoy-postgres", "clawsjoy-redis"]
        for container in containers:
            if container in result.stdout:
                if "Exited" in result.stdout:
                    state[container] = {"status": "exited", "need_fix": True}
                else:
                    state[container] = {"status": "running", "need_fix": False}
            else:
                state[container] = {"status": "not_exist", "need_fix": True}
        
        return state
    
    def search_similar_problems(self, problem: str, k: int = 3) -> List[Dict]:
        """搜索相似的历史问题"""
        if not self.vector_db or self.vector_db._collection.count() == 0:
            return []
        
        try:
            docs = self.vector_db.similarity_search(problem, k=k)
            results = []
            for doc in docs:
                # 解析元数据
                try:
                    result = json.loads(doc.metadata.get("solution", "{}"))
                    result["similarity_score"] = doc.metadata.get("score", 0.8)
                    results.append(result)
                except:
                    pass
            return results
        except Exception as e:
            print(f"⚠️ 搜索相似问题失败: {e}")
            return []
    
    def think(self, problem: str, context: Dict, similar_cases: List[Dict]) -> Dict:
        """让 LLM 思考解决方案"""
        
        # 构建 prompt
        prompt = f"""你是 SRE 运维专家。服务出现问题，请分析原因并给出修复命令。

## 当前问题
服务: {problem}
状态: {context.get('status', 'unknown')}

## 历史成功案例（参考）
{self._format_similar_cases(similar_cases) if similar_cases else "无历史记录"}

## 可用修复工具
- pm2 restart <service>
- pm2 start <service> --port <port>
- docker start <container>
- docker-compose up -d <service>
- journalctl -u <service> -n 50
- netstat -tlnp | grep <port>

## 要求
1. 分析可能原因（1-2句话）
2. 给出具体的 bash 命令
3. 提供验证命令（如何确认修复成功）
4. 如果用户是 Windows/WSL 环境，注意路径使用 /mnt/d/ 格式

请以 JSON 格式返回：
{{
    "analysis": "问题分析",
    "commands": ["命令1", "命令2"],
    "verify_command": "验证成功的命令",
    "confidence": 0.8
}}"""
        
        try:
            # 调用 LLM
            response = self.llm.invoke(prompt)
            
            # 提取 JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                return plan
            else:
                # LLM 返回的不是 JSON，生成默认方案
                return self._default_plan(problem)
                
        except Exception as e:
            print(f"❌ LLM 思考失败: {e}")
            return self._default_plan(problem)
    
    def _format_similar_cases(self, cases: List[Dict]) -> str:
        """格式化相似案例"""
        if not cases:
            return "暂无"
        
        formatted = []
        for i, case in enumerate(cases[:2], 1):
            formatted.append(f"{i}. 问题: {case.get('problem', 'unknown')}")
            formatted.append(f"   解决方案: {case.get('commands', [])}")
            formatted.append(f"   成功率: {case.get('success_rate', 0)}%")
        return "\n".join(formatted)
    
    def _default_plan(self, problem: str) -> Dict:
        """默认方案（当 LLM 失败时）"""
        service_name = problem.split('.')[0]
        return {
            "analysis": f"尝试重启服务 {service_name}",
            "commands": [f"pm2 restart {service_name}"],
            "verify_command": f"pm2 list | grep {service_name} | grep -q online",
            "confidence": 0.5
        }
    
    def execute(self, commands: List[str], verify_command: str) -> Tuple[bool, str, float]:
        """执行修复命令"""
        start_time = time.time()
        
        # 执行所有命令
        for cmd in commands:
            print(f"   🔧 执行: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"   ❌ 命令失败: {result.stderr[:100]}")
                return False, result.stderr, time.time() - start_time
        
        # 验证
        time.sleep(2)
        verify_result = subprocess.run(verify_command, shell=True)
        success = verify_result.returncode == 0
        
        duration = time.time() - start_time
        
        if success:
            print(f"   ✅ 验证成功")
        else:
            print(f"   ❌ 验证失败")
        
        return success, "", duration
    
    def learn_from_outcome(self, problem: str, plan: Dict, success: bool, duration: float, error_msg: str = ""):
        """从结果中学习"""
        
        # 1. 保存经验到 JSON
        experience = {
            "id": len(self.experience_memory) + 1,
            "timestamp": datetime.now().isoformat(),
            "problem": problem,
            "analysis": plan.get("analysis", ""),
            "commands": plan.get("commands", []),
            "verify_command": plan.get("verify_command", ""),
            "success": success,
            "duration": round(duration, 2),
            "error": error_msg[:200] if error_msg else ""
        }
        self.experience_memory.append(experience)
        self._save_experiences()
        
        # 2. 保存到向量数据库（用于相似问题搜索）
        doc = Document(
            page_content=f"问题: {problem}\n原因: {plan.get('analysis', '')}\n解决方案: {plan.get('commands', [])}",
            metadata={
                "problem": problem,
                "solution": json.dumps({
                    "problem": problem,
                    "commands": plan.get("commands", []),
                    "verify_command": plan.get("verify_command", ""),
                    "success": success
                }),
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
        )
        self.vector_db.add_documents([doc])
        
        # 3. 更新统计
        self.stats["total_fixes"] += 1
        if success:
            self.stats["success_fixes"] += 1
        
        skill_name = problem.split('.')[0]
        if skill_name not in self.stats["skills"]:
            self.stats["skills"][skill_name] = {"total": 0, "success": 0}
        self.stats["skills"][skill_name]["total"] += 1
        if success:
            self.stats["skills"][skill_name]["success"] += 1
        
        self._save_stats()
        
        # 4. 输出学习结果
        print(f"\n📝 学习记录 #{experience['id']}")
        print(f"   问题: {problem}")
        print(f"   结果: {'✅ 成功' if success else '❌ 失败'}")
        print(f"   耗时: {duration:.2f}秒")
        
        if success:
            print(f"   🎯 成功率更新: {self.stats['skills'][skill_name]['success']}/{self.stats['skills'][skill_name]['total']}")
    
    def self_reflect(self, problem: str, failed_plan: Dict, error_msg: str) -> Dict:
        """自我反思：分析失败原因，生成改进方案"""
        
        prompt = f"""之前的修复方案失败了，请反思并给出新方案。

## 问题
{problem}

## 之前的方案
命令: {failed_plan.get('commands', [])}
验证: {failed_plan.get('verify_command', '')}

## 失败信息
{error_msg[:300]}

## 可能原因
1. 服务端口被占用
2. 配置文件错误
3. 依赖服务未启动
4. 权限不足

请给出新的修复方案（JSON格式）：
{{
    "analysis": "失败原因分析",
    "commands": ["修正后的命令"],
    "verify_command": "验证命令",
    "confidence": 0.6
}}"""
        
        try:
            response = self.llm.invoke(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                new_plan = json.loads(json_match.group())
                return new_plan
        except:
            pass
        
        return failed_plan  # 返回相同方案（兜底）
    
    def heal(self, max_attempts: int = 3):
        """主循环：自我修复"""
        print("=" * 70)
        print("🩺 学习型运维 Agent 启动 (LangChain + RAG)")
        print(f"📊 历史统计: {self.stats['success_fixes']}/{self.stats['total_fixes']} 次成功")
        print("=" * 70)
        
        # 观察
        print("\n👁️ 观察系统状态...")
        state = self.observe()
        
        # 找出问题
        problems = []
        for svc, info in state.items():
            if info.get("need_fix"):
                problems.append(f"{svc}.{info['status']}")
                print(f"   ⚠️ {svc}: {info['status']}")
        
        if not problems:
            print("\n✅ 所有服务正常")
            return True
        
        print(f"\n🔍 发现 {len(problems)} 个问题")
        
        # 处理每个问题
        for problem in problems:
            print(f"\n{'='*50}")
            print(f"🎯 处理: {problem}")
            
            # 搜索相似历史问题
            similar = self.search_similar_problems(problem)
            if similar:
                print(f"📚 找到 {len(similar)} 个相似历史案例")
                for s in similar[:2]:
                    print(f"   - 历史方案: {s.get('commands', [])} (成功率: {s.get('success', False)})")
            
            # 多轮尝试
            attempt = 0
            success = False
            last_plan = None
            
            while attempt < max_attempts and not success:
                attempt += 1
                print(f"\n💡 第 {attempt} 次尝试...")
                
                # 思考方案
                if attempt == 1:
                    plan = self.think(problem, state.get(problem.split('.')[0], {}), similar)
                else:
                    # 反思改进
                    print(f"🧠 自我反思中...")
                    plan = self.self_reflect(problem, last_plan, last_error)
                
                print(f"📋 分析: {plan.get('analysis', '无分析')}")
                print(f"🔧 命令: {plan.get('commands', [])}")
                print(f"✓ 验证: {plan.get('verify_command', '')}")
                
                # 执行
                success, error_msg, duration = self.execute(
                    plan.get("commands", []),
                    plan.get("verify_command", "")
                )
                
                last_plan = plan
                last_error = error_msg
                
                # 学习结果
                self.learn_from_outcome(problem, plan, success, duration, error_msg)
                
                if success:
                    print(f"\n🎉 问题解决！共尝试 {attempt} 次")
                    break
                else:
                    print(f"\n⚠️ 第 {attempt} 次失败，继续尝试...")
            
            if not success:
                print(f"\n💀 {max_attempts} 次尝试均失败，需要人工介入")
                print(f"   最后错误: {last_error[:200]}")
        
        # 总结
        print("\n" + "=" * 70)
        print("📊 学习总结")
        print(f"   总修复次数: {self.stats['total_fixes']}")
        print(f"   成功次数: {self.stats['success_fixes']}")
        print(f"   当前成功率: {self.stats['success_fixes']/max(self.stats['total_fixes'],1)*100:.1f}%")
        
        print("\n技能掌握情况:")
        for skill, stats in sorted(self.stats["skills"].items()):
            rate = stats["success"] / max(stats["total"], 1) * 100
            bar = "█" * int(rate / 10) + "░" * (10 - int(rate / 10))
            print(f"   {skill}: [{bar}] {rate:.0f}% ({stats['success']}/{stats['total']})")
        
        print("=" * 70)
        return True

def main():
    """主函数"""
    agent = TrueLangChainOpsAgent()
    
    # 连续运行，让它学习
    for round_num in range(1, 4):
        print(f"\n{'🔄'*35}")
        print(f"第 {round_num} 轮学习")
        print(f"{'🔄'*35}")
        agent.heal()
        time.sleep(3)
    
    print("\n✅ 学习完成！Agent 现在会越来越聪明")

if __name__ == "__main__":
    main()