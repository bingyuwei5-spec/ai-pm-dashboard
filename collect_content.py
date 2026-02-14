# -*- coding: utf-8 -*-
"""
AI+项目管理信息面板 - 内容搜索和抓取
使用阿里云通义千问API
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
        
        # 使用 OpenAI 兼容接口
        self.client = OpenAI(
            api_key=config.QWEN_API_KEY,
            base_url=config.QWEN_API_BASE
        )
        self.model = config.QWEN_MODEL
    
    def search_and_summarize(self, query, content_type='news', count=10):
        """
        搜索并总结内容
        """
        try:
            # 构建提示词
            if content_type == 'news':
                prompt = f"""请总结关于"{query}"的最新AI领域动态。

要求：
1. 找到{count}条最重要、最新的AI领域进展
2. 每条新闻包含：标题、摘要（2-3句话）、重要性级别（high/medium）、相关标签
3. 优先选择对项目管理、生产力工具有影响的AI进展
4. 按重要性排序

请严格以JSON格式返回，格式如下：
[
  {{
    "title": "新闻标题",
    "summary": "新闻摘要内容",
    "priority": "high",
    "tags": ["标签1", "标签2"],
    "date": "{datetime.now().strftime('%Y年%m月')}"
  }}
]

只返回JSON，不要包含任何MarkDown代码块标记或其他文字。"""
            
            else:  # case
                prompt = f"""请列举关于"{query}"的实际应用案例。

要求：
1. 找到{count}个AI在项目管理中的真实应用案例
2. 每个案例包含：标题、公司/行业、描述、量化效果
3. 优先选择有具体数据支撑的案例

请严格以JSON格式返回，格式如下：
[
  {{
    "title": "案例标题",
    "company": "公司名称",
    "industry": "行业类别",
    "description": "详细描述AI如何应用",
    "impact": ["效果1", "效果2"]
  }}
]

只返回JSON，不要包含任何MarkDown代码块标记或其他文字。"""
            
            # 调用通义千问API
            # 注意：此处删除了会导致报错的 enable_search=True 参数
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个专业的AI信息分析师，专注于AI+项目管理领域。请直接返回JSON格式的数据。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.7
            )
            
            # 解析响应
            content = response.choices[0].message.content.strip()
            
            # 清理可能的 Markdown 标记
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            # 解析JSON
            results = json.loads(content)
            
            print(f"✅ 成功获取 {len(results)} 条{content_type}内容")
            return results
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            return []
        except Exception as e:
            print(f"❌ 运行失败: {e}")
            return []
    
    def collect_ai_news(self):
        """收集AI动态新闻"""
        print("\n📰 开始收集AI动态新闻...")
        all_news = []
        
        # 默认从配置中读取关键词，如果没有则使用备用
        keywords = getattr(config, 'SEARCH_KEYWORDS', {}).get('ai_news', ["AI latest developments", "Project Management AI"])
        
        for keyword in keywords[:2]:
            print(f"  🔍 处理关键词: {keyword}")
            news = self.search_and_summarize(query=keyword, content_type='news', count=5)
            all_news.extend(news)
            time.sleep(1)
        
        return self._deduplicate(all_news, 'title')[:10]
    
    def collect_pm_cases(self):
        """收集项目管理案例"""
        print("\n💼 开始收集项目管理案例...")
        all_cases = []
        
        keywords = getattr(config, 'SEARCH_KEYWORDS', {}).get('pm_cases', ["AI project management tools", "AI case study"])
        
        for keyword in keywords[:2]:
            print(f"  🔍 处理关键词: {keyword}")
            cases = self.search_and_summarize(query=keyword, content_type='case', count=5)
            all_cases.extend(cases)
            time.sleep(1)
        
        return self._deduplicate(all_cases, 'title')[:6]
    
    def _deduplicate(self, items, key):
        """根据指定键去重"""
        seen = set()
        unique = []
        for item in items:
            val = item.get(key)
            if val not in seen:
                seen.add(val)
                unique.append(item)
        return unique

    def save_data(self, news, cases, filename='data.json'):
        """保存数据到JSON文件"""
        data = {
            'update_time': datetime.now().strftime('%Y年%m月%d日 %H:%M'),
            'news': news,
            'cases': cases,
            'stats': {
                'news_count': len(news),
                'case_count': len(cases)
            }
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 数据已保存到 {filename}")
        return data

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AI+项目管理信息面板 - 内容更新")
    print("=" * 60)
    
    collector = AINewsCollector()
    news = collector.collect_ai_news()
    cases = collector.collect_pm_cases()
    collector.save_data(news, cases)
    
    print("\n✅ 更新完成！")
    print(f"📊 动态: {len(news)} | 案例: {len(cases)}")
    print("=" * 60)

if __name__ == '__main__':
    main()
