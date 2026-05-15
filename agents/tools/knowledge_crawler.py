#!/usr/bin/env python3
"""知识采集 Agent - 从官方网站自动采集专业知识"""

import re
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

class KnowledgeCrawler:
    def __init__(self):
        self.knowledge_dir = Path("/mnt/d/clawsjoy/knowledge/collected")
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # 官方知识源
        self.sources = {
            "pm2": {
                "url": "https://pm2.keymetrics.io/docs/usage/quick-start/",
                "type": "process_manager",
                "selector": ".content"
            },
            "docker": {
                "url": "https://docs.docker.com/get-started/overview/",
                "type": "container",
                "selector": ".article-content"
            },
            "python_import": {
                "url": "https://docs.python.org/3/tutorial/modules.html",
                "type": "language",
                "selector": ".section"
            },
            "ffmpeg": {
                "url": "https://ffmpeg.org/documentation.html",
                "type": "video_tool",
                "selector": "body"
            },
            "systemd": {
                "url": "https://www.freedesktop.org/software/systemd/man/latest/systemctl.html",
                "type": "system",
                "selector": "main"
            }
        }
    
    def fetch_knowledge(self, name, config):
        """采集知识"""
        url = config["url"]
        try:
            print(f"📚 采集知识: {name} from {url}")
            resp = requests.get(url, timeout=30, headers={'User-Agent': 'ClawsJoy/1.0'})
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # 提取关键内容
                content = self._extract_content(soup, config.get("selector", "body"))
                
                # 保存到文件
                filename = self.knowledge_dir / f"{name}.md"
                with open(filename, 'w') as f:
                    f.write(f"# {name.upper()} 官方知识\n")
                    f.write(f"来源: {url}\n")
                    f.write(f"采集时间: {__import__('time').ctime()}\n\n")
                    f.write(content[:5000])  # 保存前5000字符
                
                print(f"✅ 已采集 {name}: {len(content)} 字符")
                return True
            else:
                print(f"❌ 采集失败 {name}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"❌ 采集失败 {name}: {e}")
        return False
    
    def _extract_content(self, soup, selector):
        """提取内容"""
        content = ""
        for tag in soup.select(selector):
            text = tag.get_text()
            # 提取关键段落
            lines = text.split('\n')
            for line in lines:
                if any(kw in line.lower() for kw in ['command', 'example', 'error', 'fix', 'solution']):
                    content += line.strip() + "\n"
        return content[:5000]
    
    def learn_all(self):
        """学习所有知识源"""
        success = 0
        for name, config in self.sources.items():
            if self.fetch_knowledge(name, config):
                success += 1
            time.sleep(2)  # 礼貌延迟
        
        print(f"\n📚 学习完成: {success}/{len(self.sources)} 个知识源")
        return success
    
    def extract_useful_commands(self):
        """从采集的知识中提取有用命令"""
        all_commands = []
        for file in self.knowledge_dir.glob("*.md"):
            with open(file) as f:
                content = f.read()
            
            # 提取命令行
            commands = re.findall(r'^\s*[\$\#]\s*(.+?)$', content, re.MULTILINE)
            all_commands.extend(commands[:20])
        
        # 保存命令库
        cmd_file = self.knowledge_dir / "useful_commands.json"
        import json
        with open(cmd_file, 'w') as f:
            json.dump(all_commands, f, indent=2)
        
        print(f"📚 提取了 {len(all_commands)} 个有用命令")
        return all_commands

if __name__ == "__main__":
    crawler = KnowledgeCrawler()
    crawler.learn_all()
    crawler.extract_useful_commands()
