"""
花海纪 - 信息抽取服务
从对话历史中提取结构化旅行计划信息
"""
import json
import re
from typing import Optional

from openai import AsyncOpenAI
from app.config import get_settings
from app.models import TripPlan

settings = get_settings()

# 信息抽取专用提示词
EXTRACT_PROMPT = """请从以下用户与旅行助手的对话记录中，提取旅行规划的关键信息。

请严格按照以下 JSON 格式返回，不要添加任何其他文字：
{
  "people_count": "出行人数，如 2人、3-4人",
  "people_type": "人群类型：家庭/情侣/朋友/独自/其他",
  "budget": "预算范围，如 5000-8000元",
  "days": "出行天数，如 5天",
  "destination": "目的地城市或地区",
  "dates": "出行日期或时间段",
  "accommodation_preference": "住宿偏好：酒店/民宿/青旅/度假村",
  "food_preference": "饮食偏好描述",
  "transport_preference": "交通方式偏好",
  "special_needs": "特殊需求描述",
  "interests": "兴趣偏好描述",
  "confidence": 0.85
}

规则：
1. 如果某项信息在对话中未提及，对应值填 null
2. confidence 表示信息完整度（0到1之间），根据已获取的关键信息比例评估
3. 至少需要获取：目的地、天数、人数、预算 这4项核心信息，confidence 才能达到 0.7 以上
4. 只返回 JSON，不要有任何其他内容
"""


class ExtractorService:
    """信息抽取服务"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )

    async def extract_trip_plan(
        self,
        chat_history: list[dict],
    ) -> TripPlan:
        """
        从对话历史中提取旅行计划

        Args:
            chat_history: 对话记录列表 [{"role": "user/assistant", "content": "..."}]

        Returns:
            TripPlan 结构化旅行计划
        """
        # 将对话历史格式化为文本
        conversation_text = "\n".join(
            f"[{msg['role']}]: {msg['content']}"
            for msg in chat_history
        )

        messages = [
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": f"以下是对话记录：\n\n{conversation_text}"},
        ]

        # 调用 DeepSeek 进行抽取
        response = await self.client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.1,  # 低温度，确保输出稳定
            max_tokens=1024,
        )

        raw_text = response.choices[0].message.content or "{}"

        # 解析 JSON（处理可能的 markdown 代码块包裹）
        plan_dict = self._parse_json(raw_text)

        # 转换为 TripPlan 对象
        trip_plan = TripPlan(**plan_dict)

        return trip_plan

    def _parse_json(self, text: str) -> dict:
        """
        解析 DeepSeek 返回的 JSON
        处理可能的 markdown 代码块包裹
        """
        # 尝试提取 JSON 代码块
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if json_match:
            text = json_match.group(1).strip()

        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 尝试找到第一个 { 和最后一个 }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    pass

        # 解析失败，返回空结构
        return {
            "people_count": None,
            "people_type": None,
            "budget": None,
            "days": None,
            "destination": None,
            "dates": None,
            "accommodation_preference": None,
            "food_preference": None,
            "transport_preference": None,
            "special_needs": None,
            "interests": None,
            "confidence": 0.0,
        }

    def check_info_completeness(self, plan: TripPlan) -> dict:
        """
        检查信息完整度，返回缺失字段列表

        Returns:
            {"is_complete": bool, "missing_fields": list[str], "confidence": float}
        """
        # 核心字段
        core_fields = {
            "destination": plan.destination,
            "days": plan.days,
            "people_count": plan.people_count,
            "budget": plan.budget,
        }

        # 可选字段
        optional_fields = {
            "accommodation_preference": plan.accommodation_preference,
            "food_preference": plan.food_preference,
            "transport_preference": plan.transport_preference,
            "dates": plan.dates,
        }

        missing_core = [
            name for name, value in core_fields.items() if value is None
        ]
        missing_optional = [
            name for name, value in optional_fields.items() if value is None
        ]

        # 核心字段全部获取才算完整
        is_complete = len(missing_core) == 0

        return {
            "is_complete": is_complete,
            "missing_fields": missing_core + missing_optional,
            "confidence": plan.confidence,
        }


# 全局服务实例
extractor_service = ExtractorService()
