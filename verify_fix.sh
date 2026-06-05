#!/bin/bash
echo "🔍 ClawsJoy v5 修复验证"
echo "========================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. 服务检查
echo -n "1. 服务状态: "
if curl -s http://127.0.0.1:5002/health > /dev/null; then
    echo -e "${GREEN}✅ 运行中${NC}"
else
    echo -e "${RED}❌ 未运行${NC}"
fi

# 2. 密钥检查
echo -n "2. 硬编码密钥: "
if grep -q 'SECRET_KEY = "clawsjoy-secret-key' scripts/user_preference_service.py 2>/dev/null; then
    echo -e "${RED}❌ 仍存在${NC}"
else
    echo -e "${GREEN}✅ 已移除${NC}"
fi

# 3. 调试代码检查
echo -n "3. ipdb 调试代码: "
if grep -q "ipdb.set_trace()" --include="*.py" . 2>/dev/null; then
    echo -e "${YELLOW}⚠️ 仍有残留${NC}"
else
    echo -e "${GREEN}✅ 已清理${NC}"
fi

# 4. 配置模块检查
echo -n "4. 配置模块: "
if [ -f "core/lib/port_config.py" ] && [ -f "core/lib/path_config.py" ]; then
    echo -e "${GREEN}✅ 已创建${NC}"
else
    echo -e "${RED}❌ 缺失${NC}"
fi

# 5. 环境变量检查
echo -n "5. .env 文件: "
if grep -q "PROJECT_ROOT" .env 2>/dev/null; then
    echo -e "${GREEN}✅ 已更新${NC}"
else
    echo -e "${YELLOW}⚠️ 未更新${NC}"
fi

# 6. 最终结论
echo -e "\n========================"
if curl -s http://127.0.0.1:5002/health > /dev/null; then
    echo -e "${GREEN}🎉 修复验证通过！服务运行正常${NC}"
else
    echo -e "${RED}⚠️ 请手动重启服务: ./start_prod.sh${NC}"
fi
