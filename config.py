# -*- coding: utf-8 -*-
"""
AI+项目管理信息面板 - 配置文件
每天10:30自动更新
"""

import os

# ===== 阿里云通义千问 API 配置 =====
# 请在 GitHub Secrets 中设置 QWEN_API_KEY
QWEN_API_KEY = os.getenv('QWEN_API_KEY', '')
QWEN_MODEL = 'qwen-plus'  # 可选: qwen-turbo (便宜), qwen-plus (推荐), qwen-max (最强)
QWEN_API_BASE = 'https://dashscope.aliyuncs.com/compatible-mode/v1'

# ===== 内容配置 =====
# 每天更新的条数
NEWS_COUNT = 10  # AI动态数量
CASE_COUNT = 10  # 实践案例数量

# 搜索关键词
SEARCH_KEYWORDS = {
    'ai_news': [
        'AI latest developments 2026',
        'artificial intelligence breakthroughs',
        'AI models releases',
        'AI industry news',
        'generative AI updates'
    ],
    'pm_cases': [
        'AI project management tools',
        'AI project management case study',
        'artificial intelligence project management',
        'AI automation project management',
        'AI project planning tools'
    ]
}

# ===== 更新时间配置 =====
# GitHub Actions 使用 UTC 时间
# 中国时间 10:30 = UTC 02:30
UPDATE_TIME_CRON = '30 2 * * *'  # 每天 UTC 02:30 (北京时间 10:30)

# ===== 网页配置 =====
SITE_TITLE = 'AI+项目管理 智能信息面板'
SITE_DESCRIPTION = '实时追踪AI动态 · 发现最佳实践案例 · 提升项目管理技能'
SITE_AUTHOR = 'AI Assistant'

# ===== 其他配置 =====
# 缓存过期时间（小时）
CACHE_EXPIRE_HOURS = 24

# 日志级别
LOG_LEVEL = 'INFO'

# 输出目录
OUTPUT_DIR = 'docs'  # GitHub Pages 会自动发布这个目录

# ===== API 配置提示 =====
def check_config():
    """检查配置是否完整"""
    if not QWEN_API_KEY:
        print("⚠️  警告: 未设置 QWEN_API_KEY")
        print("请在 GitHub Secrets 中添加 QWEN_API_KEY")
        print("获取方式: https://help.aliyun.com/zh/model-studio/")
        return False
    return True
