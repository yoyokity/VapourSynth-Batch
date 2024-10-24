@echo off
chcp 65001

:: 获取当前批处理文件所在的目录
set script_dir=%~dp0

:: 激活虚拟环境
call "%script_dir%venv\Scripts\activate"

if "%~1"=="" (
    echo 请将多个文件拖放到此批处理文件上。
    pause
    exit /b
)

:: 确认 main.py 文件存在
if not exist "%script_dir%main.py" (
    echo 找不到 main.py 文件，请确认文件存在。
    pause
    exit /b
)

:: 运行 Python 脚本
python "%script_dir%main.py" %*

pause
