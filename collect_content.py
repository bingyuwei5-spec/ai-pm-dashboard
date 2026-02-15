# -*- coding: utf-8 -*-
"""
AI+项目管理信息面板 - 内容搜索和抓取
使用阿里云通义千问API（启用联网搜索）
"""

import json
import time
import re
from datetime import datetime
from openai import OpenAI
import config

class AINewsCollector:
    """AI新闻和案例收集器"""
    
    def __init__(self):
        """初始化API客户端"""
        if not config.QWEN_API_KEY:
            raise ValueError("未设置 QWEN_API_KEY，请检查配置")
        
        self.client = OpenAI(
            api_key=config.QWEN_API_KEY,
            base_url=config.QWEN_API_BASE
        )
        self.model = config.QWEN_MODEL
        print(f"✅ 使用模型: {self.model}")
    
    def search_and_summarize(self, query, content_type='news', count=5):
        """
        搜索并总结内容（启用联网搜索）
        
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
                prompt = f"""请搜索关于"{query}"的最新AI动态新闻（2025-2026年）。

要求：
1. 必须搜索互联网获取最新信息
2. 找到{count}条2025年或2026年的重要AI新闻
3. 每条新闻必须包含：标题、摘要（2-3句话）、重要性级别（high/medium）、相关标签、日期
4. 优先选择对项目管理有影响的AI进展
5. 必须是真实存在的新闻，不要编造

请严格按照以下JSON格式返回，不要有任何其他文字：
[
  {{
    "title": "新闻标题",
    "summary": "新闻摘要，说明要点和影响",
    "priority": "high",
    "tags": ["标签1", "标签2"],
    "date": "2026年2月"
  }}
]"""
            
            else:  # case
                prompt = f"""请搜索关于"{query}"的真实应用案例。

要求：
1. 必须搜索互联网获取真实案例
2. 找到{count}个AI在项目管理中的实际应用案例
3. 每个案例必须包含：标题、公司、行业、描述、量化效果
4. 必须是真实的案例，包含具体公司名称
5. 优先选择有明确数据支持的案例

请严格按照以下JSON格式返回，不要有任何其他文字：
[
  {{
    "title": "案例标题",
    "company": "公司名称",
    "industry": "行业",
    "description": "案例描述，说明如何使用AI",
    "impact": ["效果1", "效果2", "效果3"]
  }}
]"""
            
            print(f"  🔍 搜索: {query}")
            
            # 调用通义千问API - 关键：启用联网搜索
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个专业的AI信息分析师。你必须使用联网搜索功能获取最新的真实信息，然后用中文总结。不要编造内容。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.5,
                # 🔥 关键设置：启用联网搜索
                extra_body={
                    "enable_search": True  # 阿里云通义千问的联网搜索参数
                }
            )
            
            # 解析响应
            content = response.choices[0].message.content.strip()
            
            # 提取JSON（去除可能的markdown标记）
            content = self._extract_json(content)
            
            # 解析JSON
            results = json.loads(content)
            
            # 验证数据完整性
            results = self._validate_data(results, content_type)
            
            print(f"  ✅ 成功获取 {len(results)} 条内容")
            return results
            
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON解析错误: {e}")
            print(f"  原始内容: {content[:300]}...")
            return []
        except Exception as e:
            print(f"  ❌ 搜索失败: {e}")
            return []
    
    def _extract_json(self, content):
        """提取JSON内容"""
        # 去除markdown代码块标记
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        # 使用正则提取JSON数组
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            return match.group()
        
        return content
    
    def _validate_data(self, results, content_type):
        """验证和修复数据"""
        if not isinstance(results, list):
            return []
        
        valid_results = []
        for item in results:
            if content_type == 'news':
                # 验证新闻必需字段
                if all(key in item for key in ['title', 'summary', 'priority', 'tags', 'date']):
                    # 确保tags是数组
                    if isinstance(item['tags'], str):
                        item['tags'] = [item['tags']]
                    valid_results.append(item)
            else:
                # 验证案例必需字段
                if all(key in item for key in ['title', 'company', 'industry', 'description', 'impact']):
                    # 确保impact是数组
                    if isinstance(item['impact'], str):
                        item['impact'] = [item['impact']]
                    valid_results.append(item)
        
        return valid_results
    
    def collect_ai_news(self):
        """收集AI动态新闻"""
        print("\n📰 开始收集AI动态新闻...")
        all_news = []
        
        # 使用更精确的搜索关键词
        keywords = [
            "AI latest news 2026",  # 英文搜索通常更准确
            "artificial intelligence breakthroughs 2025 2026",
            "AI项目管理 2026 最新",
        ]
        
        for keyword in keywords[:2]:  # 使用前2个关键词
            news = self.search_and_summarize(
                query=keyword,
                content_type='news',
                count=5
            )
            all_news.extend(news)
            time.sleep(2)  # 避免请求过快
        
        # 去重
        unique_news = self._deduplicate(all_news, 'title')
        return unique_news[:config.NEWS_COUNT]
    
    def collect_pm_cases(self):
        """收集项目管理案例"""
        print("\n💼 开始收集项目管理案例...")
        all_cases = []
        
        keywords = [
            "AI project management case study 2025 2026",
            "企业AI项目管理实践案例",
        ]
        
        for keyword in keywords[:2]:
            cases = self.search_and_summarize(
                query=keyword,
                content_type='case',
                count=5
            )
            all_cases.extend(cases)
            time.sleep(2)
        
        # 去重
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
    
    def save_data(self, news, cases):
        """保存数据到JSON文件"""
        data = {
            'update_time': datetime.now().strftime('%Y年%m月%d日 %H:%M'),
            'news': news if news else [
                {
                    "title": "正在获取最新数据...",
                    "summary": "系统正在搜索最新的AI动态，请稍后刷新页面",
                    "priority": "medium",
                    "tags": ["系统提示"],
                    "date": datetime.now().strftime('%Y年%m月')
                }
            ],
            'cases': cases if cases else [
                {
                    "title": "正在加载案例...",
                    "company": "系统",
                    "industry": "技术",
                    "description": "正在搜索最新的AI项目管理案例",
                    "impact": ["加载中..."]
                }
            ],
            'stats': {
                'news_count': len(news) if news else 0,
                'case_count': len(cases) if cases else 0
            }
        }
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 数据已保存到 data.json")
        return data

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AI+项目管理信息面板 - 内容更新")
    print("=" * 60)
    
    try:
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
        print(f"⏰ 更新时间: {data['update_time']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
