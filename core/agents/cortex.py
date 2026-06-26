#!/usr/bin/env python3
"""
AgentCortex v4.0 - ClawsJoy 智能皮层
架构：意图识别 → 上下文检索 → Agent执行 → 回复生成
"""

import json, time, logging, re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

from core.lib.llm_client import llm_client
from core.lib.memory_bank import get_bank
from core.lib.vector_bank import get_vector_bank
from core.lib.growth_engine import get_growth

# fastText 全局模型（只加载一次）
_ft_model = None
def _get_ft_model():
    global _ft_model
    if _ft_model is None:
        try:
            import fasttext, os, sys
            _stderr = sys.stderr
            sys.stderr = open(os.devnull, 'w')
            _ft_model = fasttext.load_model('models/intent_classifier.bin')
            sys.stderr = _stderr
        except:
            pass
    return _ft_model
from core.lib.context_manager import get_context
from core.agents.agent_pool import agent_pool

logger = logging.getLogger(__name__)

MODEL_MAIN = "qwen2.5:7b-instruct-q4_0"


@dataclass
class CapabilityProfile:
    action: str; agent: str
    success_count: int = 0; total_count: int = 0
    avg_confidence: float = 0.5; avg_latency_ms: float = 0; last_used: str = ""

    @property
    def success_rate(self) -> float:
        return self.success_count / max(self.total_count, 1)

    def update(self, success: bool, confidence: float, latency_ms: float):
        self.total_count += 1
        if success: self.success_count += 1
        n = self.total_count
        self.avg_confidence = (self.avg_confidence*(n-1)+confidence)/n
        self.avg_latency_ms = (self.avg_latency_ms*(n-1)+latency_ms)/n
        self.last_used = datetime.now().isoformat()


@dataclass
class RetrievalResult:
    field: str; content: str; source: str; score: float = 0.0


class SystemRetriever:
    def __init__(self):
        self.retrieval_log: List[Dict] = []
        self._bank_cache: Dict[str, Any] = {}

    def _get_bank(self, uid): 
        if uid not in self._bank_cache: self._bank_cache[uid] = get_bank(uid)
        return self._bank_cache[uid]

    def _get_vbank(self, uid):
        k = f"v_{uid}"
        if k not in self._bank_cache: self._bank_cache[k] = get_vector_bank(uid)
        return self._bank_cache[k]

    def auto_retrieve(self, missing, uid, uinput):
        results = {}
        vbank = self._get_vbank(uid)
        bank = self._get_bank(uid)
        for field in missing:
            r = []
            v = vbank.inject(f"{field} {uinput}")
            if v and len(v.strip()) > 10: r.append(RetrievalResult(field, v, "VectorBank", 0.8))
            m = bank.recall(field, limit=3)
            if m and len(m.strip()) > 10 and "未找到" not in m: r.append(RetrievalResult(field, m, "MemoryBank", 0.6))
            if r: results[field] = r
        return results


class CortexValidator:
    VALID_ACTIONS = ["greeting","identity","memory","recall","code","write","analyze","translate","calculate","task","chat"]
    REQUIRED_FIELDS = {"identity":["名字"],"memory":["key","value"],"recall":["query"],"code":["功能描述"],"analyze":["数据"],"translate":["原文"],"calculate":["表达式"],"task":["任务名"]}

    def __init__(self): self.retriever = SystemRetriever()

    def validate(self, reasoning, uinput, uid):
        extracted = reasoning.get("extracted") or {}
        action = reasoning.get("action","")
        if action not in self.VALID_ACTIONS: return {"status":"invalid"}
        if action in ("greeting","chat"): return {"status":"success"}
        needs = self.REQUIRED_FIELDS.get(action,[])
        missing = [f for f in needs if f not in extracted or not extracted[f]]
        return {"status":"missing","missing":missing} if missing else {"status":"success"}


