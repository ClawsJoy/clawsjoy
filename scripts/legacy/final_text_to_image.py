from lib.smart_config import smart_config
#!/usr/bin/env python3
from diffusers import StableDiffusionXLPipeline
import torch
import time
import os
import json

class TextToImageGenerator:
    def __init__(self, model_path="str(smart_config.ROOT)/models/dreamshaper"):
        print("初始化模型...")
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            variant="fp16"
        )
        self.pipe.enable_model_cpu_offload()
        self.pipe.enable_attention_slicing()
        print("✅ 模型就绪 (15秒/张)\n")
    
    def generate(self, prompt, output_path=None, steps=15, size=768):
        if output_path is None:
            output_path = f"output_{int(time.time())}.png"
        
        print(f"🎨 生成: {prompt[:60]}...")
        start = time.time()
        
        image = self.pipe(
            prompt=prompt,
            num_inference_steps=steps,
            height=size,
            width=size,
            guidance_scale=7.0
        ).images[0]
        
        image.save(output_path)
        elapsed = time.time() - start
        print(f"✅ 保存: {output_path} ({elapsed:.1f}秒)\n")
        return output_path
    
    def batch_generate(self, prompts, output_dir="./outputs", steps=15, size=768):
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        for i, (title, prompt) in enumerate(prompts, 1):
            output_path = f"{output_dir}/{title}.png"
            self.generate(prompt, output_path, steps, size)
            results.append(output_path)
        
        return results

# 使用示例
if __name__ == "__main__":
    generator = TextToImageGenerator()
    
    # 自动化文案成图任务
    tasks = [
        ("产品海报_AI峰会", "AI technology conference poster, futuristic design, blue and white color scheme, text 'AI Summit 2026', professional"),
        ("社交媒体_春天", "spring blooming flowers, social media post, bright colors, inspirational quote 'New Beginnings', 4k"),
        ("营销素材_科技", "futuristic technology concept, digital transformation, glowing neon lines, corporate style"),
        ("创意配图_未来城市", "cyberpunk city with flying cars, night scene, purple and blue neon lights, highly detailed"),
    ]
    
    print(f"开始批量生成 {len(tasks)} 张图片...\n")
    generator.batch_generate(tasks, steps=15, size=768)
    
    print(f"🎉 全部完成！图片保存在 outputs/ 目录")
