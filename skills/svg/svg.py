"""SVG 图表生成技能"""
import json

class SVGGenerator:
    """SVG 图表生成器"""
    
    def execute(self, params):
        """生成 SVG 图表"""
        chart_type = params.get('type', 'bar')
        title = params.get('title', 'ClawsJoy 图表')
        data = params.get('data', [10, 20, 30, 40, 50])
        labels = params.get('labels', ['A', 'B', 'C', 'D', 'E'])
        
        if chart_type == 'bar':
            bar_width = 50
            max_height = 200
            svg = f'''<svg width="500" height="300" xmlns="http://www.w3.org/2000/svg">
    <rect width="500" height="300" fill="#f5f5f5" rx="10"/>
    <text x="250" y="30" text-anchor="middle" font-size="20" font-weight="bold" fill="#333">{title}</text>'''
            
            for i, (label, value) in enumerate(zip(labels, data)):
                x = 60 + i * 80
                height = (value / max(data)) * max_height if max(data) > 0 else 50
                y = 260 - height
                svg += f'''
    <rect x="{x}" y="{y}" width="{bar_width}" height="{height}" fill="#4CAF50" rx="5"/>
    <text x="{x + bar_width/2}" y="280" text-anchor="middle" font-size="12" fill="#333">{label}</text>
    <text x="{x + bar_width/2}" y="{y - 5}" text-anchor="middle" font-size="11" fill="#666">{value}</text>'''
            
            svg += '\n</svg>'
        else:
            svg = f'<svg width="500" height="300"><text x="250" y="150" text-anchor="middle">Unsupported chart type: {chart_type}</text></svg>'
        
        return {"svg": svg, "success": True, "type": chart_type}


skill = SVGGenerator()
