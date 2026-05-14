#!/usr/bin/env python3
"""内容生产技能链"""

import json
import sys
from datetime import datetime
from typing import Dict

sys.path.insert(0, '/mnt/d/clawsjoy')

from skills.content.content_collector import content_collector
from skills.content.script_writer import script_writer
from skills.video.video_maker import video_maker
from skills.publish.video_publisher import video_publisher

class ContentWorkflow:
    def __init__(self):
        self.history = []
    
    def run_full_workflow(self, topic: str, style: str = "科普", platform: str = "youtube") -> Dict:
        results = {}
        
        # Step 1: 采集
        print(f"📡 采集: {topic}")
        collect_result = content_collector.execute({'action': 'search', 'keyword': topic})
        results['collect'] = collect_result
        
        # Step 2: 生成脚本
        print(f"✍️ 生成脚本: {topic}")
        script_result = script_writer.execute({'action': 'generate', 'topic': topic, 'style': style})
        results['script'] = script_result
        
        # Step 3: 制作视频
        print(f"🎬 制作视频")
        video_result = video_maker.execute({'action': 'create'})
        results['video'] = video_result
        
        # Step 4: 发布
        print(f"📤 发布到 {platform}")
        publish_result = video_publisher.execute({'action': 'publish', 'platform': platform})
        results['publish'] = publish_result
        
        self.history.append({'topic': topic, 'timestamp': datetime.now().isoformat()})
        
        return {'success': True, 'workflow': results}
    
    def get_status(self) -> Dict:
        return {'total_workflows': len(self.history), 'recent': self.history[-3:] if self.history else []}

content_workflow = ContentWorkflow()
