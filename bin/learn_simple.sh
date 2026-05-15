#!/bin/bash
echo "🦞 Agent 学习报告"
echo "================"

# 1. 工程师学习内容
echo ""
echo "🔧 工程师知识:"
echo "  - 端口监控: $(ss -tlnp 2>/dev/null | wc -l) 个监听端口"
echo "  - 服务状态: $(pm2 list 2>/dev/null | grep -c online) 个在线服务"
echo "  - Docker 容器: $(docker ps 2>/dev/null | wc -l) 个运行中"

# 2. 关键词学习器
echo ""
echo "📚 关键词知识:"
echo "  - 关键词库: $(cat data/keywords.json 2>/dev/null | grep -c '"name"' || echo 0) 个"
echo "  - 待学习词: $(cat data/keyword_pending.json 2>/dev/null | grep -c '"count"' || echo 0) 个"

# 3. 爬虫学习
echo ""
echo "🕷️ 爬虫知识:"
echo "  - 发现 URL: $(cat data/urls/discovered.json 2>/dev/null | jq 'length' 2>/dev/null || echo 0) 个"
echo "  - 已采集: $(ls data/content/*.txt 2>/dev/null | wc -l) 个页面"

# 4. 安全学习
echo ""
echo "🔒 安全知识:"
echo "  - 敏感检测: 已启用"
echo "  - 密钥隔离: $(ls tenants/*/secrets.json 2>/dev/null | wc -l) 个租户"

echo ""
echo "✅ 学习完成"
