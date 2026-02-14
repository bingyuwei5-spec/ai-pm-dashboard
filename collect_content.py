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
        
        Args:
            query: 搜索查询
            content_type: 'news' 或 'case'
            count: 需要的条数
        
        Returns:
            list: 总结后的内容列表
        """
        try:
            # 构建提示词
            if content_type == 'news':
                prompt = f"""请搜索关于"{query}"的最新AI动态新闻。

要求：
1. 找到{count}条最重要、最新的AI领域动态
2. 每条新闻包含：标题、摘要（2-3句话）、重要性级别（高/中）、相关标签
3. 优先选择对项目管理有影响的AI进展
4. 按重要性排序

请以JSON格式返回，格式如下：
[
  {{
    "title": "新闻标题",
    "summary": "新闻摘要，2-3句话说明要点和影响",
    "priority": "high" 或 "medium",
    "tags": ["标签1", "标签2"],
    "date": "2026年2月"
  }}
]

只返回JSON，不要其他文字。"""
            
            else:  # case
                prompt = f"""请搜索关于"{query}"的实际应用案例。

要求：
1. 找到{count}个AI在项目管理中的真实应用案例
2. 每个案例包含：标题、公司/行业、描述、量化效果
3. 优先选择有具体数据和效果的案例
4. 涵盖不同行业（建筑、IT、制造、咨询等）

请以JSON格式返回，格式如下：
[
  {{
    "title": "案例标题",
    "company": "公司名称",
    "industry": "行业类别",
    "description": "案例描述，说明如何使用AI，2-3句话",
    "impact": ["效果1: 提升X%", "效果2: 减少Y%", "效果3: 节省Z元"]
  }}
]

只返回JSON，不要其他文字。"""
            
            # 调用通义千问API（支持联网搜索）
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个专业的AI信息分析师，专注于AI+项目管理领域。你可以搜索网络获取最新信息，并用中文总结要点。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.7,
                # 启用联网搜索（通义千问特有功能）
                enable_search=True
            )
            
            # 解析响应
            content = response.choices[0].message.content.strip()
            
            # 尝试提取JSON（去除可能的markdown标记）
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
            print(f"原始内容: {content[:500]}")
            return []
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def collect_ai_news(self):
        """收集AI动态新闻"""
        print("\n📰 开始收集AI动态新闻...")
        all_news = []
        
        for keyword in config.SEARCH_KEYWORDS['ai_news'][:2]:  # 使用前2个关键词
            print(f"  🔍 搜索: {keyword}")
            news = self.search_and_summarize(
                query=keyword,
                content_type='news',
                count=5
            )
            all_news.extend(news)
            time.sleep(2)  # 避免请求过快
        
        # 去重并限制数量
        unique_news = self._deduplicate(all_news, 'title')
        return unique_news[:config.NEWS_COUNT]
    
    def collect_pm_cases(self):
        """收集项目管理案例"""
        print("\n💼 开始收集项目管理案例...")
        all_cases = []
        
        for keyword in config.SEARCH_KEYWORDS['pm_cases'][:2]:  # 使用前2个关键词
            print(f"  🔍 搜索: {keyword}")
            cases = self.search_and_summarize(
                query=keyword,
                content_type='case',
                count=5
            )
            all_cases.extend(cases)
            time.sleep(2)  # 避免请求过快
        
        # 去重并限制数量
        unique_cases = self._deduplicate(all_cases, 'title')
        return unique_cases[:config.CASE_COUNT]
    
    def _deduplicate(self, items, key):
        """根据指定键去重"""
        seen = set()
        unique = []
        for item in items:
            if item.get(key) not in seen:
                seen.add(item.get(key))
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
    
    # 初始化收集器
    collector = AINewsCollector()
    
    # 收集内容
    news = collector.collect_ai_news()
    cases = collector.collect_pm_cases()
    
    # 保存数据
    data = collector.save_data(news, cases)
    
    print("\n" + "=" * 60)
    print(f"✅ 更新完成！")
    print(f"📊 AI动态: {len(news)} 条")
    print(f"💡 实践案例: {len(cases)} 个")
    print("=" * 60)
    
    return data

if __name__ == '__main__':
    main()
