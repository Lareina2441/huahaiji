"""
花海纪 - DeepSeek AI 对话服务
封装 DeepSeek API 调用，支持流式和非流式输出
"""
import json
from typing import AsyncGenerator
from openai import AsyncOpenAI

from app.config import get_settings

settings = get_settings()

# 系统提示词 - 旅行规划助手
SYSTEM_PROMPT = """你是一个专业、温暖的旅行规划助手，名叫"花海纪"。

你的核心任务是通过自然、友好的对话，逐步了解用户的旅行需求。

你需要收集的信息包括：
- 出行人数和人群关系（家庭出游/情侣/朋友结伴/独自旅行）
- 预算范围
- 出行天数和日期
- 目的地（如果用户还没确定，可以推荐）
- 住宿偏好（酒店/民宿/青旅/度假村）
- 饮食偏好（地方特色/国际料理/素食/无特殊要求）
- 交通方式偏好（飞机/高铁/自驾/公共交通）
- 兴趣偏好（自然风光/历史文化/美食探店/购物/冒险运动）
- 特殊需求（带小孩/老人/宠物/无障碍需求）

对话规则：
1. 不要一次性问太多问题，每次最多问 1-2 个
2. 根据用户的回答自然引导下一个话题
3. 如果用户已经透露了某些信息，不要重复询问
4. 适当分享旅行小知识和建议，让对话更有价值
5. 当你认为信息收集得比较充分时，主动总结并确认
6. 语言风格：亲切自然，像朋友聊天一样

当信息收集充分后，请用以下格式总结确认：
「我帮你整理一下旅行计划：
📍 目的地：xxx
👥 出行：xxx
📅 时间：xxx天
💰 预算：xxx
🏨 住宿：xxx
🍜 饮食：xxx
🎯 偏好：xxx

请确认以上信息是否正确，或者告诉我需要修改的地方～」
"""


class DeepSeekService:
    """DeepSeek AI 服务"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = settings.DEEPSEEK_MODEL
        self.max_tokens = settings.DEEPSEEK_MAX_TOKENS
        self.temperature = settings.DEEPSEEK_TEMPERATURE
        self.max_context_rounds = settings.MAX_CONTEXT_ROUNDS

    def _build_messages(
        self,
        user_message: str,
        chat_history: list[dict] | None = None,
    ) -> list[dict]:
        """
        构建发送给 DeepSeek 的消息列表
        自动裁剪上下文，保留最近 N 轮对话
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # 添加历史对话（保留最近 N 轮，每轮包含 user + assistant）
        if chat_history:
            # 每轮 2 条消息 (user + assistant)，保留最近 N 轮
            max_messages = self.max_context_rounds * 2
            recent_history = chat_history[-max_messages:]
            messages.extend(recent_history)

        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})

        return messages

    async def chat(
        self,
        user_message: str,
        chat_history: list[dict] | None = None,
    ) -> str:
        """
        非流式对话
        返回完整的 AI 回复文本
        """
        messages = self._build_messages(user_message, chat_history)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=False,
        )

        return response.choices[0].message.content or ""

    async def chat_stream(
        self,
        user_message: str,
        chat_history: list[dict] | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        流式对话
        逐 token 生成，用于 SSE 推送
        """
        messages = self._build_messages(user_message, chat_history)

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def chat_with_extract(
        self,
        user_message: str,
        chat_history: list[dict] | None = None,
    ) -> dict:
        """
        对话 + 自动判断信息是否收集完整
        返回: {"reply": str, "is_info_complete": bool}
        """
        reply = await self.chat(user_message, chat_history)

        # 通过抽取服务判断信息完整度（更可靠）
        is_complete = False
        try:
            from app.services.extractor import extractor_service
            full_history = list(chat_history or [])
            full_history.append({"role": "user", "content": user_message})
            full_history.append({"role": "assistant", "content": reply})
            trip_plan = await extractor_service.extract_trip_plan(full_history)
            completeness = extractor_service.check_info_completeness(trip_plan)
            is_complete = completeness["is_complete"]
        except Exception:
            # 降级：简单关键词匹配
            is_complete = "请确认以上信息" in reply or "帮你整理" in reply

        return {
            "reply": reply,
            "is_info_complete": is_complete,
        }


# 全局服务实例
deepseek_service = DeepSeekService()
