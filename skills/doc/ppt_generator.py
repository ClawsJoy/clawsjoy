"""PPT 生成技能 - 带模板和背景图"""
import sys
import os
import random
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from datetime import datetime
from lib.memory_vector import VectorMemory

class PPTGeneratorSkill:
    name = "ppt_generator"
    description = "生成带模板和背景的 PowerPoint 演示文稿"
    version = "2.0.0"
    category = "document"

    # 模板配色方案
    THEMES = {
        "default": {
            "bg_color": RGBColor(245, 245, 245),
            "title_color": RGBColor(33, 33, 33),
            "text_color": RGBColor(66, 66, 66),
            "accent_color": RGBColor(25, 118, 210)
        },
        "dark": {
            "bg_color": RGBColor(30, 30, 30),
            "title_color": RGBColor(255, 255, 255),
            "text_color": RGBColor(200, 200, 200),
            "accent_color": RGBColor(100, 200, 255)
        },
        "business": {
            "bg_color": RGBColor(240, 248, 255),
            "title_color": RGBColor(0, 51, 102),
            "text_color": RGBColor(51, 51, 51),
            "accent_color": RGBColor(0, 102, 204)
        }
    }

    def execute(self, params):
        title = params.get("title", "ClawsJoy 分析报告")
        content = params.get("content", [])
        theme_name = params.get("theme", "business")
        query_memory = params.get("query_memory", True)
        
        # 获取主题
        theme = self.THEMES.get(theme_name, self.THEMES["business"])
        
        # 如果启用记忆查询且内容为空，自动查询
        if query_memory and not content:
            vm = VectorMemory()
            results = vm.search(title, n=12)
            for r in results:
                content.append({
                    "title": r['metadata'].get('category', '信息'),
                    "content": r['text'][:400]
                })
        
        output_dir = "str(smart_config.ROOT)/output"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rand = random.randint(1000, 9999)
        output_path = os.path.join(output_dir, f"report_{timestamp}_{rand}.pptx")
        
        prs = Presentation()
        
        # 设置幻灯片尺寸（16:9）
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(5.625)
        
        # 封面页
        slide_layout = prs.slide_layouts[6]  # 空白布局
        slide = prs.slides.add_slide(slide_layout)
        
        # 背景色
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = theme["bg_color"]
        
        # 标题
        title_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(1.5))
        title_frame = title_box.text_frame
        title_frame.text = title
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(44)
        title_para.font.bold = True
        title_para.font.color.rgb = theme["title_color"]
        title_para.alignment = PP_ALIGN.CENTER
        
        # 副标题
        subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(3), Inches(8), Inches(1))
        subtitle_frame = subtitle_box.text_frame
        subtitle_frame.text = f"ClawsJoy AI 智能报告\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        sub_para = subtitle_frame.paragraphs[0]
        sub_para.font.size = Pt(18)
        sub_para.font.color.rgb = theme["text_color"]
        sub_para.alignment = PP_ALIGN.CENTER
        
        # 目录页
        if content:
            slide = prs.slides.add_slide(slide_layout)
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = theme["bg_color"]
            
            # 目录标题
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.8))
            title_frame = title_box.text_frame
            title_frame.text = "目录"
            title_para = title_frame.paragraphs[0]
            title_para.font.size = Pt(32)
            title_para.font.bold = True
            title_para.font.color.rgb = theme["title_color"]
            
            # 目录内容
            toc_text = "\n".join([f"{i+1}. {item.get('title', f'第{i+1}部分')}" for i, item in enumerate(content[:8])])
            content_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(3.5))
            content_frame = content_box.text_frame
            content_frame.text = toc_text
            for para in content_frame.paragraphs:
                para.font.size = Pt(20)
                para.font.color.rgb = theme["text_color"]
        
        # 内容页
        for i, item in enumerate(content[:10]):
            slide = prs.slides.add_slide(slide_layout)
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = theme["bg_color"]
            
            # 页面标题
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.8))
            title_frame = title_box.text_frame
            title_frame.text = item.get('title', f'第{i+1}部分')
            title_para = title_frame.paragraphs[0]
            title_para.font.size = Pt(28)
            title_para.font.bold = True
            title_para.font.color.rgb = theme["title_color"]
            
            # 分隔线
            line = slide.shapes.add_shape(1, Inches(0.5), Inches(1.3), Inches(9), Inches(0.02))
            line.fill.solid()
            line.fill.fore_color.rgb = theme["accent_color"]
            
            # 内容
            content_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(8.6), Inches(3.5))
            content_frame = content_box.text_frame
            content_frame.text = item.get('content', '无内容')[:600]
            for para in content_frame.paragraphs:
                para.font.size = Pt(16)
                para.font.color.rgb = theme["text_color"]
        
        # 总结页
        slide = prs.slides.add_slide(slide_layout)
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = theme["bg_color"]
        
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.8))
        title_frame = title_box.text_frame
        title_frame.text = "总结"
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(32)
        title_para.font.bold = True
        title_para.font.color.rgb = theme["title_color"]
        
        summary_text = f"本报告由 ClawsJoy AI 自动生成\n\n总页数: {len(prs.slides)}\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n数据来源: 向量记忆库\n\nClawsJoy 3.0 - 智能大脑调度系统"
        content_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(8.6), Inches(3.5))
        content_frame = content_box.text_frame
        content_frame.text = summary_text
        for para in content_frame.paragraphs:
            para.font.size = Pt(18)
            para.font.color.rgb = theme["text_color"]
            para.alignment = PP_ALIGN.CENTER
        
        prs.save(output_path)
        
        return {"success": True, "output": output_path, "pages": len(prs.slides), "title": title, "theme": theme_name}

skill = PPTGeneratorSkill()
