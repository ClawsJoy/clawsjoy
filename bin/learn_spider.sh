#!/bin/bash
# 爬虫专属学习

echo "🕷️ 爬虫学习链接模式..."
# 分析已采集的 URL 特征
cat /mnt/d/clawsjoy/data/urls/discovered.json | jq 'keys' | head -50 > /tmp/url_patterns.txt

python3 -c "
from agents.url_scout import URLScout
scout = URLScout()
scout.learn_patterns()
"
