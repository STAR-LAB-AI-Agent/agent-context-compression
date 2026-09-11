@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [1/3] 检查 Python...
python --version
if errorlevel 1 goto no_python

echo [2/3] 创建独立运行环境 .venv...
if not exist ".venv\Scripts\python.exe" python -m venv .venv
if errorlevel 1 goto failed

echo [3/3] 安装项目和测试依赖...
".venv\Scripts\python.exe" -m pip install -e ".[dev]"
if errorlevel 1 goto failed

echo.
echo 安装成功。请双击“一键验证.bat”。
pause
exit /b 0

:no_python
echo.
echo 没有找到 Python。请先安装 Python 3.10 至 3.12，并勾选 Add Python to PATH。
pause
exit /b 1

:failed
echo.
echo 安装失败。请截图本窗口中的错误信息。
pause
exit /b 1
