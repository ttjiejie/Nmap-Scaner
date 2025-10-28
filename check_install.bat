@echo off
REM Nmap Scanner 安装检查脚本 (Windows)

echo =========================================
echo Nmap Scanner 环境检查
echo =========================================
echo.

REM 检查Python
echo [1/3] 检查Python版本...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python已安装: !PYTHON_VERSION!
    
    REM 检查Python版本
    python -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)"
    if %errorlevel% equ 0 (
        echo [OK] Python版本满足要求 (>=3.6^)
    ) else (
        echo [FAIL] Python版本过低，需要3.6或更高版本
        pause
        exit /b 1
    )
) else (
    echo [FAIL] 未检测到Python，请先安装Python 3.6+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

REM 检查Nmap
echo [2/3] 检查Nmap...
nmap --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=1-3" %%i in ('nmap --version ^| findstr "Nmap version"') do (
        echo [OK] Nmap已安装: %%i %%j %%k
    )
) else (
    echo [FAIL] 未检测到Nmap
    echo 请安装Nmap: https://nmap.org/download.html
    echo 安装后请确保Nmap在系统PATH中
    pause
    exit /b 1
)
echo.

REM 检查文件
echo [3/3] 检查项目文件...
set ALL_OK=1

if exist "main.py" (
    echo [OK] main.py 存在
) else (
    echo [FAIL] main.py 缺失
    set ALL_OK=0
)

if exist "html_report.py" (
    echo [OK] html_report.py 存在
) else (
    echo [FAIL] html_report.py 缺失
    set ALL_OK=0
)

if exist "targets.txt" (
    echo [OK] targets.txt 存在
) else (
    echo [FAIL] targets.txt 缺失
    set ALL_OK=0
)
echo.

if %ALL_OK% equ 1 (
    echo =========================================
    echo [OK] 所有检查通过！
    echo =========================================
    echo.
    echo 开始使用:
    echo   python main.py -f targets.txt
    echo.
    echo 查看帮助:
    echo   python main.py -h
    echo.
) else (
    echo [FAIL] 部分文件缺失，请检查项目完整性
    pause
    exit /b 1
)

pause
