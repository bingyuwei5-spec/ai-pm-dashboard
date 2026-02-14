# -*- coding: utf-8 -*-
"""
AI+项目管理信息面板 - 内容搜索和抓取
使用阿里云通义千问API (已修复 exit code 1 错误)
"""

import json
import time
from datetime import datetime
from openai import OpenAI
import config

class AINewsCollector:
    """AI新闻和案例收集器"""
    
    def __init__(self):
        """初始化API客户端"""
        if not config.check_config():
            raise ValueError("配置不完整，请检查 QWEN_API_KEY")
        
        self.client = OpenAI(
            api_key=config.QWEN_API_KEY,
            base_url=config.QWEN_API_BASE
        )
        self.model = config.QWEN_MODEL
    
    def search_and_summarize(self, query, content_type='news', count=10):
        """搜索并总结内容"""
        try:
            if content_type == 'news':
                prompt = f"请列举关于'{query}'的5条最新AI新闻。以JSON数组格式返回，包含title, summary, priority, tags, date字段。不要包含markdown代码块标签。"
            else:
                prompt = f"请列举关于'{query}'的3个AI项目管理应用案例。以JSON数组格式返回，包含title, company, industry, description, impact字段。不要包含markdown代码块标签。"
            
            # 1. 修复 API 调用 (删除了 enable_search)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': '你是一个专业的AI分析师，只返回纯JSON格式数据。'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.7
            )
            
            # 2. 修复属性访问：必须加 [0]
            content = response.choices[0].message.content.strip()
            
            # 3. 修复字符串清理：正确处理 markdown 标记
            if '```' in content:
                content = content.replace('```json', '').replace('```', '').strip()
            
            # 解析JSON
            results = json.loads(content)
            print(f"✅ 成功获取 {len(results)} 条{content_type}内容")
            return results
            
        except Exception as e:
            print(f"❌ 处理失败 ({query}): {str(e)}")
            return []
    
    def collect_ai_news(self):
        print("\n📰 开始收集AI动态新闻...")
        all_news = []
        keywords = getattr(config, 'SEARCH_KEYWORDS', {}).get('ai_news', ["AI news", "LLM"])
        for keyword in keywords[:2]:
            news = self.search_and_summarize(query=keyword, content_type='news')
            all_news.extend(news)
            time.sleep(1)
        return self._deduplicate(all_news, 'title')[:10]
    
    def collect_pm_cases(self):
        print("\n💼 开始收集项目管理案例...")
        all_cases = []
        keywords = getattr(config, 'SEARCH_KEYWORDS', {}).get('pm_cases', ["AI PM case"])
        for keyword in keywords[:2]:
            cases = self.search_and_summarize(query=keyword, content_type='case')
            all_cases.extend(cases)
            time.sleep(1)
        return self._deduplicate(all_cases, 'title')[:6]
    
    def _deduplicate(self, items, key):
        seen = set()
        unique = []
        for item in items:
            val = item.get(key)
            if val and val not in seen:
                seen.add(val)
                unique.append(item)
        return unique

    def save_data(self, news, cases, filename='data.json'):
        data = {
            'update_time': datetime.now().strftime('%Y年%m月%d日 %H:%M'),
            'news': news,
            'cases': cases,
            'stats': {'news_count': len(news), 'case_count': len(cases)}
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 数据已保存到 {filename}")

def main():
    print("🚀 AI内容更新启动...")
    collector = AINewsCollector()
    news = collector.collect_ai_news()
    cases = collector.collect_pm_cases()
    collector.save_data(news, cases)
    print("✅ 更新任务执行完毕！")

if __name__ == '__main__':
    main()

