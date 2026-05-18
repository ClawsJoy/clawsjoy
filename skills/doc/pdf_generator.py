"""PDF 生成技能"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import os

class PDFGeneratorSkill:
    name = "pdf_generator"
    description = "生成 PDF 文档"
    version = "1.0.0"
    category = "document"

    def execute(self, params):
        title = params.get("title", "ClawsJoy 报告")
        content = params.get("content", [])
        output_path = params.get("output", f"output/report_{int(datetime.now().timestamp())}.pdf")
        
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # 标题
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 内容
        for item in content:
            story.append(Paragraph(f"<b>{item.get('title', '')}</b>", styles['Heading2']))
            story.append(Spacer(1, 6))
            story.append(Paragraph(item.get('content', ''), styles['Normal']))
            story.append(Spacer(1, 12))
        
        doc.build(story)
        
        return {"success": True, "output": output_path}

skill = PDFGeneratorSkill()
