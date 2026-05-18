"""智能报告生成器 - 查询记忆并生成报告"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from pptx import Presentation
from datetime import datetime
import os

class SmartReportSkill:
    name = "smart_report"
    description = "智能报告生成器"
    version = "1.0.0"
    category = "document"

    def execute(self, params):
        topic = params.get("topic", "系统报告")
        content = params.get("content", [])
        output_path = params.get("output", f"output/smart_report_{int(datetime.now().timestamp())}.pptx")
        
        prs = Presentation()
        
        # 封面
        slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = topic
        slide.placeholders[1].text = f"ClawsJoy AI 智能生成\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 内容页
        for i, item in enumerate(content):
            slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(slide_layout)
            slide.shapes.title.text = item.get('title', f'第{i+1}部分')
            slide.placeholders[1].text = item.get('content', '')[:600]
        
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        prs.save(output_path)
        
        return {"success": True, "output": output_path, "pages": len(content) + 1}

skill = SmartReportSkill()
