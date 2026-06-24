#!/bin/bash
# ClawsJoy 离线打包脚本

VERSION="5.0.0"
PACKAGE="clawsjoy-${VERSION}-$(uname -s)-$(uname -m).tar.gz"
TEMP_DIR="/tmp/clawsjoy-package"

echo "📦 打包 ClawsJoy v${VERSION}..."

# 创建临时目录
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR/clawsjoy"

# 复制源码
rsync -a --exclude='__pycache__' --exclude='*.pyc' --exclude='venv' \
      --exclude='data' --exclude='logs' --exclude='_archive' \
      --exclude='.git' --exclude='*.tar.gz' \
      ./ "$TEMP_DIR/clawsjoy/"

# 生成依赖列表
cd "$TEMP_DIR/clawsjoy"
pip freeze > requirements.lock 2>/dev/null || echo "flask>=3.0\npsutil>=5.9\npyyaml>=6.0" > requirements.lock

# 下载Ollama安装脚本
curl -sL https://ollama.com/install.sh -o ollama-install.sh 2>/dev/null || echo "#!/bin/bash\necho '请访问 https://ollama.com 安装Ollama'" > ollama-install.sh

# 创建安装说明
cat > INSTALL.txt << 'README'
ClawsJoy v5.0 - 智能体矩阵系统
=================================

系统要求:
  - CPU: 4核+
  - 内存: 8GB+
  - GPU: 推荐 NVIDIA 4GB+ VRAM
  - 系统: Linux / macOS / WSL2

安装步骤:
  1. 安装Ollama: curl -fsSL https://ollama.com/install.sh | sh
  2. 下载模型: ollama pull qwen2.5:3b
  3. 安装Python依赖: pip install -r requirements.lock
  4. 启动: python3 agent_gateway_enhanced.py
  5. 访问: http://localhost:5002/dashboard

硬件厂商预装:
  - 将模型文件放入 /usr/share/clawsjoy/models/
  - systemd服务: sudo cp clawsjoy.service /etc/systemd/system/
  - 开机自启: sudo systemctl enable clawsjoy

README

# 打包
cd /tmp
tar czf "$PACKAGE" clawsjoy/
mv "$PACKAGE" "$OLDPWD/"

# 清理
rm -rf "$TEMP_DIR"

echo ""
echo "✅ 打包完成: ${PACKAGE}"
echo "   大小: $(du -h "${PACKAGE}" | cut -f1)"
echo ""
echo "解压安装: tar xzf ${PACKAGE} && cd clawsjoy && bash install.sh"
