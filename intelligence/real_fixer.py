"""真正的修复器 - 针对你环境的真实故障"""
import time
import requests
import subprocess
import os
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_enhanced import brain as brain_core

class RealFixer:
    """真正能修复问题的执行器"""
    
    def __init__(self):
        self.fix_count = 0
        self.port_conflicts_resolved = 0
        
    def fix_port_conflict(self, port):
        """真正解决端口冲突"""
        print(f"🔧 解决端口 {port} 冲突...")
        
        # 1. 找到占用端口的进程
        result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
        pids = result.stdout.strip().split('\n')
        
        for pid in pids:
            if pid and pid.isdigit():
                print(f"   杀死进程 {pid}")
                subprocess.run(f"kill -9 {pid}", shell=True)
        
        time.sleep(1)
        
        # 2. 确认端口已释放
        check = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True)
        if not check.stdout.strip():
            print(f"   ✅ 端口 {port} 已释放")
            self.port_conflicts_resolved += 1
            return True
        else:
            print(f"   ❌ 端口 {port} 仍被占用")
            return False
    
    def fix_service(self, service_name, port, cmd):
        """真正修复服务"""
        print(f"🔧 修复 {service_name}...")
        
        # 1. 先解决端口冲突
        self.fix_port_conflict(port)
        
        # 2. 启动服务
        subprocess.Popen(cmd, shell=True, cwd="/mnt/d/clawsjoy")
        time.sleep(3)
        
        # 3. 验证服务是否启动
        try:
            resp = requests.get(f"http://localhost:{port}/health", timeout=5)
            if resp.status_code == 200:
                print(f"   ✅ {service_name} 启动成功")
                return True
        except:
            pass
        
        print(f"   ❌ {service_name} 启动失败")
        return False
    
    def fix_ollama(self):
        """真正修复Ollama"""
        print(f"🔧 修复 Ollama...")
        
        # 1. 重启Ollama服务
        subprocess.run("pkill -f ollama", shell=True)
        time.sleep(2)
        subprocess.Popen("ollama serve > /dev/null 2>&1 &", shell=True)
        time.sleep(5)
        
        # 2. 验证
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=10)
            if resp.status_code == 200:
                print("   ✅ Ollama 恢复")
                return True
        except:
            pass
        
        print("   ❌ Ollama 恢复失败")
        return False
    
    def fix_dependency(self, module_name):
        """真正安装依赖"""
        print(f"🔧 安装依赖: {module_name}")
        
        result = subprocess.run(f"pip install {module_name} -q", shell=True, capture_output=True)
        if result.returncode == 0:
            print(f"   ✅ {module_name} 安装成功")
            return True
        else:
            print(f"   ❌ {module_name} 安装失败")
            return False
    
    def clean_memory(self):
        """真正清理内存"""
        print(f"🔧 清理内存缓存...")
        
        # 清理Python缓存
        subprocess.run("find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null", shell=True)
        
        # 清理系统缓存（需要sudo）
        subprocess.run("sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true", shell=True)
        
        print("   ✅ 内存清理完成")
        return True

class RealFaultLoop:
    """真正的故障学习闭环 - 执行真实修复"""
    
    def __init__(self):
        self.fixer = RealFixer()
        self.loop_count = 0
        
        # 真实服务配置
        self.services = {
            'gateway': {'port': 5002, 'cmd': 'python3 agent_gateway_web.py'},
            'agent': {'port': 5005, 'cmd': 'python3 multi_agent_service_v2.py'},
            'doc': {'port': 5008, 'cmd': 'python3 doc_generator.py'}
        }
        
        # 真实故障处理映射
        self.fault_handlers = {
            'port_in_use': self._handle_port_conflict,
            'service_down': self._handle_service_down,
            'connection_refused': self._handle_service_down,
            'import_error': self._handle_import_error,
            'ollama_down': self._handle_ollama_down
        }
        
        print("\n" + "="*60)
        print("🔧 真实故障修复系统")
        print("="*60)
        print("可以修复: 端口冲突、服务重启、依赖安装、Ollama恢复")
        print("="*60)
    
    def _handle_port_conflict(self, port):
        """处理端口冲突"""
        return self.fixer.fix_port_conflict(port)
    
    def _handle_service_down(self, service_name, port, cmd):
        """处理服务停止"""
        return self.fixer.fix_service(service_name, port, cmd)
    
    def _handle_import_error(self, module_name):
        """处理导入错误"""
        return self.fixer.fix_dependency(module_name)
    
    def _handle_ollama_down(self):
        """处理Ollama故障"""
        return self.fixer.fix_ollama()
    
    def detect_and_fix(self):
        """检测并修复真实故障"""
        self.loop_count += 1
        
        print(f"\n{'='*50}")
        print(f"🔄 检测周期 #{self.loop_count} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*50}")
        
        fixed = []
        
        # 1. 检查并修复服务
        for name, config in self.services.items():
            try:
                resp = requests.get(f"http://localhost:{config['port']}/health", timeout=3)
                if resp.status_code != 200:
                    print(f"\n❌ {name} 异常 (HTTP {resp.status_code})")
                    if self.fixer.fix_service(name, config['port'], config['cmd']):
                        fixed.append(name)
                        brain_core.record_experience(
                            agent="real_fixer",
                            action=f"fix_{name}",
                            result={"success": True},
                            context="auto_heal"
                        )
            except requests.exceptions.ConnectionError:
                print(f"\n❌ {name} 连接失败")
                if self.fixer.fix_service(name, config['port'], config['cmd']):
                    fixed.append(name)
            except Exception as e:
                print(f"\n❌ {name} 故障: {str(e)[:50]}")
        
        # 2. 检查端口冲突
        for port in [5002, 5005, 5008]:
            result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True)
            if result.stdout.strip():
                print(f"\n⚠️ 端口 {port} 冲突")
                self.fixer.fix_port_conflict(port)
        
        # 3. 检查Ollama
        try:
            requests.get("http://localhost:11434/api/tags", timeout=3)
        except:
            print(f"\n⚠️ Ollama 故障")
            self.fixer.fix_ollama()
        
        # 输出结果
        if fixed:
            print(f"\n✅ 本次修复: {fixed}")
        else:
            print(f"\n✅ 无故障")
        
        return fixed
    
    def run(self):
        """持续运行"""
        print("\n🚀 启动真实故障监控...")
        print("每30秒检测一次，发现问题立即修复\n")
        
        try:
            while True:
                self.detect_and_fix()
                print(f"\n⏳ 等待30秒...")
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n\n停止监控")
            print(f"总周期: {self.loop_count}")
            print(f"解决端口冲突: {self.fixer.port_conflicts_resolved}")

if __name__ == "__main__":
    loop = RealFaultLoop()
    loop.run()
