import json
import logging
import os
import re

from app.schemas.sentiment import SentimentDetail, SentimentResponse
from app.services.gemini_client import GeminiClient, get_gemini_client

logger = logging.getLogger("app.services.sentiment_service")


class SentimentService:
    def __init__(self, gemini_client: GeminiClient = None):
        self.client = gemini_client or get_gemini_client()
        self.prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts", "sentiment_prompt.txt"
        )
        self.prompt = ""
        self._load_prompt()

    def _load_prompt(self):
        try:
            if os.path.exists(self.prompt_path):
                with open(self.prompt_path, encoding="utf-8") as f:
                    self.prompt = f.read()
            else:
                self.prompt = "Analyze sentiment of support messages."
        except Exception as e:
            logger.error(f"Error loading sentiment prompt: {e}")
            self.prompt = "Analyze sentiment of support messages."

    def clean_json_string(self, text: str) -> str:
        if not text:
            return ""
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    async def analyze_sentiment(self, text: str) -> SentimentResponse:
        if not text:
            return SentimentResponse(
                sentiment=SentimentDetail(label="neutral", score=0.5), escalation_recommended=False
            )

        try:
            schema = SentimentResponse.model_json_schema()
            contents = [
                {
                    "role": "user",
                    "parts": [{"text": f"Message to analyze sentiment from:\n\n{text}"}],
                }
            ]
            raw_res = await self.client.generate_content(
                contents=contents,
                system_instruction=self.prompt,
                response_schema=schema,
                response_mime_type="application/json",
                temperature=0.1,
            )

            try:
                raw_text = raw_res["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                logger.error(
                    f"Malformed response format from Gemini client in SentimentService: {e}"
                )
                raw_text = "{}"

            cleaned = self.clean_json_string(raw_text)
            data = json.loads(cleaned) if cleaned else {}

            sent_data = data.get("sentiment", {})
            return SentimentResponse(
                sentiment=SentimentDetail(
                    label=str(sent_data.get("label", "neutral")),
                    score=float(sent_data.get("score", 0.5)),
                ),
                escalation_recommended=bool(data.get("escalation_recommended", False)),
            )

        except Exception as e:
            logger.error(f"SentimentService error: {e}")
            return SentimentResponse(
                sentiment=SentimentDetail(label="neutral", score=0.5), escalation_recommended=False
            )


def get_sentiment_service() -> SentimentService:
    return SentimentService()
