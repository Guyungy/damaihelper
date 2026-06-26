@echo off
REM Step 1: 创建 conda 虚拟环境 python3.12 命名为 joker
conda create --name joker python=3.12 -y

REM Step 2: 激活虚拟环境
conda activate joker

REM Step 3: 安装依赖包
pip install -r requirements.txt

REM Step 4: 启动选项选择
echo ===================================================
echo     DamaiHelper 全能抢票王 - 一键运行控制中心
echo ===================================================
echo   [1] 启动全新 Web 网页控制面板 (推荐)
echo   [2] 启动经典 Desktop GUI 图形界面
echo ===================================================
set /p choice="请选择要启动的界面序号 (默认 1): "

if "%choice%"=="2" (
    echo 正在启动 经典 Desktop GUI 图形界面...
    python GUI.py
) else (
    echo 正在启动 全新 Web 网页控制面板...
    python web_server.py
)

REM Step 5: 保持命令行窗口打开，直到用户关闭
pause
