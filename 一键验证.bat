@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto not_installed

echo ================================
echo 第一步：运行 9 个自动测试
echo ================================
".venv\Scripts\python.exe" -m pytest -q
if errorlevel 1 goto failed

echo.
echo ================================
echo 第二步：压缩示例长对话
echo ================================
".venv\Scripts\python.exe" -m context_compactor examples\sample_chat.txt -i "对比压缩前后的 Token 和质量" --root . --pretty -o outputs\my_result.json
if errorlevel 1 goto failed

echo.
echo ================================
echo 验证成功
echo ================================
echo 测试应显示：9 passed
echo 压缩结果：outputs\my_result.json
echo 请打开该文件，查看 metrics 中的 tokens_before、tokens_after 和 saving_rate。
start "" notepad "outputs\my_result.json"
pause
exit /b 0

:not_installed
echo 尚未安装。请先双击“一键安装.bat”。
pause
exit /b 1

:failed
echo.
echo 验证失败。请截图本窗口中的错误信息。
pause
exit /b 1
