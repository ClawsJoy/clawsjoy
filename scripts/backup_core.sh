#!/bin/bash
# ClawsJoy 核心备份脚本 - 只备份开箱即用部分

set -e

# 配置
BACKUP_NAME="clawsjoy-core-$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="/mnt/d/clawsjoy-backups"
mkdir -p "$BACKUP_DIR"

echo "=========================================="
echo "ClawsJoy 核心备份"
echo "=========================================="
echo "备份名称: $BACKUP_NAME"
echo "备份目录: $BACKUP_DIR"
echo ""

# 创建临时目录
TEMP_DIR="/tmp/$BACKUP_NAME"
mkdir -p "$TEMP_DIR"

echo "1. 复制核心代码..."
# 核心库
cp -r lib "$TEMP_DIR/"
cp -r intelligence "$TEMP_DIR/"
cp -r agents "$TEMP_DIR/"
# 注意：agent_core 是依赖，需要包含
cp -r agent_core "$TEMP_DIR/" 2>/dev/null || echo "   agent_core 不存在，跳过"

echo "2. 复制技能系统..."
# 只复制标准技能目录（排除 __pycache__）
mkdir -p "$TEMP_DIR/skills"
for skill in ai-image-gen check_video_status file_service_skill improve_executor scheduler video_description video_public audio core data doc image math memory network self_heal text tools video wrappers; do
    if [ -d "skills/$skill" ]; then
        cp -r "skills/$skill" "$TEMP_DIR/skills/"
        echo "   ✅ $skill"
    fi
done

echo "3. 复制配置文件..."
mkdir -p "$TEMP_DIR/config"
cp -r config/driver "$TEMP_DIR/config/"
cp -r config/intelligence "$TEMP_DIR/config/" 2>/dev/null
cp config/agents.yaml "$TEMP_DIR/config/" 2>/dev/null
cp config/config.yaml "$TEMP_DIR/config/" 2>/dev/null

echo "4. 复制 Web 界面..."
cp web_dashboard.py "$TEMP_DIR/"
cp -r web "$TEMP_DIR/"
cp app_v4.py "$TEMP_DIR/"
cp bin/active_runner.py "$TEMP_DIR/bin/" 2>/dev/null || mkdir -p "$TEMP_DIR/bin" && cp bin/active_runner.py "$TEMP_DIR/bin/"

echo "5. 复制记忆框架（不含数据）..."
mkdir -p "$TEMP_DIR/memory"
cp memory/MEMORY.md "$TEMP_DIR/memory/" 2>/dev/null
# 创建空的记忆目录结构
mkdir -p "$TEMP_DIR/memory/daily"
mkdir -p "$TEMP_DIR/memory/long_term"

echo "6. 复制文档..."
cp -r docs "$TEMP_DIR/"
cp README.md "$TEMP_DIR/"
cp VERSION "$TEMP_DIR/"
cp VERSION_SPEC.md "$TEMP_DIR/"
cp CHANGELOG.md "$TEMP_DIR/"

echo "7. 复制依赖文件..."
cp requirements.txt "$TEMP_DIR/" 2>/dev/null
cp .env.example "$TEMP_DIR/" 2>/dev/null

echo "8. 清理临时文件..."
find "$TEMP_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$TEMP_DIR" -name "*.pyc" -delete 2>/dev/null

echo "9. 创建版本信息..."
cat > "$TEMP_DIR/BUILD_INFO.txt" << EOF
ClawsJoy Core Backup
Build Date: $(date)
Version: $(cat VERSION 2>/dev/null || echo "4.0.0")
Backup Script Version: 1.0.0

Contents:
- Core libraries (lib/, intelligence/, agents/)
- Standardized skills (20 skills)
- Configuration files (driver/, intelligence/)
- Web interface
- Memory framework (structure only)
- Documentation
