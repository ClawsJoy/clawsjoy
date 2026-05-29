from lib.smart_config import smart_config
"""十六进制颜色转RGB"""

class HexToRgbSkill:
    name = "hex_to_rgb"
    description = "将十六进制颜色代码转换为RGB值"
    version = "1.0.0"
    category = "color"
    
    def execute(self, params):
        hex_color = params.get("hex", "")
        if not hex_color:
            return {"success": False, "error": "需要提供十六进制颜色代码"}
        
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return {"success": True, "rgb": [r, g, b], "hex": f"#{hex_color}"}
        except:
            return {"success": False, "error": "无效的十六进制颜色代码"}

skill = HexToRgbSkill()
