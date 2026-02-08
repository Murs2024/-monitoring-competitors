"""
Сервис анализа: DeepSeek — текст и распарсенные страницы; OpenAI — изображения (и PDF при появлении).
"""
import base64
import json
import re
from typing import Optional

from openai import OpenAI

from backend.config import settings
from backend.models.schemas import CompetitorAnalysis, ImageAnalysis


class OpenAIService:
    """DeepSeek — текст и парсинг (с повтором на стандартный URL как в лекции); OpenAI — изображения."""

    # Стандартный URL для повтора, если кастомный DEEPSEEK_BASE_URL не сработал (как в PEm07 image_cli)
    DEEPSEEK_STANDARD_BASE = "https://api.deepseek.com"

    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.openai_model = settings.openai_model
        self.vision_model = settings.openai_vision_model
        self.deepseek_api_key = (settings.deepseek_api_key or "").strip()
        self.deepseek_base_url = (settings.deepseek_base_url or "").strip() or self.DEEPSEEK_STANDARD_BASE
        self.deepseek_model = settings.deepseek_model or "deepseek-chat"

    def _chat_text(self, messages: list) -> str:
        """Текст: DeepSeek (с повтором на стандартный URL как в лекции) или OpenAI, если нет DEEPSEEK_API_KEY."""
        if self.deepseek_api_key:
            for base_url in (self.deepseek_base_url, self.DEEPSEEK_STANDARD_BASE):
                try:
                    client = OpenAI(api_key=self.deepseek_api_key, base_url=base_url)
                    response = client.chat.completions.create(
                        model=self.deepseek_model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2000,
                    )
                    content = (response.choices[0].message.content or "").strip()
                    if content:
                        return content
                except Exception:
                    if base_url == self.DEEPSEEK_STANDARD_BASE:
                        raise
                    continue
        # Fallback на OpenAI, если DeepSeek не настроен
        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        return (response.choices[0].message.content or "").strip()

    def _parse_json_response(self, content: str) -> dict:
        """Извлечь JSON из ответа модели."""
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if json_match:
            content = json_match.group(1)
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            content = json_match.group(0)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    def analyze_text(self, text: str) -> CompetitorAnalysis:
        """Анализ текста (юридические услуги, описание конкурента)."""
        system_prompt = """Ты — эксперт по юриспруденции и конкурентному анализу юридического рынка. Проанализируй текст (описание услуг, лендинг юрфирмы, реклама) и верни структурированный JSON-ответ.

Формат ответа (строго JSON):
{
    "strengths": ["сильная сторона 1", "сильная сторона 2", ...],
    "weaknesses": ["слабая сторона 1", "слабая сторона 2", ...],
    "unique_offers": ["уникальное предложение 1", ...],
    "recommendations": ["рекомендация 1", "рекомендация 2", ...],
    "summary": "Краткое резюме анализа"
}

Важно:
- Каждый массив 3-5 пунктов, пиши на русском
- Оценивай с точки зрения клиента и подачи юридических услуг: понятность, доверие, риски формулировок"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Проанализируй текст (юридическая сфера):\n\n{text}"},
        ]
        content = self._chat_text(messages)
        data = self._parse_json_response(content or "")
        return CompetitorAnalysis(
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            unique_offers=data.get("unique_offers", []),
            recommendations=data.get("recommendations", []),
            summary=data.get("summary", ""),
        )

    def analyze_image(self, image_base64: str, mime_type: str = "image/jpeg") -> ImageAnalysis:
        """Анализ изображения (лендинг, баннер юрфирмы, скрин сайта)."""
        system_prompt = """Ты — эксперт по визуальному маркетингу и дизайну в сфере юриспруденции. Проанализируй изображение (лендинг, баннер, сайт юрфирмы) и верни структурированный JSON-ответ.

Формат ответа (строго JSON):
{
    "description": "Детальное описание того, что изображено",
    "marketing_insights": ["инсайт 1", "инсайт 2", ...],
    "visual_style_score": 7,
    "visual_style_analysis": "Анализ визуального стиля: насколько серьёзно и доверительно выглядит",
    "recommendations": ["рекомендация 1", "рекомендация 2", ...]
}

Важно:
- visual_style_score от 0 до 10 (в т.ч. впечатление «доверия» для юридической темы)
- Каждый массив 3-5 пунктов, пиши на русском
- Оценивай: подачу для юруслуг, читаемость, цвет, типографику"""

        response = self.openai_client.chat.completions.create(
            model=self.vision_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Проанализируй это изображение (юридическая тема: лендинг, баннер, сайт) с точки зрения маркетинга и доверия:",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
                        },
                    ],
                },
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        content = response.choices[0].message.content
        data = self._parse_json_response(content or "")
        return ImageAnalysis(
            description=data.get("description", ""),
            marketing_insights=data.get("marketing_insights", []),
            visual_style_score=min(10, max(0, data.get("visual_style_score", 5))),
            visual_style_analysis=data.get("visual_style_analysis", ""),
            recommendations=data.get("recommendations", []),
        )

    def analyze_parsed_content(
        self,
        title: Optional[str],
        h1: Optional[str],
        paragraph: Optional[str],
    ) -> CompetitorAnalysis:
        """Анализ распарсенного контента: новости/обновления (КонсультантПлюс и т.п.) или описание конкурента."""
        parts = []
        if title:
            parts.append(f"Заголовок страницы (title): {title}")
        if h1:
            parts.append(f"Главный заголовок (H1): {h1}")
        if paragraph:
            parts.append(f"Первый абзац / фрагмент контента: {paragraph}")
        combined = "\n\n".join(parts)
        if not combined.strip():
            return CompetitorAnalysis(summary="Не удалось извлечь контент для анализа")

        system_prompt = """Ты — эксперт по юриспруденции. По контенту страницы (заголовки, абзац) определи тип страницы и заполни JSON.

Если это новости, обновления законодательства, анонсы (например КонсультантПлюс, правовые порталы):
- Заполни: news_highlights (что нового, ключевые изменения), attention_points (на что обратить внимание юристу), key_topics (ключевые темы/рубрики), summary (краткое резюме).
- Массивы strengths, weaknesses, unique_offers, recommendations оставь пустыми [].

Если это описание юридических услуг, лендинг юрфирмы, реклама:
- Заполни: strengths, weaknesses, unique_offers, recommendations, summary.
- Массивы news_highlights, attention_points, key_topics оставь пустыми [].

Формат ответа (строго JSON):
{
    "strengths": [],
    "weaknesses": [],
    "unique_offers": [],
    "recommendations": [],
    "summary": "Краткое резюме",
    "news_highlights": [],
    "attention_points": [],
    "key_topics": []
}

Заполняй только те массивы, которые подходят под тип страницы. summary заполняй всегда. Пиши на русском, 3-7 пунктов в каждом непустом массиве."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Проанализируй контент страницы:\n\n{combined}"},
        ]
        content = self._chat_text(messages)
        data = self._parse_json_response(content or "")
        return CompetitorAnalysis(
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            unique_offers=data.get("unique_offers", []),
            recommendations=data.get("recommendations", []),
            summary=data.get("summary", ""),
            news_highlights=data.get("news_highlights") or [],
            attention_points=data.get("attention_points") or [],
            key_topics=data.get("key_topics") or [],
        )


openai_service = OpenAIService()
