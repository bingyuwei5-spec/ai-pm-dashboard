# -*- coding: utf-8 -*-
import json
import time
import re
from datetime import datetime
from openai import OpenAI
import config

class AINewsCollector:
    def __init__(self):
        try:
            self.client = OpenAI(
                api_key=config.QWEN_API_KEY,
                base_url=config.QWEN_API_BASE
            )
            self.model = config.QWEN_MODEL
        except Exception as e:
            print(f"初始化失敗: {e}")

    def safe_get_json(self, content):
        """暴力提取 JSON，防止 AI 回傳多餘文字"""
        try:
            # 使用正則表達式尋找 [ ] 之間的內容
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(content)
        except:
            return []

    def fetch(self, query, is_news=True):
        """抓取數據，增加徹底的錯誤攔截"""
        try:
            prompt = f"請用中文列出關於'{query}'的3條最新資訊。以JSON數組格式返回，必須包含字段: "
            prompt += "title, summary, priority, tags, date" if is_news else "title, company, industry, description, impact (數組)"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': '你是一個只會輸出純中文JSON數組的機器人。'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.3
            )
            
            # 正確的訪問路徑：choices[0]
            raw_content = response.choices[0].message.content.strip()
            data = self.safe_get_json(raw_content)
            
            # 修正「垂直顯示」Bug：強制 impact 變成數組
            if not is_news:
                for item in data:
                    if isinstance(item.get('impact'), str):
                        item['impact'] = [item['impact']]
            return data
        except Exception as e:
            print(f"請求跳過 ({query}): {e}")
            return []

    def run(self):
        print("🚀 啟動自動化抓取...")
        
        # 抓取新聞
        news = []
        for kw in ["AI項目管理", "生成式AI工具"]:
            news.extend(self.fetch(kw, True))
            time.sleep(1)
        
        # 抓取案例
        cases = []
        for kw in ["AI自動化案例", "企業級AI應用"]:
            cases.extend(self.fetch(kw, False))
            time.sleep(1)

        # 最終數據封裝
        final_data = {
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'news': news if news else [{"title": "數據更新中", "summary": "請稍後刷新", "priority": "medium", "tags": ["System"], "date": "2026-02"}],
            'cases': cases if cases else [{"title": "案例加載中", "company": "System", "industry": "IT", "description": "正在獲取最新案例", "impact": ["優化中"]}],
            'stats': {'news_count': len(news), 'case_count': len(cases)}
        }
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print("✅ 執行成功！")

if __name__ == '__main__':
    AINewsCollector().run()
