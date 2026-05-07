#!/usr/bin/env python3
"""短信验证码服务"""

import random
import time
import redis
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

# ============ 配置（需要修改） ============
ACCESS_KEY_ID = "your-access-key-id"
ACCESS_KEY_SECRET = "your-access-key-secret"
SIGN_NAME = "ClawsJoy"
TEMPLATE_CODE = "SMS_xxx"
SMS_REGION = "cn-hangzhou"

# Redis 连接（存储验证码）
REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 1

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def generate_code(length=6):
    """生成6位验证码"""
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def send_sms(phone, code):
    """发送短信验证码"""
    try:
        client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, SMS_REGION)
        request = CommonRequest()
        request.set_accept_format("json")
        request.set_domain("dysmsapi.aliyuncs.com")
        request.set_method("POST")
        request.set_protocol_type("https")
        request.set_version("2017-05-25")
        request.set_action_name("SendSms")

        request.add_query_param("RegionId", SMS_REGION)
        request.add_query_param("PhoneNumbers", phone)
        request.add_query_param("SignName", SIGN_NAME)
        request.add_query_param("TemplateCode", TEMPLATE_CODE)
        request.add_query_param("TemplateParam", f'{{"code":"{code}"}}')

        response = client.do_action(request)
        return True
    except Exception as e:
        print(f"短信发送失败: {e}")
        return False


def send_verify_code(phone):
    """发送验证码并存储到 Redis"""
    code = generate_code()
    # 存储到 Redis，5分钟过期
    r.setex(f"sms_code:{phone}", 300, code)

    if send_sms(phone, code):
        return {"success": True, "message": "验证码已发送"}
    return {"success": False, "error": "发送失败"}


def verify_code(phone, code):
    """验证验证码"""
    saved = r.get(f"sms_code:{phone}")
    if saved and saved == code:
        r.delete(f"sms_code:{phone}")
        return True
    return False


if __name__ == "__main__":
    print("短信服务模块已加载")
    print("需要配置 ACCESS_KEY_ID, ACCESS_KEY_SECRET, SIGN_NAME, TEMPLATE_CODE")
