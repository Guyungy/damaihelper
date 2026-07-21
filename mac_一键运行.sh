#!/bin/bash
set -e
cd "$(dirname "$0")"
clear
echo "==================================================="
echo "  DamaiHelper 一键运行 (macOS/Linux)"
echo "==================================================="

if ! command -v python3 >/dev/null 2>&1; then
  echo "[!] 未找到 python3"
  exit 1
fi

echo "[1] 安装 Python 依赖..."
python3 tools/install_deps.py || true

if [ -f web-ui/package.json ] && command -v npm >/dev/null 2>&1; then
  echo "[2] 构建 Ant Design 前端..."
  (cd web-ui && npm install && npm run build) || true
fi

echo ""
echo "  [1] Web 控制面板"
echo "  [2] Desktop GUI"
read -p "选择 (默认 1): " choice
if [ "$choice" = "2" ]; then
  python3 GUI.py
else
  python3 web_server.py
fi
