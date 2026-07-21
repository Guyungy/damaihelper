@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"

echo ===================================================
echo   DamaiHelper 一键运行控制中心
echo ===================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [!] 未找到 python，请先安装 Python 3.10+ 并加入 PATH
  pause
  exit /b 1
)

echo [1] 安装 / 更新 Python 依赖 (含 CUDA torch 探测)
python tools\install_deps.py
if errorlevel 1 (
  echo [!] 依赖安装出现错误，仍可尝试启动（YOLO 将走 mock）
)

echo.
if exist "web-ui\package.json" (
  where npm >nul 2>nul
  if not errorlevel 1 (
    echo [2] 安装前端依赖并构建 Ant Design 面板
    pushd web-ui
    call npm install
    call npm run build
    popd
  ) else (
    echo [2] 未检测到 npm，跳过 Ant Design 构建，将使用 web/index.html
  )
)

echo.
echo ===================================================
echo   [1] 启动 Web 控制面板 (推荐)
echo   [2] 启动经典 Desktop GUI
echo   [3] 仅安装依赖后退出
echo ===================================================
set /p choice="请选择 (默认 1): "

if "%choice%"=="2" (
  echo 启动 Desktop GUI...
  python GUI.py
) else if "%choice%"=="3" (
  echo 完成。
) else (
  echo 启动 Web 服务...
  python web_server.py
)

pause
