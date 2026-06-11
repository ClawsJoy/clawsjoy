#!/bin/bash
# 定时任务配置

# 每日统计报告
0 9 * * * cd /home/flybo/clawsjoy_v5 && python3 -c "from core.lib.usage_stats import usage_stats; print(usage_stats.generate_report())" >> logs/daily_report.log

# 每周生成推广文章
0 10 * * 1 cd /home/flybo/clawsjoy_v5 && python3 scripts/generate_promo.py >> logs/promo.log

# 每次 push 后更新 CHANGELOG
# (配置 git hook)
