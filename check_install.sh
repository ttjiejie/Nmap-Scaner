#!/bin/bash
# Nmap Scanner 安装检查脚本

echo "========================================="
echo "Nmap Scanner 环境检查"
echo "========================================="
echo ""

# 检查Python版本
echo "[1/3] 检查Python版本..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python已安装: $PYTHON_VERSION"
    
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 6 ]; then
        echo "✓ Python版本满足要求 (≥3.6)"
    else
        echo "✗ Python版本过低，需要3.6或更高版本"
        exit 1
    fi
else
    echo "✗ 未检测到Python3，请先安装Python"
    exit 1
fi
echo ""

# 检查Nmap
echo "[2/3] 检查Nmap..."
if command -v nmap &> /dev/null; then
    NMAP_VERSION=$(nmap --version 2>&1 | head -n1)
    echo "✓ Nmap已安装: $NMAP_VERSION"
else
    echo "✗ 未检测到Nmap"
    echo "请安装Nmap:"
    echo "  Ubuntu/Debian: sudo apt-get install nmap"
    echo "  CentOS/RHEL:   sudo yum install nmap"
    echo "  macOS:         brew install nmap"
    exit 1
fi
echo ""

# 检查文件
echo "[3/3] 检查项目文件..."
FILES=("main.py" "html_report.py" "targets.txt")
ALL_OK=true

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file 存在"
    else
        echo "✗ $file 缺失"
        ALL_OK=false
    fi
done
echo ""

if [ "$ALL_OK" = true ]; then
    echo "========================================="
    echo "✓ 所有检查通过！"
    echo "========================================="
    echo ""
    echo "开始使用:"
    echo "  python3 main.py -f targets.txt"
    echo ""
    echo "查看帮助:"
    echo "  python3 main.py -h"
    echo ""
else
    echo "✗ 部分文件缺失，请检查项目完整性"
    exit 1
fi
