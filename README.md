# 🔍 Nmap端口扫描与服务识别工具

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.6+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Nmap-7.0+-red.svg" alt="Nmap">
</p>

一个基于Python和Nmap开发的高效端口扫描工具，专为安全研究和渗透测试设计。支持批量扫描IP地址和CIDR网段，自动识别服务版本和操作系统，生成美观的可交互HTML报告。

## ✨ 主要特性

- 🚀 **基于Nmap引擎** - 利用Nmap强大的扫描和服务识别能力
- 📋 **批量目标支持** - 支持IP地址、CIDR网段、域名等多种格式
- 🎯 **精确服务识别** - 自动识别服务版本、操作系统、运行脚本探测
- 📊 **精美HTML报告** - 生成可折叠的可视化报告，清晰展示扫描结果
- ⚙️ **灵活配置** - 支持多种扫描模式、自定义端口范围等参数
- 💡 **模块化设计** - 代码结构清晰，易于扩展和维护
- 🌍 **跨平台支持** - 完美支持Windows、Linux和macOS

## 📸 效果预览

### 扫描过程
```
╔═══════════════════════════════════════════════════════════╗
║   🔍 轻量级资产端口扫描与服务识别工具 v2.0.0            ║
║   基于 Nmap 的高精度端口扫描和服务识别                  ║
╚═══════════════════════════════════════════════════════════╝

[+] Nmap version 7.98
[+] 系统平台: Windows 10
[*] 共需扫描 1 个目标
[*] 扫描类型: quick
[+] 192.168.1.100 - 发现 15 个开放端口
```

### HTML报告特点
- ✅ 折叠式主机卡片，点击展开查看详情
- ✅ 服务类型徽章标识（HTTP/HTTPS/SSH/数据库等）
- ✅ 完整的端口、协议、服务版本信息
- ✅ NSE脚本扫描结果展示
- ✅ 操作系统识别信息
- ✅ 响应式设计，支持移动端

## 📁 项目结构

```
PortScan/
├── main.py              # 主程序 - 扫描逻辑和CLI
├── html_report.py       # HTML报告生成模块
├── targets.txt          # 目标列表示例
├── requirements.txt     # Python依赖（无第三方库）
├── .gitignore          # Git忽略配置
├── LICENSE             # MIT开源许可证
└── README.md           # 项目文档
```

## 📦 安装

### 1. 环境要求

- **Python**: 3.6或更高版本
- **Nmap**: 7.0或更高版本
- **操作系统**: Windows / Linux / macOS

### 2. 安装Nmap

#### Windows
1. 下载安装包: https://nmap.org/download.html
2. 运行安装程序
3. 确保将Nmap添加到系统PATH

#### Linux
```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install nmap

# CentOS/RHEL
sudo yum install nmap

# Fedora
sudo dnf install nmap
```

#### macOS
```bash
# 使用Homebrew
brew install nmap

# 或从官网下载.dmg安装包
# https://nmap.org/download.html
```

### 3. 克隆项目

```bash
git clone https://github.com/yourusername/nmap-scanner.git
cd nmap-scanner
```

### 4. 验证安装

```bash
# 检查Python版本
python --version  # 应显示 Python 3.6+

# 检查Nmap版本
nmap --version    # 应显示 Nmap 7.0+

# 查看工具帮助
python main.py -h
```

## 🚀 快速开始

### 1. 准备目标文件

创建 `targets.txt` 文件，每行一个目标：

```txt
# 单个IP地址
192.168.1.100

# CIDR网段
192.168.1.0/24
10.0.0.0/16

# 域名
www.example.com
api.example.com
```

### 2. 基础扫描

```bash
# 扫描常见端口
python main.py -f targets.txt

# 快速扫描模式
python main.py -f targets.txt --scan-type quick

# 指定输出文件
python main.py -f targets.txt -o my_report.html
```

### 3. 高级扫描

```bash
# 扫描指定端口
python main.py -f targets.txt -p 80,443,8080,3306

# 扫描端口范围
python main.py -f targets.txt -p 1-10000

# 服务版本探测
python main.py -f targets.txt -sV

# 完整扫描（版本+OS+脚本）
python main.py -f targets.txt -sV -O -sC

# 激进模式（需要管理员权限）
python main.py -f targets.txt -A
```

