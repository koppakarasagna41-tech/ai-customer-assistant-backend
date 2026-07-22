from typing import Any

from app.services.gemini_client import GeminiClient, get_gemini_client


class GeminiService:
    def __init__(
        self,
        client: GeminiClient | None = None,
    ):
        self.client = client or get_gemini_client()

    async def analyze_ticket(
        self,
        title: str,
        description: str,
    ) -> dict[str, Any]:
        system_instruction = """
You are an AI customer support assistant.

Analyze the support ticket and return ONLY valid JSON.

Required JSON format:
{
  "predicted_category": "...",
  "predicted_priority": "...",
  "suggested_response": "...",
  "confidence_score": 0.95
}
"""

        contents = [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"Title: {title}\n"
                            f"Description: {description}"
                        )
                    }
                ],
            }
        ]

        response = await self.client.generate_content(
            contents=contents,
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.2,
        )

        text = (
            response["candidates"][0]["content"]["parts"][0]["text"]
        )

        import json

        return json.loads(text)


def get_gemini_service() -> GeminiService:
    return GeminiService()