# -*- coding: utf-8 -*-
"""
AI+项目管理信息面板 - 内容抓取 (修复 Exit Code 1 与 格式 Bug)
"""

import json
import time
from datetime import datetime
from openai import OpenAI
import config

class AINewsCollector:
    def __init__(self):
        if not config.check_config():
            raise ValueError("配置不完整，请检查 QWEN_API_KEY")
        self.client = OpenAI(
            api_key=config.QWEN_API_KEY,
            base_url=config.QWEN_API_BASE
        )
        self.model = config.QWEN_MODEL

    def search_and_summarize(self, query, content_type='news'):
        """搜索并总结内容 - 修复 choices[0] 访问逻辑"""
        try:
            if content_type == 'news':
                prompt = f"请搜索关于'{query}'的最新AI新闻。必须用中文回答。返回一个JSON数组，包含: title, summary, priority (high或medium), tags (字符串数组), date (格式如'2026-02-14')。不要包含markdown代码块。"
            else:
                prompt = f"请搜索'{query}'的AI应用案例。必须用中文回答。返回一个JSON数组，包含: title, company, industry, description, impact (必须是一个包含3个短句的数组，如 ['效率提升', '成本降低'])。不要包含markdown代码块。"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': '你是一个专业的AI项目管理分析师。你必须使用中文回答。你只返回纯JSON数组，不输出任何其他多余解释。'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3  # 进一步降低随机性，确保格式和语言稳定
            )

            # ✅ 修复关键点：增加 [0] 索引
            content = response.choices[0].message.content.strip()
            
            # 清理 Markdown 标签
            if '```' in content:
                content = content.replace('```json', '').replace('```', '').strip()
            
            results = json.loads(content)
            
            # 确保 impact 是列表，防止页面垂直排列 Bug
            if content_type == 'case' and isinstance(results, list):
                for item in results:
                    if 'impact' in item and isinstance(item['impact'], str):
                        item['impact'] = [item['impact']]
            
            return results
        except Exception as e:
            print(f"❌ 运行中出错 ({query}): {str(e)}")
            return []

    def collect_ai_news(self):
        all_news = []
        keywords = getattr(config, 'SEARCH_KEYWORDS', {}).get('ai_news', ["AI 行业动态"])
        for kw in keywords[:2]:
            res = self.search_and_summarize(kw, 'news')
            if isinstance(res, list): all_news.extend(res)
            time.sleep(1)
        return all_news[:10]

    def collect_pm_cases(self):
        all_cases = []
        keywords = getattr(config, 'SEARCH_KEYWORDS', {}).get('pm_cases', ["AI 项目管理案例"])
        for kw in keywords[:2]:
            res = self.search_and_summarize(kw, 'case')
            if isinstance(res, list): all_cases.extend(res)
            time.sleep(1)
        return all_cases[:6]

    def save_data(self, news, cases):
        data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'news': news,
            'cases': cases,
            'stats': {'news_count': len(news), 'case_count': len(cases)}
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("🚀 开始执行中文数据抓取...")
    collector = AINewsCollector()
    news = collector.collect_ai_news()
    cases = collector.collect_pm_cases()
    collector.save_data(news, cases)
    print(f"✅ 成功! 抓取到 {len(news)} 条新闻和 {len(cases)} 个案例。")

if __name__ == '__main__':
    main()
