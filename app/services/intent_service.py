import os
import json
import logging
import re
from app.services.gemini_client import get_gemini_client, GeminiClient
from app.schemas.intent import IntentResponse, IntentDetail

logger = logging.getLogger("app.services.intent_service")

class IntentService:
    def __init__(self, gemini_client: GeminiClient = None):
        self.client = gemini_client or get_gemini_client()
        self.prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts", "intent_prompt.txt"
        )
        self.prompt = ""
        self._load_prompt()

    def _load_prompt(self):
        try:
            if os.path.exists(self.prompt_path):
                with open(self.prompt_path, "r", encoding="utf-8") as f:
                    self.prompt = f.read()
            else:
                self.prompt = "Detect intent from customer support messages."
        except Exception as e:
            logger.error(f"Error loading intent prompt: {e}")
            self.prompt = "Detect intent from customer support messages."

    def clean_json_string(self, text: str) -> str:
        if not text:
            return ""
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    async def detect_intent(self, text: str) -> IntentResponse:
        if not text:
            return IntentResponse(intents=[IntentDetail(intent="general_inquiry", confidence=1.0)])

        try:
            schema = IntentResponse.model_json_schema()
            contents = [
                {"role": "user", "parts": [{"text": f"Message to detect intent from:\n\n{text}"}]}
            ]
            raw_res = await self.client.generate_content(
                contents=contents,
                system_instruction=self.prompt,
                response_schema=schema,
                response_mime_type="application/json",
                temperature=0.1
            )
            
            try:
                raw_text = raw_res["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                logger.error(f"Malformed response format from Gemini client in IntentService: {e}")
                raw_text = "{}"

            cleaned = self.clean_json_string(raw_text)
            data = json.loads(cleaned) if cleaned else {}
            
            intents_list = []
            for item in data.get("intents", []):
                intents_list.append(
                    IntentDetail(
                        intent=str(item.get("intent", "general_inquiry")),
                        confidence=float(item.get("confidence", 1.0))
                    )
                )
            if not intents_list:
                intents_list.append(IntentDetail(intent="general_inquiry", confidence=1.0))
            return IntentResponse(intents=intents_list)
            
        except Exception as e:
            logger.error(f"IntentService error: {e}")
            return IntentResponse(intents=[IntentDetail(intent="general_inquiry", confidence=1.0)])

def get_intent_service() -> IntentService:
    return IntentService()
