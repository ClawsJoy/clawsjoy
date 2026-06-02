#!/bin/bash
echo "清理临时文件..."
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete  
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.log" -type f -size +100M -delete
find . -name "nohup.out" -delete

echo "压缩旧日志..."
find logs/ -name "*.log" -mtime +30 -gzip 2>/dev/null

echo "清理完成"
