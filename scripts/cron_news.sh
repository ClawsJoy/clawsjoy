#!/bin/bash
# 定时抓取新闻并更新向量库

cd "$(dirname "$0")/.."

# 激活虚拟环境（如果需要）
# source venv/bin/activate

echo "=========================================="
echo "新闻抓取任务开始: $(date)"
echo "=========================================="

# 抓取所有分类新闻
python3 services/news_crawler.py --category all --limit 15

echo ""
echo "新闻抓取任务完成: $(date)"
echo "=========================================="