## 📖 详细文档

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-f, --file` | 目标文件路径（必需） | - |
| `-o, --output` | 输出HTML报告文件名 | scan_report.html |
| `-p, --ports` | 端口范围（如: 80,443 或 1-1000） | 常见端口 |
| `--scan-type` | 扫描类型（default/quick/full/stealth） | default |
| `-sV, --service-version` | 启用服务版本探测 | 关闭 |
| `-O, --os-detect` | 启用OS探测（需管理员权限） | 关闭 |
| `-sC, --script-scan` | 启用NSE脚本扫描 | 关闭 |
| `-A, --aggressive` | 激进模式（含-sV -O -sC） | 关闭 |

### 扫描类型说明

- **default**: 标准快速扫描，适合日常使用
- **quick**: T4快速扫描，速度最快
- **full**: 完整准确扫描，跳过主机发现
- **stealth**: 隐蔽SYN扫描，速度较慢但更隐蔽

### 内置常见端口

工具预设了50+个常见服务端口：

- **Web服务**: 80(HTTP), 443(HTTPS), 8080, 8443
- **数据库**: 3306(MySQL), 5432(PostgreSQL), 1433(MSSQL), 27017(MongoDB), 6379(Redis)
- **远程访问**: 22(SSH), 3389(RDP), 23(Telnet)
- **邮件服务**: 25(SMTP), 110(POP3), 143(IMAP)
- **其他服务**: Docker, Elasticsearch, RabbitMQ, Memcached等

## 🎯 使用场景

- 📌 **资产盘点** - 快速发现网络中的存活主机和开放服务
- 🔒 **安全评估** - 检查是否有意外开放的高危端口
- 🎓 **学习实践** - 理解Nmap使用和端口扫描原理
- 🧪 **渗透测试** - 信息收集阶段的快速探测工具
- 🏢 **网络管理** - 监控内网服务和端口变化

## 🔧 高级用法

### 组合扫描策略

```bash
# 快速识别Web服务
python main.py -f targets.txt -p 80,443,8080,8000,8443,8888 -sV

# 数据库服务探测
python main.py -f targets.txt -p 3306,5432,1433,27017,6379 -sV

# 内网全面扫描
python main.py -f internal_network.txt -p 1-65535 --scan-type full -sV

# 隐蔽扫描（避免被IDS检测）
python main.py -f targets.txt --scan-type stealth -sV
```

### 性能调优

```bash
# 小规模目标 - 使用激进模式
python main.py -f targets.txt -A

# 大规模扫描 - 仅扫描关键端口
python main.py -f large_network.txt -p 22,80,443 --scan-type quick

# 精确扫描 - 完整服务识别
python main.py -f targets.txt -sV -sC --scan-type full
```

## ⚠️ 注意事项

1. **合法使用** - 仅对授权目标进行扫描，未经授权的扫描可能违法
2. **权限要求** - OS检测(`-O`)需要管理员/root权限
3. **网络影响** - 大规模扫描可能对网络造成压力
4. **防火墙** - 部分防火墙可能检测并阻止扫描行为
5. **误报率** - 服务识别基于特征匹配，可能存在误判

## 🐛 故障排除

### 常见问题

**Q: 提示"未检测到Nmap"**
```bash
# 检查Nmap是否安装
nmap --version

# Windows: 确保Nmap在系统PATH中
# Linux: sudo apt-get install nmap
# macOS: brew install nmap
```

**Q: 权限错误**
```bash
# Linux/macOS - 使用sudo
sudo python main.py -f targets.txt -O

# Windows - 以管理员身份运行PowerShell/CMD
```

**Q: 扫描速度慢**
```bash
# 使用快速扫描模式
python main.py -f targets.txt --scan-type quick

# 减少扫描端口数量
python main.py -f targets.txt -p 80,443,22
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Nmap Project](https://nmap.org/) - 提供强大的网络扫描引擎
- 所有贡献者和使用者

## 📞 联系方式

- **作者**: Security Researcher
- **邮箱**: your.email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)

---

**⚠️ 免责声明**: 本工具仅用于授权的安全测试，使用者应遵守当地法律法规。开发者不对任何滥用行为负责。

<p align="center">Made with ❤️ for Security Community</p>
