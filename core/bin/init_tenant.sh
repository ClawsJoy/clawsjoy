#!/bin/bash
# 初始化租户 - 全自动配置

TENANT_ID=$1
if [ -z "$TENANT_ID" ]; then
    echo "用法: ./init_tenant.sh <租户ID>"
    exit 1
fi

TENANT_DIR="/mnt/d/clawsjoy/tenants/$TENANT_ID"
mkdir -p $TENANT_DIR/{config/youtube,videos,data,logs}

echo "✅ 租户 $TENANT_ID 目录已创建"

# 创建租户配置文件
cat > $TENANT_DIR/config/tenant.json << JSON
{
    "tenant_id": "$TENANT_ID",
    "name": "租户 $TENANT_ID",
    "created_at": "$(date -Iseconds)",
    "youtube_configured": false
}
JSON

echo ""
echo "📋 租户 $TENANT_ID 初始化完成"
echo ""
echo "下一步："
echo "1. 用户将 client_secrets.json 放到: $TENANT_DIR/config/youtube/"
echo "2. 运行授权: python3 agents/youtube_uploader.py --tenant $TENANT_ID --auth"
echo "3. 之后自动上传: python3 agents/youtube_uploader.py --tenant $TENANT_ID"
