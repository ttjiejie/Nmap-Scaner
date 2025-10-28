#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级资产端口扫描与服务识别工具 - Nmap版本
支持批量扫描IP地址和CIDR网段
使用Nmap进行精确扫描和服务识别
输出HTML格式报告

Author: Security Researcher
License: MIT
Repository: https://github.com/yourusername/nmap-scanner
"""

import subprocess
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import os
import tempfile
import platform
from html_report import HTMLReportGenerator

# 版本信息
__version__ = '2.0.0'

# Python版本检查
if sys.version_info < (3, 6):
    print("[!] 错误: 需要Python 3.6或更高版本")
    print(f"[!] 当前版本: Python {sys.version}")
    sys.exit(1)

# 常见端口及对应服务(作为后备)
COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 81: 'HTTP-Alternate', 110: 'POP3', 111: 'RPC',
    135: 'MSRPC', 139: 'NetBIOS-SSN', 143: 'IMAP', 443: 'HTTPS',
    445: 'SMB', 465: 'SMTPS', 587: 'SMTP-Submission', 993: 'IMAPS',
    995: 'POP3S', 1080: 'SOCKS', 1433: 'MSSQL', 1521: 'Oracle',
    2181: 'Zookeeper', 2375: 'Docker', 3306: 'MySQL', 3389: 'RDP',
    4848: 'GlassFish', 5432: 'PostgreSQL', 5672: 'RabbitMQ',
    5984: 'CouchDB', 6379: 'Redis', 7001: 'WebLogic', 8000: 'HTTP-Alt',
    8001: 'HTTP-Alt', 8080: 'HTTP-Proxy', 8081: 'HTTP-Alt',
    8443: 'HTTPS-Alt', 8888: 'HTTP-Alt', 9000: 'PHP-FPM',
    9090: 'WebSphere', 9200: 'Elasticsearch', 9300: 'Elasticsearch-Transport',
    11211: 'Memcached', 27017: 'MongoDB', 50000: 'SAP', 50070: 'Hadoop',
}


class NmapScanner:
    """基于Nmap的端口扫描器"""
    
    def __init__(self, targets_file, output_file='scan_report.html', 
                 ports=None, scan_type='default', service_detect=True,
                 os_detect=False, script_scan=False, aggressive=False):
        """
        初始化扫描器
        :param targets_file: 目标文件路径
        :param output_file: 输出HTML报告路径
        :param ports: 要扫描的端口(格式: "80,443" 或 "1-1000" 或 None表示常见端口)
        :param scan_type: 扫描类型 (default/quick/full/stealth)
        :param service_detect: 是否进行服务版本探测
        :param os_detect: 是否进行操作系统探测
        :param script_scan: 是否运行默认脚本扫描
        :param aggressive: 是否使用激进模式(-A)
        """
        self.targets_file = targets_file
        self.output_file = output_file
        self.ports = ports
        self.scan_type = scan_type
        self.service_detect = service_detect
        self.os_detect = os_detect
        self.script_scan = script_scan
        self.aggressive = aggressive
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.total_scanned = 0
        self.nmap_version = None
        
        # 检查Nmap是否安装
        self.check_nmap()
    
    def check_nmap(self):
        """检查Nmap是否安装并检测系统平台"""
        nmap_cmd = 'nmap.exe' if platform.system() == 'Windows' else 'nmap'
        
        try:
            result = subprocess.run([nmap_cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5,
                                  encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.nmap_version = version_line
                print(f"[+] {version_line}")
                print(f"[+] 系统平台: {platform.system()} {platform.release()}")
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            print(f"[!] 错误: 未检测到Nmap,请先安装Nmap")
            print(f"[!] 下载地址: https://nmap.org/download.html")
            if platform.system() == 'Windows':
                print(f"[!] Windows用户: 安装后请确保Nmap在系统PATH中")
            elif platform.system() == 'Linux':
                print(f"[!] Linux用户: sudo apt-get install nmap 或 sudo yum install nmap")
            elif platform.system() == 'Darwin':
                print(f"[!] macOS用户: brew install nmap")
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print("[!] 错误: Nmap命令超时")
            sys.exit(1)
        except Exception as e:
            print(f"[!] 检查Nmap时发生错误: {e}")
            sys.exit(1)
    
    def load_targets(self):
        """从文件加载目标列表"""
        targets = []
        try:
            with open(self.targets_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        targets.append(line)
        except FileNotFoundError:
            print(f"[!] 错误: 找不到目标文件 '{self.targets_file}'")
            sys.exit(1)
        except Exception as e:
            print(f"[!] 读取目标文件时出错: {e}")
            sys.exit(1)
        
        return targets
    
    def build_nmap_command(self, target):
        """构建Nmap扫描命令"""
        cmd = ['nmap']
        
        # 扫描类型
        if self.scan_type == 'quick':
            cmd.append('-T4')  # 快速扫描
        elif self.scan_type == 'full':
            cmd.append('-T3')  # 较慢但更准确
            cmd.append('-Pn')  # 跳过主机发现
        elif self.scan_type == 'stealth':
            cmd.append('-sS')  # SYN扫描
            cmd.append('-T2')  # 慢速扫描
        else:
            cmd.append('-T4')  # 默认快速扫描
        
        # 激进模式(包含OS检测、版本检测、脚本扫描、traceroute)
        if self.aggressive:
            cmd.append('-A')
        else:
            # 服务版本探测
            if self.service_detect:
                cmd.append('-sV')
            
            # 操作系统探测
            if self.os_detect:
                cmd.append('-O')
            
            # 脚本扫描
            if self.script_scan:
                cmd.append('-sC')
        
        # 端口范围
        if self.ports:
            cmd.extend(['-p', self.ports])
        else:
            # 扫描常见端口
            common_ports_str = ','.join(map(str, sorted(COMMON_PORTS.keys())))
            cmd.extend(['-p', common_ports_str])
        
        # 输出格式(XML格式便于解析)
        temp_xml = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False)
        temp_xml.close()
        cmd.extend(['-oX', temp_xml.name])
        
        # 禁用DNS解析加速扫描
        cmd.append('-n')
        
        # 目标
        cmd.append(target)
        
        return cmd, temp_xml.name
    
    def parse_nmap_xml(self, xml_file):
        """解析Nmap XML输出"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            host_results = {}
            
            for host in root.findall('host'):
                # 检查主机状态
                status = host.find('status')
                if status is None or status.get('state') != 'up':
                    continue
                
                # 获取IP地址
                address = host.find('address')
                if address is None:
                    continue
                ip = address.get('addr')
                
                # 获取主机名
                hostnames = []
                for hostname in host.findall('.//hostname'):
                    name = hostname.get('name')
                    if name:
                        hostnames.append(name)
                
                # 获取操作系统信息
                os_info = None
                os_match = host.find('.//osmatch')
                if os_match is not None:
                    os_info = {
                        'name': os_match.get('name'),
                        'accuracy': os_match.get('accuracy')
                    }
                
                # 获取端口信息
                ports_data = []
                ports = host.find('ports')
                if ports is not None:
                    for port in ports.findall('port'):
                        state = port.find('state')
                        if state is None or state.get('state') != 'open':
                            continue
                        
                        port_id = port.get('portid')
                        protocol = port.get('protocol')
                        
                        # 服务信息
                        service = port.find('service')
                        service_name = 'unknown'
                        service_product = ''
                        service_version = ''
                        service_extra = ''
                        
                        if service is not None:
                            service_name = service.get('name', 'unknown')
                            service_product = service.get('product', '')
                            service_version = service.get('version', '')
                            service_extra = service.get('extrainfo', '')
                        
                        # 脚本输出
                        scripts = []
                        for script in port.findall('script'):
                            script_id = script.get('id')
                            script_output = script.get('output', '')
                            scripts.append({
                                'id': script_id,
                                'output': script_output
                            })
                        
                        ports_data.append({
                            'port': int(port_id),
                            'protocol': protocol,
                            'service': service_name,
                            'product': service_product,
                            'version': service_version,
                            'extra': service_extra,
                            'scripts': scripts
                        })
                
                if ports_data:
                    host_results[ip] = {
                        'hostnames': hostnames,
                        'os': os_info,
                        'ports': sorted(ports_data, key=lambda x: x['port'])
                    }
            
            return host_results
            
        except Exception as e:
            print(f"[!] 解析XML文件出错: {e}")
            return {}
    
    def scan(self):
        """执行扫描"""
        print("[*] 正在加载目标...")
        targets = self.load_targets()
        
        if not targets:
            print("[!] 没有有效的目标需要扫描")
            return
        
        print(f"[*] 共需扫描 {len(targets)} 个目标")
        print(f"[*] 扫描类型: {self.scan_type}")
        print(f"[*] 服务识别: {'开启' if self.service_detect else '关闭'}")
        print(f"[*] OS识别: {'开启' if self.os_detect else '关闭'}")
        print(f"[*] 脚本扫描: {'开启' if self.script_scan else '关闭'}")
        print("-" * 60)
        
        self.start_time = datetime.now()
        
        for idx, target in enumerate(targets, 1):
            print(f"\n[*] [{idx}/{len(targets)}] 正在扫描目标: {target}")
            
            # 构建Nmap命令
            cmd, xml_file = self.build_nmap_command(target)
            
            print(f"[*] 执行命令: {' '.join(cmd)}")
            
            try:
                # 执行Nmap扫描
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                # 实时输出进度
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        print(f"    {line}")
                
                process.wait()
                
                # 解析结果
                if process.returncode == 0:
                    results = self.parse_nmap_xml(xml_file)
                    if results:
                        self.results.update(results)
                        for ip, data in results.items():
                            print(f"[+] {ip} - 发现 {len(data['ports'])} 个开放端口")
                    else:
                        print(f"[!] {target} - 未发现开放端口")
                else:
                    print(f"[!] 扫描 {target} 时出错")
                
                # 清理临时文件
                try:
                    os.unlink(xml_file)
                except:
                    pass
                    
            except Exception as e:
                print(f"[!] 扫描 {target} 时发生异常: {e}")
                continue
            
            self.total_scanned += 1
        
        self.end_time = datetime.now()
        
        print("\n" + "=" * 60)
        print(f"[*] 扫描完成!")
        print(f"[*] 发现 {len(self.results)} 个存活主机")
        print(f"[*] 耗时: {(self.end_time - self.start_time).total_seconds():.2f} 秒")
    
    def generate_html_report(self):
        """生成HTML格式报告"""
        scan_info = {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'total_scanned': self.total_scanned,
            'nmap_version': self.nmap_version
        }
        
        report_generator = HTMLReportGenerator(self.results, scan_info)
        report_generator.generate(self.output_file)


