#!/usr/bin/env python3
"""邮件服务模块 - 发送验证邮件"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer
import os

# 邮件配置（需要修改为实际配置）
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "your-email@qq.com")
SMTP_PASS = os.environ.get("SMTP_PASS", "your-smtp-password")
SECRET_KEY = os.environ.get("SECRET_KEY", "clawsjoy-secret-2026")

serializer = URLSafeTimedSerializer(SECRET_KEY)


def generate_token(email):
    """生成邮箱验证 token"""
    return serializer.dumps(email, salt="email-verify")


def verify_token(token, expiration=3600):
    """验证 token"""
    try:
        email = serializer.loads(token, salt="email-verify", max_age=expiration)
        return email
    except:
        return None


def send_email(to_email, subject, html_body):
    """发送邮件"""
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


def send_verify_email(to_email):
    """发送验证邮件"""
    token = generate_token(to_email)
    verify_url = f"http://redis:8082/api/auth/verify?token={token}"

    html = f"""
    <h2>欢迎注册 ClawsJoy</h2>
    <p>请点击下方链接验证您的邮箱：</p>
    <p><a href="{verify_url}">{verify_url}</a></p>
    <p>链接有效期 1 小时</p>
    <p>如果非本人操作，请忽略此邮件。</p>
    """
    return send_email(to_email, "ClawsJoy 邮箱验证", html)


def send_reset_email(to_email):
    """发送重置密码邮件"""
    token = generate_token(to_email)
    reset_url = f"http://redis:8082/reset-password?token={token}"

    html = f"""
    <h2>重置 ClawsJoy 密码</h2>
    <p>请点击下方链接重置密码：</p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    <p>链接有效期 1 小时</p>
    <p>如果非本人操作，请忽略此邮件。</p>
    """
    return send_email(to_email, "ClawsJoy 密码重置", html)


if __name__ == "__main__":
    print("邮件服务模块已加载")
    print("需要配置 SMTP_HOST, SMTP_USER, SMTP_PASS 环境变量")
