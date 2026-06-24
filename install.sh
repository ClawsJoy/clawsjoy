#!/bin/bash
# ClawsJoy v5.0 一键安装脚本
# 支持: Linux (Ubuntu/Debian/CentOS) / macOS / WSL

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║       ClawsJoy v5.0 安装程序         ║"
echo "  ║   智能体矩阵系统 · 开箱即用          ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

INSTALL_DIR="${HOME}/clawsjoy"
PYTHON_CMD=""
VENV_DIR=""

# ========== 检测系统 ==========
detect_system() {
    echo -e "${YELLOW}[1/6] 检测系统环境...${NC}"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if [ -f /etc/debian_version ]; then
            DISTRO="debian"
        elif [ -f /etc/redhat-release ]; then
            DISTRO="redhat"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        echo -e "${YELLOW}Windows检测到，请使用 WSL2 或 install.ps1${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}  ✓ 系统: $OS${NC}"
}

# ========== 检测Python ==========
detect_python() {
    echo -e "${YELLOW}[2/6] 检测 Python...${NC}"
    
    for cmd in python3.12 python3.11 python3.10 python3.9 python3; do
        if command -v $cmd &> /dev/null; then
            version=$($cmd --version 2>&1 | grep -oP '\d+\.\d+')
            major=$(echo $version | cut -d. -f1)
            minor=$(echo $version | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
                PYTHON_CMD=$cmd
                break
            fi
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        echo -e "${RED}  ✗ 需要 Python 3.9+，请先安装${NC}"
        if [ "$OS" = "linux" ] && [ "$DISTRO" = "debian" ]; then
            echo "  sudo apt install python3.11 python3.11-venv -y"
        fi
        exit 1
    fi
    
    echo -e "${GREEN}  ✓ Python: $($PYTHON_CMD --version)${NC}"
}

# ========== 创建虚拟环境 ==========
setup_venv() {
    echo -e "${YELLOW}[3/6] 创建虚拟环境...${NC}"
    
    VENV_DIR="${INSTALL_DIR}/venv"
    $PYTHON_CMD -m venv "$VENV_DIR"
    source "${VENV_DIR}/bin/activate"
    
    # 升级pip
    pip install --upgrade pip -q
    echo -e "${GREEN}  ✓ 虚拟环境: ${VENV_DIR}${NC}"
}

# ========== 安装依赖 ==========
install_deps() {
    echo -e "${YELLOW}[4/6] 安装依赖...${NC}"
    
    pip install -q \
        flask flask-cors pyyaml requests \
        psutil aiohttp \
        pydantic dataclasses-json \
        tiktoken chromadb \
        2>&1 | tail -1
    
    echo -e "${GREEN}  ✓ 依赖安装完成${NC}"
}

# ========== 检测/安装 Ollama ==========
setup_ollama() {
    echo -e "${YELLOW}[5/6] 设置 Ollama...${NC}"
    
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}  ✓ Ollama 已安装${NC}"
    else
        echo "  安装 Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        echo -e "${GREEN}  ✓ Ollama 安装完成${NC}"
    fi
    
    # 确保服务运行
    if ! pgrep -x ollama > /dev/null; then
        ollama serve &
        sleep 2
    fi
    
    # 检测硬件推荐模型
    echo "  检测硬件配置..."
    $PYTHON_CMD -c "
import sys; sys.path.insert(0, '${INSTALL_DIR}')
from core.lib.hardware_probe import hardware_probe
rec = hardware_probe.report()['recommended']
for m in rec['models']:
    print(f'  → {m}')
" 2>/dev/null || echo "  → qwen2.5:3b"
    
    echo -e "${GREEN}  ✓ Ollama 就绪${NC}"
}

# ========== 创建启动脚本 ==========
create_launcher() {
    echo -e "${YELLOW}[6/6] 创建启动脚本...${NC}"
    
    # 启动脚本
    cat > "${INSTALL_DIR}/start.sh" << 'STARTEOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

# 确保Ollama运行
pgrep -x ollama > /dev/null || ollama serve &

echo "🚀 ClawsJoy Gateway 启动中..."
python3 agent_gateway_enhanced.py
STARTEOF
    chmod +x "${INSTALL_DIR}/start.sh"
    
    # 停止脚本
    cat > "${INSTALL_DIR}/stop.sh" << 'STOPEOF'
#!/bin/bash
pkill -f "agent_gateway_enhanced.py" 2>/dev/null
echo "🛑 ClawsJoy 已停止"
STOPEOF
    chmod +x "${INSTALL_DIR}/stop.sh"
    
    # systemd 服务（Linux）
    if [ "$OS" = "linux" ]; then
        cat > "${INSTALL_DIR}/clawsjoy.service" << 'SVCEOF'
[Unit]
Description=ClawsJoy AI Agent System
After=network.target ollama.service

[Service]
Type=simple
User=%u
WorkingDirectory=%h/clawsjoy
ExecStart=%h/clawsjoy/start.sh
ExecStop=%h/clawsjoy/stop.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF
        echo -e "${GREEN}  ✓ systemd服务文件: ${INSTALL_DIR}/clawsjoy.service${NC}"
        echo "  安装服务: sudo cp ${INSTALL_DIR}/clawsjoy.service /etc/systemd/system/ && sudo systemctl enable clawsjoy"
    fi
    
    echo -e "${GREEN}  ✓ 启动脚本: ${INSTALL_DIR}/start.sh${NC}"
}

# ========== 主流程 ==========
main() {
    detect_system
    detect_python
    
    # 复制项目到安装目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
        echo "  复制项目到 ${INSTALL_DIR}..."
        mkdir -p "$INSTALL_DIR"
        rsync -a --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
              --exclude='data' --exclude='logs' --exclude='_archive' \
              "$SCRIPT_DIR/" "$INSTALL_DIR/"
    fi
    
    cd "$INSTALL_DIR"
    mkdir -p data logs
    
    setup_venv
    install_deps
    setup_ollama
    create_launcher
    
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║      ClawsJoy v5.0 安装完成！        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  启动: ${CYAN}${INSTALL_DIR}/start.sh${NC}"
    echo -e "  停止: ${CYAN}${INSTALL_DIR}/stop.sh${NC}"
    echo -e "  Web:  ${CYAN}http://localhost:5002${NC}"
    echo ""
    echo -e "${YELLOW}  首次启动会自动下载推荐模型，请耐心等待${NC}"
    echo ""
}

main