def main():
    banner = f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   🔍 轻量级资产端口扫描与服务识别工具 v{__version__}      ║
    ║   基于 Nmap 的高精度端口扫描和服务识别                  ║
    ║   Python {sys.version_info.major}.{sys.version_info.minor} | {platform.system()}                                        ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    
    parser = argparse.ArgumentParser(
        description='基于Nmap的端口扫描与服务识别工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基础扫描
  python main.py -f targets.txt
  
  # 扫描指定端口
  python main.py -f targets.txt -p 80,443,8080
  
  # 扫描端口范围
  python main.py -f targets.txt -p 1-10000
  
  # 快速扫描模式
  python main.py -f targets.txt --scan-type quick
  
  # 完整扫描(含服务版本、OS检测、脚本)
  python main.py -f targets.txt -sV -O -sC
  
  # 激进模式(全面扫描)
  python main.py -f targets.txt -A
  
  # 隐蔽扫描
  python main.py -f targets.txt --scan-type stealth
        """
    )
    
    parser.add_argument('-f', '--file', required=True,
                       help='目标文件路径(支持IP、CIDR、域名)')
    parser.add_argument('-o', '--output', default='scan_report.html',
                       help='输出HTML报告文件名(默认: scan_report.html)')
    parser.add_argument('-p', '--ports',
                       help='端口范围(如: 80,443 或 1-1000),默认扫描常见端口')
    parser.add_argument('--scan-type', choices=['default', 'quick', 'full', 'stealth'],
                       default='default', help='扫描类型')
    parser.add_argument('-sV', '--service-version', action='store_true',
                       help='启用服务版本探测')
    parser.add_argument('-O', '--os-detect', action='store_true',
                       help='启用操作系统探测(需要root/管理员权限)')
    parser.add_argument('-sC', '--script-scan', action='store_true',
                       help='启用默认脚本扫描')
    parser.add_argument('-A', '--aggressive', action='store_true',
                       help='激进模式(包含-sV -O -sC --traceroute)')
    
    args = parser.parse_args()
    
    # 创建扫描器实例
    scanner = NmapScanner(
        targets_file=args.file,
        output_file=args.output,
        ports=args.ports,
        scan_type=args.scan_type,
        service_detect=args.service_version,
        os_detect=args.os_detect,
        script_scan=args.script_scan,
        aggressive=args.aggressive
    )
    
    try:
        scanner.scan()
        scanner.generate_html_report()
        print("\n" + "=" * 60)
        print("[*] 🎉 扫描任务全部完成!")
        print(f"[*] 📄 报告文件: {os.path.abspath(args.output)}")
        print(f"[*] 💾 文件大小: {os.path.getsize(args.output) / 1024:.2f} KB")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n[!] 用户中断扫描")
        sys.exit(0)
    except PermissionError as e:
        print(f"\n[!] 权限错误: {e}")
        print("[!] 提示: 某些扫描选项(如-O)需要管理员/root权限")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] 发生错误: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
