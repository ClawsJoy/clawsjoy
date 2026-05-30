"""智能主动服务 - 事件驱动 + 条件触发"""

import threading
import time
from typing import Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass
class Condition:
    """触发条件"""
    name: str
    check: Callable[[Dict], bool]
    action: Callable[[Dict], None]
    cooldown: int = 300  # 冷却时间（秒）


class ActiveService:
    """智能主动服务"""
    
    def __init__(self):
        self.conditions: List[Condition] = []
        self.last_trigger: Dict[str, float] = {}
        self.user_context: Dict[str, Dict] = {}
        self.running = False
        self.thread = None
        self._load_context()
    
    def _load_context(self):
        """加载用户上下文"""
        context_file = Path(f"{config_helper.get_data_root()}/v5/active_context.json")
        if context_file.exists():
            try:
                with open(context_file, 'r') as f:
                    self.user_context = json.load(f)
            except:
                pass
    
    def _save_context(self):
        """保存用户上下文"""
        context_file = Path(f"{config_helper.get_data_root()}/v5/active_context.json")
        context_file.parent.mkdir(parents=True, exist_ok=True)
        with open(context_file, 'w') as f:
            json.dump(self.user_context, f, indent=2)
    
    def register_condition(self, name: str, check_func: Callable, action_func: Callable, cooldown: int = 300):
        """注册触发条件"""
        self.conditions.append(Condition(name, check_func, action_func, cooldown))
        print(f"   ✅ 注册主动条件: {name}")
    
    def update_context(self, user_id: str, key: str, value):
        """更新用户上下文"""
        if user_id not in self.user_context:
            self.user_context[user_id] = {"last_active": time.time()}
        self.user_context[user_id][key] = value
        self.user_context[user_id]["last_active"] = time.time()
        self._save_context()
    
    def get_context(self, user_id: str) -> Dict:
        """获取用户上下文"""
        return self.user_context.get(user_id, {"last_active": time.time()})
    
    def start(self):
        """启动主动服务"""
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("🧠 智能主动服务已启动")
    
    def _run(self):
        while self.running:
            now = time.time()
            for condition in self.conditions:
                # 检查冷却
                last = self.last_trigger.get(condition.name, 0)
                if now - last < condition.cooldown:
                    continue
                
                # 检查条件
                try:
                    if condition.check(self.user_context):
                        condition.action(self.user_context)
                        self.last_trigger[condition.name] = now
                except Exception as e:
                    print(f"主动服务错误: {condition.name} - {e}")

            time.sleep(10)  # 每10秒检查一次
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)


# 全局实例
active_service = ActiveService()


# ========== 内置主动条件 ==========

def init_default_conditions(butler_callback=None):
    """初始化默认主动条件"""
    
    # 条件1: 空闲提醒
    def idle_check(context):
        for user_id, ctx in context.items():
            last_active = ctx.get("last_active", 0)
            idle_time = time.time() - last_active
            todos = ctx.get("todos", 0)
            if idle_time > 1800 and todos > 0:  # 30分钟 + 有待办
                return True
        return False
    
    def idle_action(context):
        for user_id, ctx in context.items():
            last_active = ctx.get("last_active", 0)
            idle_time = time.time() - last_active
            todos = ctx.get("todos", 0)
            if idle_time > 1800 and todos > 0:
                print(f"\n💡 [主动提醒] {user_id}: 您有 {todos} 个待办事项，需要处理吗？")
                if butler_callback:
                    butler_callback(user_id, f"您有 {todos} 个待办事项未完成")
    
    # 条件2: 早安问候
    def morning_check(context):
        hour = datetime.now().hour
        return 8 <= hour <= 10
    
    def morning_action(context):
        print(f"\n🌅 [主动问候] 早安！新的一天开始了~")
        if butler_callback:
            butler_callback("default", "早安！新的一天开始了~")
    
    # 注册条件
    active_service.register_condition("idle_reminder", idle_check, idle_action, cooldown=3600)
    active_service.register_condition("morning_greeting", morning_check, morning_action, cooldout=86400)
    
    print("   ✅ 默认主动条件已注册")


# 启动主动服务
active_service.start()
init_default_conditions()
