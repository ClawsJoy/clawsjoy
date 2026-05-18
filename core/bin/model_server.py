from lib.smart_config import smart_config
#!/usr/bin/env python3
from diffusers import StableDiffusionXLPipeline
import torch
import time
import os
import json
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# 全局模型实例
pipe = None

def load_model():
    global pipe
    print("加载模型...")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "str(smart_config.ROOT)/models/dreamshaper",
        torch_dtype=torch.float16,
        variant="fp16"
    )
    pipe.enable_model_cpu_offload()
    print("✅ 模型加载完成")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', 'a beautiful landscape')
    steps = data.get('steps', 15)
    
    print(f"生成: {prompt[:50]}...")
    start = time.time()
    
    image = pipe(
        prompt=prompt,
        num_inference_steps=steps,
        height=768,
        width=768
    ).images[0]
    
    filename = f"output_{int(time.time())}.png"
    image.save(filename)
    elapsed = time.time() - start
    
    return jsonify({
        "success": True,
        "file": filename,
        "time": elapsed,
        "prompt": prompt
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "model_loaded": pipe is not None})

if __name__ == '__main__':
    load_model()
    print("启动API服务...")
    app.run(host='0.0.0.0', port=5000)
