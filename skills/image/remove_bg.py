"""抠图技能 - 移除图片背景，生成透明 PNG"""
import os
from pathlib import Path

class RemoveBgSkill:
    name = "remove_bg"
    description = "移除图片背景，生成透明背景的 PNG 图片"
    version = "1.0.0"
    category = "image"
    
    def execute(self, params):
        input_path = params.get("input_path", "")
        output_path = params.get("output_path", "")
        
        if not input_path:
            return {"success": False, "error": "缺少 input_path 参数"}
        
        if not os.path.exists(input_path):
            return {"success": False, "error": f"输入图片不存在: {input_path}"}
        
        if not output_path:
            name = Path(input_path).stem
            output_dir = params.get("output_dir", "output/bg")
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            output_path = f"{output_dir}/{name}_nobg.png"
        
        try:
            from rembg import remove
            from PIL import Image
            
            # 读取图片
            with open(input_path, 'rb') as f:
                input_data = f.read()
            
            # 移除背景
            output_data = remove(input_data)
            
            # 保存结果
            with open(output_path, 'wb') as f:
                f.write(output_data)
            
            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "message": f"抠图完成，保存到 {output_path}"
            }
        except ImportError as e:
            return {"success": False, "error": f"请安装依赖: pip install rembg onnxruntime, 错误: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

skill = RemoveBgSkill()