class AgentCortex:
    """v4.0 极简架构：意图识别→上下文检索→Agent执行→回复生成"""

    def __init__(self):
        self._stats = {"total":0,"success":0}
        self._agent_cache: Dict[str,Any] = {}
        self._last_action = "chat"
        self._last_extracted: Dict = {}
        self.validator = CortexValidator()
        self._agent_capabilities = self._load_agent_capabilities()
        logger.info("🧠 AgentCortex v4.0")

    def process(self, user_input: str, user_id: str = "default", context: Dict = None) -> Dict:
        start_time = time.time()
        self._stats["total"] += 1
        if not user_input or len(user_input.strip()) == 0:
            return {"success": True, "response": "请输入您的问题", "method": "empty"}

        # 第1层：意图识别
        action, confidence = self._infer_action(user_input)
        extracted = self._extract(user_input, action)
        self._last_extracted = {}  # 重置，防止跨请求污染
        self._last_action = action
        self._last_extracted = extracted

        # 第1.5层：改动点：根据action决定是否检索上下文 =====
        # WRITE类action：跳过上下文检索，不补全extracted
        WRITE_ACTIONS = {"identity", "memory", "forget", "clear"}
        READ_ACTIONS = {"recall", "question"}
    
        if action in WRITE_ACTIONS:
            # 写操作：不检索历史，不补全
            context_data = {"补全": {}}
    
        elif action in READ_ACTIONS:
            context_data = self._retrieve_context(action, extracted, user_input, user_id)
            # 额外：用 MemoryBank 做语义预检索
            query = extracted.get("query", "") or extracted.get("key", "")
            if query:
                bank = get_bank(user_id, "memory_agent_v4")
                pre_fetched = bank.semantic_search(query)
                if pre_fetched:
                    context_data["补全"]["pre_fetched"] = pre_fetched
    
        else:
            # chat/greeting 等：轻量上下文
            context_data = self._retrieve_context(action, extracted, user_input, user_id)
            if context_data.get("补全"):
                for k, v in context_data["补全"].items():
                    if not extracted.get(k):
                        extracted[k] = v
        # ===== 改动结束 =====

        # 验收
        validation = self.validator.validate({"action":action,"extracted":extracted}, user_input, user_id)
        if validation.get("status") == "missing":
            retrieved = self.validator.retriever.auto_retrieve(validation.get("missing",[]), user_id, user_input)
            if retrieved:
                for field, results in retrieved.items():
                    if results and not extracted.get(field): extracted[field] = results[0].content
            else:
                return {"success":True,"response":f"我还需要知道：{'、'.join(validation['missing'])}。","method":"ask_user"}

        # 第1.8层：决策编排 - 复杂任务分解
        # 检测是否需要编排
        complex_kw = ["然后", "接着", "再", "漫剧", "做成视频", "一键", "全套", "帮我做", "整个流程", "帮我写", "写一首", "写个", "帮我画", "翻译成"]
        need_orchestrate = any(kw in user_input for kw in complex_kw)
        
        if need_orchestrate:
            import re
            # 先用 LLM 分解
            steps = []
            try:
                r = requests.post('http://127.0.0.1:11434/api/generate', json={
                    'model': 'qwen2.5:7b-instruct-q4_0',
                    'prompt': f'将用户请求分解为3-5个执行步骤，每行一个，只输出步骤：\n用户：{user_input}\n分解：',
                    'stream': False
                }, timeout=15)
                for line in r.json().get('response', '').split('\n'):
                    line = line.strip().lstrip('0123456789. -')
                    if line and len(line) > 3:
                        steps.append(line)
            except:
                pass
            
            # LLM 失败则用简单规则
            if not steps:
                steps = re.split(r'[，,然后接着再]+', user_input)
                steps = [s.strip() for s in steps if s.strip()]
            
            if 1 < len(steps) <= 10:
                # 用 do_anything 智能路由每个步骤
                results = []
                for i, step in enumerate(steps):
                    if (time.time()-start_time) > 60:  # 总超时60秒
                        results.append("...")
                        break
                    # do_anything 智能路由
                    try:
                        from skills.core.do_anything import DoAnythingSkill
                        router = DoAnythingSkill()
                        route = router.execute({"text": step, "input": step})
                        target = route.get("target", "")
                        if target and target != "llm":
                            agent = self._get_agent(target, user_id)
                            if agent:
                                r = agent.process(step, {})
                                results.append(r.get("response", "")[:300])
                                continue
                    except:
                        pass
                    # 如果是翻译步骤，传入上一步结果
                    prev = results[-1] if results else ""
                    if ("翻译" in step or "译" in step) and prev:
                        r = self.process(f"翻译：{prev[:200]}", user_id, context)
                    else:
                        r = self.process(step, user_id, context)
                    results.append(r.get("response", ""))
                reply = " | ".join(results)
                latency_ms = (time.time()-start_time)*1000
                self._learn(user_input, "orchestrated", {}, reply, latency_ms, user_id)
                self._stats["success"] += 1
                return {"success":True,"response":reply,"method":"orchestrated","steps":len(steps)}

        # 第2层：Agent执行
        agents = self._infer_agents(action)
        agent_result = None
        if agents and action not in ("greeting","chat"):
            agent_result = self._execute_single(agents[0], user_input, user_id, context_data)

        # 第3层：回复生成
        reply = self._generate_reply(user_input, action, extracted, context_data, user_id, agent_result)

        latency_ms = (time.time()-start_time)*1000
        self._learn(user_input, action, extracted, reply, latency_ms, user_id)
        self._stats["success"] += 1

        # 主动服务：生成建议
        proactive = ""
        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            pa = wisdom_factory.get_agent("proactive_agent", user_id)
            proactive = pa.process(user_input, {"user_id": user_id}).get("response", "")[:300]
        except:
            pass

        return {"success":True,"response":reply,"output_content":reply,"intent":action,"confidence":confidence,"method":"v4","agents_used":agents,"extracted":extracted,"proactive":proactive}

    # ========== 意图识别 ==========

    def _infer_action(self, user_input: str) -> Tuple[str,float]:
        # 1. fastText 意图分类（优先）
        try:
            model = _get_ft_model()
            if model:
                label, conf = model.predict(user_input.strip())
                action = label[0].replace('__label__', '')
                # 高置信度直接返回，低置信度降级为 chat
                if conf[0] > 0.8:
                    return action, conf[0]
                if conf[0] < 0.5:
                    return "chat", conf[0]
                # 0.5-0.8 之间，走正则兜底，不直接信任
        except:
            pass
        
        text = user_input.strip().lower()

        import sys

        # ===== 第0层：特殊查询（最高优先级） =====
        if re.search(r"我叫(?:什么|来着)", text):
            return "recall", 0.90
        if re.search(r"上次.*密码|密码.*多少|那个密码", text):
            return "recall", 0.90

        # greeting
        greet = ["^你好","^嗨","^hi","^hello","^你是谁","^你叫什么","^你是哪位","^介绍一下"]
        for p in greet:
            if re.search(p, text): return "greeting", 0.95

        # identity（必须在memory之前）
        if re.search(r"^我是[^谁]", text) or re.search(r"^我叫[^什来]", text) or re.search(r"^叫我", text):
            return "identity", 0.90
        if "名字叫" in text and not any(w in text for w in ["什么","来着","呢"]):
            return "identity", 0.88

        # memory
        if any(w in text for w in ["记住","保存","存储","记一下","记下","帮我记","帮我存","存一下"]):
            if any(w in text for w in ["是多少","是什么","什么","多少"]): return "recall", 0.80
            return "memory", 0.90

        # recall
        recall_words = ["还记得","记不记得","记得吗","你忘了吗","帮我查","帮我找","查一下","找一下",
                        "是什么","哪些","哪里","怎么","如何","谁","来着","多少","是多少", "是啥", "啥", "什么东西", "吃的", "爱吃什么", "喜欢什么", "有没有", "在哪儿", "在哪"]
        if any(w in text for w in recall_words):
            return "recall", 0.80

        # 能力规则表
        from core.lib.ability_rules import PRIORITY, ABILITY_REGEX
        for action in PRIORITY:
            if action in ("greeting","identity","memory","recall"): continue
            rules = ABILITY_REGEX.get(action,{})
            for pattern in rules.get("patterns",[]):
                if re.search(pattern, text):
                    return action, min(0.85+(len(re.search(pattern,text).group())/max(len(text),1))*0.1, 0.98)

        return "chat", 0.30

    def _extract(self, user_input: str, action: str) -> Dict:
        text = user_input.strip()
        extracted = {}

        if action == "memory":
            content = text
            prefixes = ["帮我存一下","帮我存","帮我记一下","帮我记","记一下","记下","记住","保存","存储"]
            for p in sorted(prefixes, key=len, reverse=True):
                if text.startswith(p): content = text[len(p):].strip(); break
            content = re.sub(r'^(一下|一个)\s*','', content)
            # 数字分离前循环清前缀
            import re as _re
            clean = content.strip()
            for _ in range(3):
                new_clean = _re.sub(r'^(你|我|我的|帮我|帮我记|记一下|记|存|一下|一个|下|的)\s*','',clean)
                if new_clean == clean: break
                clean = new_clean
            # 分隔符
            for sep in ["是","=","为","：",":"]:
                if sep in clean:
                    k,v = clean.split(sep,1)
                    extracted["key"]=k.strip(); extracted["value"]=v.strip()
                    return extracted
            # 数字分离
            m = _re.search(r'^(.+?)(\d{2,})$', clean)
            if m:
                extracted["key"]=m.group(1).strip(); extracted["value"]=m.group(2).strip()
                return extracted
            if _re.match(r'^\d+$', clean): extracted["value"]=clean; return extracted
            if clean: extracted["key"]=clean
            return extracted

        if action == "identity":
            if "名字叫" in text:
                clean = text.replace("我的","").replace("名字叫","").strip()
                if clean: extracted["名字"]=clean; return extracted
            if text.startswith("我叫"): extracted["名字"]=text[len("我叫"):].strip()
            elif text.startswith("我是"): extracted["名字"]=text[len("我是"):].strip()
            return extracted

        if action == "recall":
            query = text
            for p in ["回忆","查询","查一下","找一下","搜索"]:
                if text.startswith(p): query=text[len(p):].strip(); break
            for kw in ["什么","哪些","哪里","怎么","如何","谁","我的","来着","呀","呢","吗"]:
                query=query.replace(kw,"")
            if "我叫" in text and ("什么" in text or "来着" in text): query="名字"
            query = re.sub(r'[？?！!。，,、\s]+','',query)
            extracted["query"]=query.strip() or "信息"
            return extracted

        if action == "code":
            for p in ["写","编写"]:
                if text.startswith(p): extracted["功能描述"]=text[len(p):].strip(); return extracted
            extracted["功能描述"]=text
            return extracted

        return extracted

    # ========== 上下文检索 ==========

    def _retrieve_context(self, action, extracted, user_input, user_id):
        context = {"补全":{}}
        bank = get_bank(user_id, "memory_agent_v4")

        needs_key = action=="memory" and not extracted.get("key")
        needs_value = action=="memory" and extracted.get("key") and not extracted.get("value")
        needs_query = action=="recall" and not extracted.get("query")
        needs_name = action=="identity" and not extracted.get("名字")

        # 读历史
        history = []
        raw = bank.recall("history", limit=10)
        if raw and "未找到" not in raw:
            try:
                for line in raw.split('\n'):
                    if line.strip():
                        try: history.append(json.loads(line.strip()))
                        except: pass
            except: pass

        if needs_key:
            for item in reversed(history[-5:]):
                if item.get("action") in ["memory","identity"]:
                    ext = item.get("extracted",{})
                    if ext.get("key"): context["补全"]["key"]=ext["key"]; break
                    if ext.get("名字"): context["补全"]["key"]=ext["名字"]; break

        if needs_value and extracted.get("key"):
            r = bank.recall(extracted["key"], limit=1)
            if r and "未找到" not in r and "{\"user\"" not in r: context["补全"]["value"]=r

        if needs_query:
            for item in reversed(history[-3:]):
                if item.get("action") in ["memory","identity"]:
                    ext = item.get("extracted",{})
                    if ext.get("key"): context["补全"]["query"]=ext["key"]; break
                    if ext.get("名字"): context["补全"]["query"]=ext["名字"]; break

        if needs_name:
            r = bank.recall("名字", limit=1)
            if r and "未找到" not in r and "{" not in r: context["补全"]["名字"]=r

        if action == "greeting":
            r = bank.recall("名字", limit=1)
            if r and "未找到" not in r and len(r)<30 and "{" not in r: context["user_name"]=r

        return context

    # ========== Agent路由 ==========

    def _infer_agents(self, action):
        """精确匹配 Agent + Skill 的 actions 字段"""
        agents = []
        skills = []
        try:
            for name, info in self._agent_capabilities.items():
                if action in info.get("actions", []):
                    if info.get("type") == "skill":
                        skills.append(name)
                    else:
                        agents.append(name)
        except:
            pass
        
        # 优先级
        priority = ["memory_agent", "chat_agent", "code_agent", "calculator_agent", "translate_agent"]
        agents.sort(key=lambda x: priority.index(x) if x in priority else 99)
        
        if agents:
            return agents[:1]
        if skills:
            self._last_extracted["_skill_name"] = skills[0]
            return ["executor_agent"]
        if not agents:
            agents = ["chat_agent"]
        
        # 学习优化：低成功率降级
        try:
            fb = Path("data/feedback.json")
            if fb.exists():
                data = json.loads(fb.read_text())
                failures = sum(1 for f in data.get("failure",[]) if f.get("action")==action)
                successes = sum(1 for f in data.get("success",[]) if f.get("action")==action)
                total = failures + successes
                if total > 3 and successes / total < 0.5:
                    return ["chat_agent"]
        except:
            pass
        
        return agents[:1]  # 返回最佳匹配

    def _execute_single(self, agent_name: str, user_input: str, user_id: str, context_data: Dict = None) -> Dict:
        agent = self._get_agent(agent_name, user_id)
        if not agent:
            return {"success": False, "response": f"Agent不可用"}

        ctx = {
            "user_id": user_id,
            "action": self._last_action,
            "extracted": self._last_extracted,
            "pre_fetched": context_data.get("补全", {}).get("pre_fetched", []) if context_data else [], # ✅ 传递预检索结果
        }

        try:
            if hasattr(agent, 'process'):
                return agent.process(user_input, ctx)
        except Exception as e:
            return {"success": False, "response": str(e)}
        return {"success": False, "response": "无可用方法"}


    def _get_agent(self, agent_name, user_id):
        k = f"{agent_name}:{user_id}"
        if k in self._agent_cache: return self._agent_cache[k]
        a = agent_pool.get(agent_name, user_id)
        if not a:
            try:
                from core.agents.wisdom.wisdom_factory import wisdom_factory
                a = wisdom_factory.get_agent(agent_name, user_id)
            except: pass
        if a: self._agent_cache[k] = a
        return a

    # ========== 回复生成 ==========

    def _generate_reply(self, user_input, action, extracted, context, user_id, agent_result=None):
        if agent_result and agent_result.get("success") and agent_result.get("response"):
            raw = str(agent_result.get("response"))
            if '{"user"' not in raw and '{"assistant"' not in raw:
                return raw

        ctx_parts = []
        if context.get("补全"): ctx_parts.append(f"系统补全:{json.dumps(context['补全'],ensure_ascii=False)}")
        if context.get("user_name"): ctx_parts.append(f"用户名字:{context['user_name']}")
        ctx_text = " | ".join(ctx_parts)

        prompt = f"""你是ClawsJoy本地AI系统。
{ctx_text}
用户: {user_input}
意图: {action}
回复:"""

        # 预热 LLM（首次加载慢）
        try:
            llm_client.generate("ready", model=MODEL_MAIN, max_tokens=5, task_type="reply", timeout=30)
        except:
            pass

        try:
            resp = llm_client.generate(f"用户说：{user_input}\n请简短回复。", model=MODEL_MAIN, max_tokens=200, task_type="reply", timeout=10)
            if resp and len(resp.strip())>2: return resp.strip()
        except: pass

        return self._fallback(action, extracted, context)

    def _fallback(self, action, extracted, context):
        if action=="greeting": return "你好！我是ClawsJoy。"
        if action=="memory":
            k = extracted.get("key","信息"); v = extracted.get("value") or context.get("补全",{}).get("value","")
            return f"已记住{k}" + (f"={v}" if v else "")
        if action=="chat": return "我在，请继续。";
        if action=="identity":
            n = extracted.get("名字") or context.get("补全",{}).get("名字","")
            return f"你好，{n}！" if n else "好的。"
        if action=="chat": return "好的，请继续。"
        if action=="recall": return f"查一下{extracted.get('query','信息')}..."
        return "好的。"

    # ========== 学习 ==========

    def _learn(self, user_input, action, extracted, response, latency_ms, user_id):
        # 决策反馈记录
        try:
            feedback_file = Path("data/feedback.json")
            existing = json.loads(feedback_file.read_text()) if feedback_file.exists() else {"success": [], "failure": []}
            cat = "success" if latency_ms < 5000 else "failure"
            existing[cat].append({"user_id": user_id, "action": action, "input": user_input[:100], "latency_ms": latency_ms, "time": datetime.now().isoformat()})
            feedback_file.write_text(json.dumps(existing, indent=2))
        except:
            pass

        bank = get_bank(user_id, "memory_agent_v4")
        vbank = get_vector_bank(user_id)
        growth = get_growth(user_id)
        ctx_mgr = get_context(user_id)

        entry = {"user":user_input[:300],"assistant":response[:300],"action":action,"extracted":extracted,"ts":datetime.now().isoformat()}
        with open(Path(f"data/users/{user_id}/history.jsonl"), "a") as f: f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        ctx_mgr.add_turn(user_input, response, action, extracted)
        if extracted:
            for k,v in extracted.items():
                if v and len(str(v))<100: ctx_mgr.update_entity(k, str(v))
            vbank.remember(action, user_input[:200], json.dumps({"input":user_input[:200],"extracted":extracted,"response":response[:200]}, ensure_ascii=False))
        growth.grow(user_input, {"action":action,"extracted":extracted}, response)

    def get_learning_stats(self, user_id: str = None) -> Dict:
        """查询学习数据"""
        feedback_file = Path("data/feedback.json")
        if feedback_file.exists():
            data = json.loads(feedback_file.read_text())
            return {
                "total": len(data.get("success", [])) + len(data.get("failure", [])),
                "success_rate": round(len(data.get("success", [])) / max(len(data.get("success", [])) + len(data.get("failure", [])), 1) * 100, 1)
            }
        return {"total": 0, "success_rate": 0}

    def _load_agent_capabilities(self) -> Dict:
        """从配置加载 Agent + Skill 能力声明"""
        caps = {}
        import yaml
        
        # Agent 能力声明
        cap_dir = Path("config/agents/capabilities")
        if cap_dir.exists():
            for f in cap_dir.glob("*.yaml"):
                try:
                    data = yaml.safe_load(f.read_text())
                    agent = data.get("agent", data)
                    name = agent.get("name", f.stem)
                    actions = agent.get("actions", [])
                    for cap in agent.get("capabilities", []):
                        if isinstance(cap, dict):
                            actions.append(cap.get("name", ""))
                        elif isinstance(cap, str):
                            actions.append(cap)
                    if actions:
                        caps[name] = {"type": "agent", "actions": actions}
                except:
                    pass
        
        # Skill 能力声明（和 Agent 同样的加载方式）
        skill_cap_dir = Path("config/capabilities/skills")
        if skill_cap_dir.exists():
            for f in skill_cap_dir.glob("*.yaml"):
                try:
                    data = yaml.safe_load(f.read_text())
                    name = data.get("name", f.stem)
                    actions = data.get("actions", [])
                    if actions:
                        caps[name] = {"type": "skill", "actions": actions}
                except:
                    pass
        
        return caps

    def get_stats(self):
        stats = {**self._stats}
        stats["cached_agents"] = len(self._agent_cache)
        stats["success_rate"] = round(stats["success"]/max(stats["total"],1)*100, 1)
        stats["agents"] = {}
        for k in self._agent_cache:
            name = k.split(":")[0]
            stats["agents"][name] = stats["agents"].get(name, 0) + 1
        return stats
    def clear_cache(self): self._agent_cache.clear()


agent_cortex = AgentCortex()
