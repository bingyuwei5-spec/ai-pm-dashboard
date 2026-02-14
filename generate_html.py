# -*- coding: utf-8 -*-
"""
AI+项目管理信息面板 - 网页生成器
"""

import json
from datetime import datetime
import config
import os

class DashboardGenerator:
    """信息面板网页生成器"""
    
    def __init__(self, data_file='data.json'):
        """初始化生成器"""
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self):
        """加载数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 数据文件不存在: {self.data_file}")
            return None
    
    def generate_news_html(self, news_list):
        """生成AI动态HTML"""
        html = ""
        for news in news_list:
            priority_class = 'priority-high' if news.get('priority') == 'high' else 'priority-medium'
            priority_emoji = '🔴' if news.get('priority') == 'high' else '🟡'
            priority_text = '重要' if news.get('priority') == 'high' else '关注'
            
            tags_html = ''.join([f'<span class="news-tag">{tag}</span>' for tag in news.get('tags', [])])
            
            html += f'''
                <div class="news-item">
                    <div class="news-title">
                        {news.get('title', '未知标题')}
                        <span class="priority-badge {priority_class}">{priority_emoji} {priority_text}</span>
                    </div>
                    <div class="news-summary">
                        {news.get('summary', '暂无摘要')}
                    </div>
                    <div class="news-meta">
                        <div>
                            {tags_html}
                        </div>
                        <span>{news.get('date', '未知日期')}</span>
                    </div>
                </div>
            '''
        return html
    
    def generate_cases_html(self, cases_list):
        """生成案例HTML"""
        html = ""
        for case in cases_list:
            impact_html = '<br>'.join([f"• {item}" for item in case.get('impact', [])])
            
            html += f'''
                <div class="case-item">
                    <div class="case-title">{case.get('title', '未知案例')}</div>
                    <span class="case-company">{case.get('industry', '行业')} · {case.get('company', '未知公司')}</span>
                    <div class="case-description">
                        {case.get('description', '暂无描述')}
                    </div>
                    <div class="case-impact">
                        <div class="impact-title">📊 实际效果</div>
                        <div class="impact-value">{impact_html}</div>
                    </div>
                </div>
            '''
        return html
    
    def generate_html(self, output_file='index.html'):
        """生成完整的HTML页面"""
        if not self.data:
            print("❌ 无数据，无法生成网页")
            return False
        
        news_html = self.generate_news_html(self.data.get('news', []))
        cases_html = self.generate_cases_html(self.data.get('cases', []))
        
        stats = self.data.get('stats', {})
        update_time = self.data.get('update_time', datetime.now().strftime('%Y年%m月%d日 %H:%M'))
        
        html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.SITE_TITLE}</title>
    <meta name="description" content="{config.SITE_DESCRIPTION}">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 32px;
            color: #2d3748;
            margin-bottom: 10px;
        }}

        .header p {{
            color: #718096;
            font-size: 16px;
        }}

        .update-time {{
            display: inline-block;
            background: #e6fffa;
            color: #047857;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 14px;
            margin-top: 10px;
        }}

        .auto-badge {{
            display: inline-block;
            background: #fef3c7;
            color: #d97706;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 14px;
            margin-left: 10px;
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}

        @media (max-width: 968px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
        }}

        .panel {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .panel-header {{
            display: flex;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f7fafc;
        }}

        .panel-icon {{
            font-size: 32px;
            margin-right: 15px;
        }}

        .panel-title {{
            font-size: 24px;
            color: #2d3748;
            font-weight: 600;
        }}

        .news-item {{
            margin-bottom: 25px;
            padding: 20px;
            background: #f7fafc;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }}

        .news-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }}

        .news-title {{
            font-size: 18px;
            color: #2d3748;
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
        }}

        .priority-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }}

        .priority-high {{
            background: #fee2e2;
            color: #dc2626;
        }}

        .priority-medium {{
            background: #fef3c7;
            color: #d97706;
        }}

        .news-summary {{
            color: #4a5568;
            font-size: 15px;
            line-height: 1.6;
            margin-bottom: 10px;
        }}

        .news-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
            font-size: 13px;
            color: #a0aec0;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .news-tag {{
            display: inline-block;
            background: #e0e7ff;
            color: #4f46e5;
            padding: 4px 10px;
            border-radius: 6px;
            margin-right: 6px;
            font-size: 12px;
        }}

        .case-item {{
            margin-bottom: 25px;
            padding: 20px;
            background: #f0fdf4;
            border-radius: 12px;
            border-left: 4px solid #10b981;
            transition: all 0.3s ease;
        }}

        .case-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
        }}

        .case-title {{
            font-size: 18px;
            color: #2d3748;
            font-weight: 600;
            margin-bottom: 10px;
        }}

        .case-company {{
            display: inline-block;
            background: #d1fae5;
            color: #047857;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
        }}

        .case-description {{
            color: #4a5568;
            font-size: 15px;
            line-height: 1.6;
            margin-bottom: 12px;
        }}

        .case-impact {{
            background: white;
            padding: 12px;
            border-radius: 8px;
            margin-top: 12px;
        }}

        .impact-title {{
            font-size: 13px;
            color: #059669;
            font-weight: 600;
            margin-bottom: 6px;
        }}

        .impact-value {{
            color: #2d3748;
            font-size: 14px;
            line-height: 1.8;
        }}

        .stats-bar {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }}

        .stat-item {{
            flex: 1;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}

        .stat-number {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .stat-label {{
            font-size: 12px;
            opacity: 0.9;
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
            font-size: 14px;
            opacity: 0.9;
        }}

        .footer a {{
            color: white;
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 {config.SITE_TITLE}</h1>
            <p>{config.SITE_DESCRIPTION}</p>
            <span class="update-time">📅 最后更新: {update_time}</span>
            <span class="auto-badge">🤖 自动更新 · 每天10:30</span>
        </div>

        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-number">{stats.get('news_count', 0)}</div>
                <div class="stat-label">今日AI动态</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{stats.get('case_count', 0)}</div>
                <div class="stat-label">实践案例</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">自动</div>
                <div class="stat-label">智能更新</div>
            </div>
        </div>

        <div class="dashboard">
            <!-- 左侧：AI重要动态 -->
            <div class="panel">
                <div class="panel-header">
                    <span class="panel-icon">🔥</span>
                    <h2 class="panel-title">AI重要动态</h2>
                </div>
                {news_html}
            </div>

            <!-- 右侧：AI+项目管理案例 -->
            <div class="panel">
                <div class="panel-header">
                    <span class="panel-icon">💡</span>
                    <h2 class="panel-title">AI+项目管理实践</h2>
                </div>
                {cases_html}
            </div>
        </div>

        <div class="footer">
            <p>⚡ 由阿里云通义千问AI驱动 | 每天10:30自动更新</p>
            <p>🔗 <a href="https://github.com/yourusername/ai-pm-dashboard" target="_blank">查看项目源代码</a></p>
        </div>
    </div>
</body>
</html>'''
        
        # 确保输出目录存在
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(config.OUTPUT_DIR, output_file)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"✅ 网页已生成: {output_path}")
        return True

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🎨 生成网页...")
    print("=" * 60)
    
    generator = DashboardGenerator()
    success = generator.generate_html()
    
    if success:
        print("=" * 60)
        print("✅ 网页生成完成！")
        print(f"📁 文件位置: {config.OUTPUT_DIR}/index.html")
        print("=" * 60)
    
    return success

if __name__ == '__main__':
    main()
