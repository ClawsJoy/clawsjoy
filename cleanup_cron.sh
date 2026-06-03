#!/bin/bash
echo "清理临时文件..."
find /home/flybo/clawsjoy_v5 -name "*.pyc" -delete
find /home/flybo/clawsjoy_v5 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /home/flybo/clawsjoy_v5/output -type f -mtime +7 -delete
echo "清理完成: $(date)" >> /home/flybo/clawsjoy_v5/logs/cleanup.log
