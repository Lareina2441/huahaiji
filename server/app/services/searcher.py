"""
花海纪 - 搜索服务
调用搜索 API 获取旅行攻略，并用 AI 总结提炼
"""
import json
import httpx
from typing import Optional

from openai import AsyncOpenAI
from app.config import get_settings
from app.models import TripPlan, PlaceInfo, PlaceType, SearchResult

settings = get_settings()

# AI 总结提示词
SUMMARIZE_PROMPT = """你是一个旅行攻略专家。请根据以下搜索结果，为用户整理出结构化的旅行推荐。

用户旅行计划：
- 目的地：{destination}
- 天数：{days}天
- 人数：{people_count}
- 预算：{budget}
- 住宿偏好：{accommodation_preference}
- 饮食偏好：{food_preference}
- 兴趣偏好：{interests}

请严格按以下 JSON 格式返回推荐列表：
{{
  "attractions": [
    {{
      "name": "景点名称",
      "type": "attraction",
      "address": "地址",
      "rating": 4.5,
      "description": "50字以内简介",
      "price_range": "门票价格",
      "opening_hours": "开放时间",
      "tips": "游玩小贴士"
    }}
  ],
  "restaurants": [
    {{
      "name": "餐厅名称",
      "type": "restaurant",
      "address": "地址",
      "rating": 4.7,
      "description": "50字以内简介",
      "price_range": "人均消费",
      "tips": "推荐菜品"
    }}
  ],
  "hotels": [
    {{
      "name": "酒店名称",
      "type": "hotel",
      "address": "地址",
      "rating": 4.3,
      "description": "50字以内简介",
      "price_range": "每晚价格",
      "tips": "入住建议"
    }}
  ],
  "summary": "一段100字以内的行程概要建议"
}}

规则：
1. 每类推荐 3-5 个
2. 优先推荐符合用户偏好和预算的选项
3. 如果搜索结果不足，可以基于你的知识补充推荐
4. 只返回 JSON，不要有任何其他内容
"""


class SearcherService:
    """搜索服务"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )

    def _build_search_keywords(self, plan: TripPlan) -> list[str]:
        """
        根据旅行计划生成搜索关键词组合
        """
        dest = plan.destination or "热门目的地"
        days = plan.days or ""
        budget = plan.budget or ""
        acc = plan.accommodation_preference or ""
        food = plan.food_preference or ""
        interests = plan.interests or ""

        keywords = []

        # 综合攻略
        keywords.append(f"{dest} {days}天自由行攻略 2025")

        # 景点推荐
        if interests:
            keywords.append(f"{dest} {interests}景点推荐")
        else:
            keywords.append(f"{dest} 必去景点排行榜")

        # 美食推荐
        if food:
            keywords.append(f"{dest} {food}美食推荐")
        else:
            keywords.append(f"{dest} 本地人推荐美食")

        # 住宿推荐
        if acc:
            keywords.append(f"{dest} {acc}推荐")
        if budget:
            keywords.append(f"{dest} {budget}预算住宿")

        # 实用攻略
        keywords.append(f"{dest} 交通攻略 注意事项")

        return keywords

    async def _search_serper(self, query: str, num: int = 5) -> list[dict]:
        """
        调用 Serper Google Search API 搜索
        """
        url = f"{settings.SERPER_BASE_URL}/search"
        headers = {
            "X-API-KEY": settings.SERPER_API_KEY,
            "Content-Type": "application/json",
        }
        params = {
            "q": query,
            "num": num,
            "hl": "zh-cn",  # 中文搜索
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        # 提取搜索结果
        results = []
        for item in data.get("organic", []):
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            })

        # 提取知识图谱信息（如果有）
        if "knowledgeGraph" in data:
            kg = data["knowledgeGraph"]
            results.append({
                "title": kg.get("title", ""),
                "link": kg.get("website", ""),
                "snippet": kg.get("description", ""),
            })

        return results

    async def _summarize_with_ai(
        self,
        plan: TripPlan,
        search_results: dict[str, list[dict]],
    ) -> SearchResult:
        """
        用 AI 对搜索结果进行总结提炼
        """
        # 构建搜索结果文本
        results_text = ""
        for keyword, results in search_results.items():
            results_text += f"\n【搜索: {keyword}】\n"
            for i, r in enumerate(results, 1):
                results_text += f"  {i}. {r['title']}\n     {r['snippet']}\n     链接: {r['link']}\n"

        # 填充总结提示词
        prompt = SUMMARIZE_PROMPT.format(
            destination=plan.destination or "未定",
            days=plan.days or "未定",
            people_count=plan.people_count or "未定",
            budget=plan.budget or "未定",
            accommodation_preference=plan.accommodation_preference or "无特殊要求",
            food_preference=plan.food_preference or "无特殊要求",
            interests=plan.interests or "无特殊要求",
        )

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"搜索结果如下：{results_text}"},
        ]

        response = await self.client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=3000,
        )

        raw_text = response.choices[0].message.content or "{}"

        # 解析结果
        try:
            # 处理可能的 markdown 代码块
            if "```" in raw_text:
                import re
                json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
                if json_match:
                    raw_text = json_match.group(1).strip()

            result_dict = json.loads(raw_text)

            return SearchResult(
                attractions=[
                    PlaceInfo(**item) for item in result_dict.get("attractions", [])
                ],
                restaurants=[
                    PlaceInfo(**item) for item in result_dict.get("restaurants", [])
                ],
                hotels=[
                    PlaceInfo(**item) for item in result_dict.get("hotels", [])
                ],
                summary=result_dict.get("summary"),
            )
        except (json.JSONDecodeError, Exception):
            return SearchResult(summary="搜索结果解析失败，请重试。")

    async def search_places(self, plan: TripPlan) -> SearchResult:
        """
        完整搜索流程：
        1. 生成搜索关键词
        2. 并发搜索
        3. AI 总结提炼
        """
        keywords = self._build_search_keywords(plan)

        # 并发搜索
        search_results = {}
        async with httpx.AsyncClient(timeout=15.0) as client:
            tasks = []
            for kw in keywords:
                tasks.append(self._search_serper(kw))
            # 逐个执行（避免并发过多）
            for i, kw in enumerate(keywords):
                try:
                    results = await self._search_serper(kw)
                    search_results[kw] = results
                except Exception as e:
                    search_results[kw] = [{"title": "搜索失败", "snippet": str(e), "link": ""}]

        # AI 总结
        result = await self._summarize_with_ai(plan, search_results)

        return result


# 全局服务实例
searcher_service = SearcherService()
