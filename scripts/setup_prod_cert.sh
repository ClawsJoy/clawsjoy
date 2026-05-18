#!/bin/bash
# 生产证书配置脚本

echo "=========================================="
echo "生产证书配置"
echo "=========================================="

# 方式1: 使用 Let's Encrypt (需要域名)
if [ -n "$1" ]; then
    DOMAIN=$1
    echo "为域名 $DOMAIN 配置证书..."
    
    # 安装 certbot
    sudo apt update
    sudo apt install -y certbot
    
    # 获取证书
    sudo certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN
    
    # 复制证书
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/cert.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/key.pem
    sudo chmod 644 ssl/cert.pem
    sudo chmod 600 ssl/key.pem
    
    echo "✅ 证书已配置: $DOMAIN"
else
    echo "⚠️ 未提供域名，使用现有自签名证书"
    echo "用法: ./scripts/setup_prod_cert.sh yourdomain.com"
fi

echo "当前证书:"
ls -la ssl/
