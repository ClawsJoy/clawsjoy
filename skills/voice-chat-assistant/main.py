#!/usr/bin/env python3
"""语音聊天 Skill - 返回动作指令"""
import json

def execute(params):
    tenant_id = params.get('tenant_id', '1')
    message = params.get('message', '')
    
    # 检测是否制作宣传片
    if '宣传片' in message:
        city = '香港'
        if '北京' in message: city = '北京'
        elif '上海' in message: city = '上海'
        elif '深圳' in message: city = '深圳'
        
        style = '科技'
        
        # 返回动作指令，让主程序执行
        return {
            'success': True,
            'action': 'make_promo',
            'city': city,
            'style': style,
            'tenant_id': tenant_id
        }
    
    # 检测是否查找资料库
    if '照片' in message or '图片' in message or '相册' in message:
        return {
            'success': True,
            'action': 'list_library',
            'tenant_id': tenant_id,
            'limit': 5
        }
    
    # 普通聊天
    return {
        'success': True,
        'action': 'chat',
        'message': f'收到消息: {message}。您可以说"制作北京宣传片"或"找我的照片"。'
    }
