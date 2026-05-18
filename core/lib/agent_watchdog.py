#!/usr/bin/env python3
"""Agent 看门狗 - 配置驱动版（修复启动缓冲期）"""

import os
import time
import yaml
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict

class AgentWatchdog:
    VERSION = "1.0.1"
    
    DEFAULT_CONFIG = {
        "check_interval": 60,
        "heartbeat_timeout": 120,
        "startup_grace_period": 30,  # 新增：启动缓冲期（秒）
        "auto_restart": True,
        "max_restart_attempts": 5,
        "restart_cooldown": 30,
        "monitored_agents": ["decision_agent", "chat_agent", "executor_agent", "collector_agent"]
    }
    
    AGENTS = {
        "decision_agent": {"script": "agents/decision_agent_v3.py"},
        "chat_agent": {"script": "agents/chat_agent.py"},
        "executor_agent": {"script": "agents/executor_agent.py"},
        "collector_agent": {"script": "agents/collector_agent.py"},
    }
    
    def __init__(self):
        self.processes = {}
        self.restart_counts = {}
        self.heartbeats = {}
        self.start_times = {}  # 记录启动时间
        self.running = False
        
        self.log_file = Path("logs/watchdog.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._load_config()
    
    def _load_config(self):
        config_file = Path("config/driver/watchdog.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.check_interval = config.get('check_interval', self.DEFAULT_CONFIG['check_interval'])
                self.heartbeat_timeout = config.get('heartbeat_timeout', self.DEFAULT_CONFIG['heartbeat_timeout'])
                self.startup_grace_period = config.get('startup_grace_period', self.DEFAULT_CONFIG['startup_grace_period'])
                self.auto_restart = config.get('auto_restart', self.DEFAULT_CONFIG['auto_restart'])
                self.max_restart_attempts = config.get('max_restart_attempts', self.DEFAULT_CONFIG['max_restart_attempts'])
                self.restart_cooldown = config.get('restart_cooldown', self.DEFAULT_CONFIG['restart_cooldown'])
                self.monitored_agents = config.get('monitored_agents', self.DEFAULT_CONFIG['monitored_agents'])
        else:
            self.check_interval = self.DEFAULT_CONFIG['check_interval']
            self.heartbeat_timeout = self.DEFAULT_CONFIG['heartbeat_timeout']
            self.startup_grace_period = self.DEFAULT_CONFIG['startup_grace_period']
            self.auto_restart = self.DEFAULT_CONFIG['auto_restart']
            self.max_restart_attempts = self.DEFAULT_CONFIG['max_restart_attempts']
            self.restart_cooldown = self.DEFAULT_CONFIG['restart_cooldown']
            self.monitored_agents = self.DEFAULT_CONFIG['monitored_agents']
        
        self._log(f"📋 配置加载: 检查间隔={self.check_interval}s, 心跳超时={self.heartbeat_timeout}s, 启动缓冲={self.startup_grace_period}s")
    
    def _log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"[{timestamp}] {message}")
    
    def heartbeat(self, agent_name: str):
        """Agent 主动发送心跳"""
        self.heartbeats[agent_name] = datetime.now()
        self._log(f"💓 心跳: {agent_name}")
    
    def is_in_grace_period(self, name: str) -> bool:
        """检查是否还在启动缓冲期内"""
        start_time = self.start_times.get(name)
        if not start_time:
            return False
        return (datetime.now() - start_time).seconds < self.startup_grace_period
    
    def check_heartbeat(self, name: str) -> bool:
        """检查心跳是否超时"""
        # 缓冲期内不检查心跳
        if self.is_in_grace_period(name):
            return True
        
        last = self.heartbeats.get(name)
        if not last:
            return False
        return (datetime.now() - last).seconds < self.heartbeat_timeout
    
    def start_agent(self, name: str, config: dict) -> bool:
        script_path = Path(config["script"])
        if not script_path.exists():
            self._log(f"❌ 脚本不存在: {script_path}")
            return False
        
        if self.restart_counts.get(name, 0) >= self.max_restart_attempts:
            self._log(f"⚠️ Agent {name} 重启次数已达上限 {self.max_restart_attempts}，停止尝试")
            return False
        
        try:
            proc = subprocess.Popen(
                ["python3", str(script_path)],
                cwd="/mnt/d/clawsjoy_clean",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.processes[name] = proc
            self.start_times[name] = datetime.now()  # 记录启动时间
            self.restart_counts[name] = self.restart_counts.get(name, 0) + 1
            self._log(f"✅ 启动 Agent: {name} (PID: {proc.pid}, 重启次数: {self.restart_counts[name]})")
            return True
        except Exception as e:
            self._log(f"❌ 启动失败 {name}: {e}")
            return False
    
    def stop_agent(self, name: str):
        if name in self.processes:
            proc = self.processes[name]
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            del self.processes[name]
            if name in self.start_times:
                del self.start_times[name]
            self._log(f"🛑 停止 Agent: {name}")
    
    def check_agent(self, name: str) -> bool:
        if name not in self.processes:
            return False
        return self.processes[name].poll() is None
    
    def restart_agent(self, name: str):
        if not self.auto_restart:
            self._log(f"⚠️ 自动重启已禁用，跳过 {name}")
            return
        
        self.stop_agent(name)
        time.sleep(self.restart_cooldown)
        self.start_agent(name, self.AGENTS[name])
    
    def start_all(self):
        self._log(f"🚀 启动所有 Agent... (缓冲期: {self.startup_grace_period}s)")
        for name in self.monitored_agents:
            if name in self.AGENTS:
                self.start_agent(name, self.AGENTS[name])
    
    def stop_all(self):
        self._log("🛑 停止所有 Agent...")
        for name in list(self.processes.keys()):
            self.stop_agent(name)
    
    def monitor(self):
        self.running = True
        self._log(f"👁️ 看门狗监控启动 (间隔: {self.check_interval}s)")
        
        while self.running:
            for name in self.monitored_agents:
                if name not in self.AGENTS:
                    continue
                
                # 检查进程是否存在
                if not self.check_agent(name):
                    self._log(f"⚠️ Agent {name} 进程消失，正在重启...")
                    self.restart_agent(name)
                # 检查心跳（缓冲期内自动跳过）
                elif not self.check_heartbeat(name):
                    self._log(f"⚠️ Agent {name} 心跳超时 ({self.heartbeat_timeout}s)，正在重启...")
                    self.restart_agent(name)
            
            time.sleep(self.check_interval)
    
    def start_monitor(self):
        thread = threading.Thread(target=self.monitor, daemon=True)
        thread.start()
        return thread


watchdog = AgentWatchdog()


if __name__ == "__main__":
    print(f"Agent 看门狗 v{watchdog.VERSION}")
    watchdog.start_all()
    watchdog.start_monitor()
    print("按 Ctrl+C 停止...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watchdog.stop_all()
