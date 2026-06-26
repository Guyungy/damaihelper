#!/bin/bash
clear
echo "==================================================="
echo "    DamaiHelper 全能抢票王 - 一键运行控制中心 (macOS)"
echo "==================================================="
echo ""

# Step 1: Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "[!] 未检测到 python3，请确保已安装 Python 3 环境并添加到 PATH！"
    exit 1
fi

# Step 2: Install dependencies
echo "[*] 正在检查并自动安装依赖包 (requirements.txt)..."
python3 -m pip install -r requirements.txt

# Step 3: Run interactive selection menu
echo ""
echo "==================================================="
echo "   [1] 启动全新 Web 网页控制面板 (推荐)"
echo "   [2] 启动经典 Desktop GUI 图形界面"
echo "==================================================="
read -p "请选择要启动的界面序号 (默认 1): " choice

if [ "$choice" = "2" ]; then
    echo ""
    echo "[*] 正在启动 经典 Desktop GUI 图形界面..."
    python3 GUI.py
else
    echo ""
    echo "[*] 正在启动 全新 Web 网页控制面板..."
    python3 web_server.py
fi
