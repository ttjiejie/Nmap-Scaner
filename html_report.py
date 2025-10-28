#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML报告生成模块
负责将扫描结果生成美观的HTML报告

Author: Security Researcher
License: MIT
"""

from datetime import datetime
import html


class HTMLReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self, results, scan_info):
        """
        初始化报告生成器
        :param results: 扫描结果字典
        :param scan_info: 扫描信息字典，包含开始时间、结束时间等
        """
        self.results = results
        self.scan_info = scan_info
    
    def generate(self, output_file):
        """
        生成HTML报告
        :param output_file: 输出文件路径
        """
        html_content = self._build_html()
        
        try:
            with open(output_file, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(html_content)
            print(f"\n[+] HTML报告已保存至: {output_file}")
        except Exception as e:
            print(f"[!] 保存报告时出错: {e}")
    
    def _build_html(self):
        """构建完整的HTML内容"""
        host_details_html = self._build_host_details()
        total_ports = sum(len(host_data['ports']) for host_data in self.results.values())
        
        duration = (self.scan_info['end_time'] - self.scan_info['start_time']).total_seconds()
        
        return self._get_html_template().format(
            nmap_version=self.scan_info.get('nmap_version', 'Nmap'),
            total_scanned=self.scan_info.get('total_scanned', 0),
            alive_hosts=len(self.results),
            total_ports=total_ports,
            duration=f"{duration:.2f}s",
            host_details=host_details_html,
            start_time=self.scan_info['start_time'].strftime('%Y-%m-%d %H:%M:%S'),
            end_time=self.scan_info['end_time'].strftime('%Y-%m-%d %H:%M:%S'),
            generate_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def _build_host_details(self):
        """构建主机详情HTML"""
        if not self.results:
            return '<div class="no-results">😔 未发现开放端口或存活主机</div>'
        
        html_parts = []
        
        for ip, host_data in sorted(self.results.items()):
            ports = host_data['ports']
            
            # 主机名
            hostnames = ', '.join(host_data['hostnames']) if host_data['hostnames'] else ''
            hostname_html = f'<div class="hostname">🏷️ {hostnames}</div>' if hostnames else ''
            
            # 操作系统信息
            os_html = ''
            if host_data['os']:
                os_name = host_data['os']['name']
                os_accuracy = host_data['os']['accuracy']
                os_html = f'<div class="os-info">💻 {os_name} ({os_accuracy}%)</div>'
            
            # 构建端口表格行
            ports_rows = self._build_ports_rows(ports)
            
            # 组装主机卡片
            host_card = f"""
            <div class="host-card">
                <div class="host-header" onclick="toggleHost(this)">
                    <div class="host-info">
                        <h3>📡 {ip} <span class="toggle-icon collapsed">▼</span></h3>
                        {hostname_html}
                    </div>
                    <div class="host-meta">
                        <span class="port-badge">{len(ports)} 个开放端口</span>
                        {os_html}
                    </div>
                </div>
                <div class="ports-content">
                    <table class="ports-table">
                        <thead>
                            <tr>
                                <th style="width: 60px; text-align: center;">#</th>
                                <th style="width: 100px;">端口/协议</th>
                                <th>服务详情</th>
                            </tr>
                        </thead>
                        <tbody>
                            {ports_rows}
                        </tbody>
                    </table>
                </div>
            </div>"""
            
            html_parts.append(host_card)
        
        return '\n'.join(html_parts)
    
    def _build_ports_rows(self, ports):
        """构建端口表格行"""
        rows = []
        
        for idx, port_info in enumerate(ports, 1):
            service_full = port_info['service']
            if port_info['product']:
                service_full += f" - {port_info['product']}"
            if port_info['version']:
                service_full += f" {port_info['version']}"
            if port_info['extra']:
                service_full += f" ({port_info['extra']})"
            
            badge_class = self._get_service_badge(port_info['service'])
            service_badge = f'<span class="badge {badge_class}">{port_info["service"]}</span>' if badge_class else ''
            
            # 脚本输出
            scripts_html = ''
            if port_info['scripts']:
                for script in port_info['scripts']:
                    scripts_html += f'''
                    <div class="script-output">
                        <div class="script-title">📜 {script["id"]}</div>
                        {script["output"]}
                    </div>'''
            
            row = f"""
            <tr>
                <td style="width: 60px; text-align: center;">{idx}</td>
                <td style="width: 100px;">
                    <span class="port-number">{port_info['port']}</span>
                    <div style="color: #999; font-size: 0.85em;">{port_info['protocol']}</div>
                </td>
                <td>
                    {service_badge}
                    <span class="service-name">{port_info['service']}</span>
                    <div class="service-detail">{service_full}</div>
                    {scripts_html}
                </td>
            </tr>"""
            
            rows.append(row)
        
        return '\n'.join(rows)
    
    @staticmethod
    def _get_service_badge(service):
        """根据服务类型返回对应的徽章样式"""
        service_lower = service.lower()
        if 'http' in service_lower and 'ssl' not in service_lower:
            return 'badge-http'
        elif 'https' in service_lower or 'ssl' in service_lower:
            return 'badge-https'
        elif 'ssh' in service_lower:
            return 'badge-ssh'
        elif any(db in service_lower for db in ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle']):
            return 'badge-database'
        return ''
    
    @staticmethod
    def _get_html_template():
        """返回HTML模板"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="description" content="Nmap端口扫描报告 - 资产端口扫描与服务识别">
    <meta name="generator" content="NmapScanner v2.0">
    <title>Nmap 端口扫描报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
            margin-top: 10px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .summary-item {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .summary-item:hover {{
            transform: translateY(-5px);
        }}
        
        .summary-item .icon {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .summary-item .label {{
            color: #666;
            font-size: 0.95em;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        .summary-item .value {{
            color: #667eea;
            font-size: 2.2em;
            font-weight: bold;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .controls {{
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        
        .btn-expand {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-expand:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-collapse {{
            background: #6c757d;
            color: white;
        }}
        
        .btn-collapse:hover {{
            background: #5a6268;
            transform: translateY(-2px);
        }}
        
        .host-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .host-card:hover {{
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
            border-color: #667eea;
        }}
        
        .host-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            cursor: pointer;
            user-select: none;
        }}
        
        .host-header:hover {{
            background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
        }}
        
        .toggle-icon {{
            font-size: 1.2em;
            transition: transform 0.3s ease;
            margin-left: 10px;
        }}
        
        .toggle-icon.collapsed {{
            transform: rotate(-90deg);
        }}
        
        .host-info {{
            flex: 1;
        }}
        
        .host-info h3 {{
            font-size: 1.4em;
            margin-bottom: 5px;
        }}
        
        .host-info .hostname {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .host-meta {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .port-badge {{
            background: rgba(255,255,255,0.25);
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 0.95em;
            font-weight: 600;
        }}
        
        .os-info {{
            background: rgba(255,255,255,0.15);
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.85em;
        }}
        
        .ports-content {{
            display: grid;
            grid-template-rows: 0fr;
            overflow: hidden;
            transition: grid-template-rows 0.3s ease-out, opacity 0.3s ease-out;
            opacity: 0;
        }}
        
        .ports-content.expanded {{
            grid-template-rows: 1fr;
            opacity: 1;
        }}
        
        .ports-content > * {{
            min-height: 0;
        }}
        
        .ports-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .ports-table thead {{
            background: linear-gradient(to right, #f8f9fa, #e9ecef);
        }}
        
        .ports-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 3px solid #667eea;
            font-size: 0.95em;
        }}
        
        .ports-table td {{
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
            vertical-align: top;
        }}
        
        .ports-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .port-number {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.15em;
        }}
        
        .service-name {{
            color: #764ba2;
            font-weight: 600;
            font-size: 1.05em;
        }}
        
        .service-detail {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
            line-height: 1.5;
        }}
        
        .script-output {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
            margin-top: 10px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85em;
            color: #333;
            white-space: pre-wrap;
            border-left: 3px solid #667eea;
        }}
        
        .script-title {{
            color: #667eea;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 25px;
            text-align: center;
            color: #666;
            border-top: 2px solid #e0e0e0;
            line-height: 1.8;
        }}
        
        .footer strong {{
            color: #333;
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px;
            color: #999;
            font-size: 1.3em;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-right: 5px;
        }}
        
        .badge-http {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .badge-https {{
            background: #e8f5e9;
            color: #388e3c;
        }}
        
        .badge-ssh {{
            background: #fff3e0;
            color: #f57c00;
        }}
        
        .badge-database {{
            background: #fce4ec;
            color: #c2185b;
        }}
        
        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .host-header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            
            .host-meta {{
                flex-direction: column;
                align-items: flex-start;
                width: 100%;
            }}
        }}
    </style>
    <script>
        // 切换单个主机的展开/折叠状态
        function toggleHost(element) {{
            const content = element.nextElementSibling;
            const icon = element.querySelector('.toggle-icon');
            
            // 使用 requestAnimationFrame 优化性能
            requestAnimationFrame(() => {{
                if (content.classList.contains('expanded')) {{
                    content.classList.remove('expanded');
                    icon.classList.add('collapsed');
                }} else {{
                    content.classList.add('expanded');
                    icon.classList.remove('collapsed');
                }}
            }});
        }}
        
        // 展开所有主机
        function expandAll() {{
            const contents = document.querySelectorAll('.ports-content');
            const icons = document.querySelectorAll('.toggle-icon');
            
            requestAnimationFrame(() => {{
                contents.forEach(content => {{
                    content.classList.add('expanded');
                }});
                
                icons.forEach(icon => {{
                    icon.classList.remove('collapsed');
                }});
            }});
        }}
        
        // 折叠所有主机
        function collapseAll() {{
            const contents = document.querySelectorAll('.ports-content');
            const icons = document.querySelectorAll('.toggle-icon');
            
            requestAnimationFrame(() => {{
                contents.forEach(content => {{
                    content.classList.remove('expanded');
                }});
                
                icons.forEach(icon => {{
                    icon.classList.add('collapsed');
                }});
            }});
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Nmap 端口扫描报告</h1>
            <p class="subtitle">基于 Nmap 的资产端口扫描与服务识别</p>
            <p style="font-size: 0.9em; margin-top: 10px; opacity: 0.8;">{nmap_version}</p>
        </div>
        
        <div class="summary">
            <div class="summary-item">
                <div class="icon">🎯</div>
                <div class="label">扫描目标</div>
                <div class="value">{total_scanned}</div>
            </div>
            <div class="summary-item">
                <div class="icon">✅</div>
                <div class="label">存活主机</div>
                <div class="value">{alive_hosts}</div>
            </div>
            <div class="summary-item">
                <div class="icon">🔓</div>
                <div class="label">开放端口总数</div>
                <div class="value">{total_ports}</div>
            </div>
            <div class="summary-item">
                <div class="icon">⏱️</div>
                <div class="label">扫描耗时</div>
                <div class="value">{duration}</div>
            </div>
        </div>
        
        <div class="content">
            <h2 style="margin-bottom: 20px; color: #333; font-size: 1.8em;">📊 扫描详情</h2>
            <div class="controls">
                <button class="btn btn-expand" onclick="expandAll()">
                    <span>🔽</span> 展开全部
                </button>
                <button class="btn btn-collapse" onclick="collapseAll()">
                    <span>🔼</span> 折叠全部
                </button>
            </div>
            {host_details}
        </div>
        
        <div class="footer">
            <p><strong>扫描开始时间:</strong> {start_time}</p>
            <p><strong>扫描结束时间:</strong> {end_time}</p>
            <p><strong>报告生成时间:</strong> {generate_time}</p>
            <p style="margin-top: 15px; color: #999; font-size: 0.9em;">
                Powered by Nmap - The Network Mapper
            </p>
        </div>
    </div>
</body>
</html>"""
