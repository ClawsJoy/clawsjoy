#!/bin/bash
TENANT_ID=$1
if [ -z "$TENANT_ID" ]; then
    echo "用法: ./setup_youtube_tenant.sh <租户ID>"
    exit 1
fi

TENANT_CONFIG="/mnt/d/clawsjoy/tenants/$TENANT_ID/config"
mkdir -p "$TENANT_CONFIG"

echo "=========================================="
echo "YouTube 配置向导 - 租户: $TENANT_ID"
echo "=========================================="
echo ""
echo "1. 请将 Google Cloud 下载的 client_secrets.json 放到:"
echo "   $TENANT_CONFIG/client_secrets.json"
echo ""
echo "2. 然后运行授权:"
echo "   cd /mnt/d/clawsjoy"
echo "   python3 agents/youtube_uploader.py --tenant $TENANT_ID --auth"
echo ""
echo "3. 授权成功后 token 会自动保存"
echo "=========================================="
