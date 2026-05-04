#!/usr/bin/env python3
"""语音聊天 Skill - 自然语言理解 + 意图分发"""
import json
import re
import requests
from datetime import datetime

# 会话记忆存储（简单字典，后续可改为 Redis）
sessions = {}

def call_clawsjoy_api(endpoint, method='POST', data=None):
    """调用 ClawsJoy 内部 API"""
    url = f"http://localhost:8084{endpoint}"
    try:
        if method == 'POST':
            resp = requests.post(url, json=data, timeout=30)
        else:
            resp = requests.get(url, params=data, timeout=30)
        return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        print(f"调用 API 失败: {e}")
        return None

def extract_intent_and_entities(text, session_id):
    """使用本地 Ollama 模型解析意图和实体"""
    prompt = f"""分析用户输入，提取意图和关键信息。
用户: {text}

输出 JSON 格式，只输出 JSON，不要其他解释。
可能意图: make_promo, search_library, chat, help
关键实体: city, style, keyword

示例:
{{"intent": "make_promo", "city": "北京", "style": "科技"}}
{{"intent": "search_library", "keyword": "照片"}}
{{"intent": "chat", "reply": "你好，有什么可以帮你的？"}}"""
    
    try:
        resp = requests.post("http://localhost:11434/api/generate", 
                            json={"model": "qwen2.5:3b", "prompt": prompt, "stream": False},
                            timeout=30)
        if resp.status_code == 200:
            result_text = resp.json().get('response', '{}')
            # 提取 JSON 部分
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
    except Exception as e:
        print(f"Ollama 调用失败: {e}")
    
    # 降级：简单的关键词匹配
    if '制作' in text and '宣传片' in text:
        city = '香港'
        if '上海' in text: city = '上海'
        elif '北京' in text: city = '北京'
        return {"intent": "make_promo", "city": city, "style": "科技"}
    elif '照片' in text or '相册' in text or '图片' in text:
        return {"intent": "search_library", "keyword": text}
    else:
        return {"intent": "chat", "reply": "你好！我可以帮你制作宣传片、查找资料库中的照片。试试说：'制作北京宣传片' 或 '找我的照片'"}

def execute(params):
    """Skill 入口"""
    tenant_id = params.get('tenant_id', '1')
    message = params.get('message', '')
    session_id = params.get('session_id', 'default')
    
    # 获取或创建会话记忆
    if session_id not in sessions:
        sessions[session_id] = {'history': [], 'last_intent': None}
    
    # 解析意图
    parsed = extract_intent_and_entities(message, session_id)
    intent = parsed.get('intent', 'chat')
    
    response = {}
    
    if intent == 'make_promo':
        city = parsed.get('city', '香港')
        style = parsed.get('style', '科技')
        # 调用宣传片制作 Skill
        promo_result = call_clawsjoy_api('/api/task/promo', 'POST', 
                                         {'city': city, 'style': style, 'tenant_id': tenant_id})
        if promo_result and promo_result.get('success'):
            response = {
                'type': 'promo',
                'message': f'已为您生成{city}{style}宣传片',
                'video_url': promo_result.get('video_url')
            }
        else:
            response = {'type': 'text', 'message': f'抱歉，生成{city}宣传片失败，请稍后重试。'}
    
    elif intent == 'search_library':
        keyword = parsed.get('keyword', message)
        # 调用资料库检索（通过内部 API）
        lib_result = call_clawsjoy_api('/api/library/list', 'GET', 
                                       {'tenant_id': tenant_id, 'limit': 10})
        if lib_result and lib_result.get('success'):
            files = lib_result.get('files', [])
            if files:
                file_list = '\n'.join([f"📄 {f['name']}" for f in files[:5]])
                response = {
                    'type': 'library',
                    'message': f'在您的资料库中找到以下文件：\n{file_list}'
                }
            else:
                response = {'type': 'text', 'message': '您的资料库暂无文件，请先上传。'}
        else:
            response = {'type': 'text', 'message': '资料库检索失败，请稍后重试。'}
    
    else:  # chat 或默认
        reply = parsed.get('reply', '您好，我是 ClawsJoy 助手。您可以对我说："制作北京宣传片" 或 "找我的照片"。')
        response = {'type': 'text', 'message': reply}
    
    # 更新会话记忆
    sessions[session_id]['history'].append({'user': message, 'assistant': response.get('message', '')})
    sessions[session_id]['last_intent'] = intent
    
    return {'success': True, 'response': response}
