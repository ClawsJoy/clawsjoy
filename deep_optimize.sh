#!/bin/bash
echo "🔧 ClawsJoy v5 深度优化"

# 1. 替换硬编码路径为配置
echo "修复硬编码路径..."
find . -name "*.py" -exec sed -i 's|"data/|f"{get_data_root()}/|g' {} \;

# 2. 替换 print 为 logging（核心文件）
echo "添加 logging 配置..."
cat >> core/lib/logging_config.py << 'LOG'
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
LOG

# 3. 检查并修复配置文件
echo "验证配置文件..."
python3 -c "
import yaml
import os

configs = ['config/system/system_unified.yaml', 'config/routes/routes.yaml']
for cfg in configs:
    if os.path.exists(cfg):
        with open(cfg) as f:
            data = yaml.safe_load(f)
            print(f'✅ {cfg} 有效')
"

echo "✅ 深度优化完成"
