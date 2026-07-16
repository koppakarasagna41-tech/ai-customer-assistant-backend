import os
import json
import logging
import re
from app.services.gemini_client import get_gemini_client, GeminiClient
from app.schemas.classification import ClassificationResponse, ClassificationDetail

logger = logging.getLogger("app.services.classification_service")

class ClassificationService:
    def __init__(self, gemini_client: GeminiClient = None):
        self.client = gemini_client or get_gemini_client()
        self.prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts", "classification_prompt.txt"
        )
        self.prompt = ""
        self._load_prompt()

    def _load_prompt(self):
        try:
            if os.path.exists(self.prompt_path):
                with open(self.prompt_path, "r", encoding="utf-8") as f:
                    self.prompt = f.read()
            else:
                self.prompt = "Classify support tickets into enterprise categories."
        except Exception as e:
            logger.error(f"Error loading classification prompt: {e}")
            self.prompt = "Classify support tickets into enterprise categories."

    def clean_json_string(self, text: str) -> str:
        if not text:
            return ""
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    async def classify_ticket(self, text: str) -> ClassificationResponse:
        if not text:
            return ClassificationResponse(classifications=[ClassificationDetail(category="TECHNICAL", confidence=1.0)])

        try:
            schema = ClassificationResponse.model_json_schema()
            contents = [
                {"role": "user", "parts": [{"text": f"Message to classify ticket from:\n\n{text}"}]}
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
                logger.error(f"Malformed response format from Gemini client in ClassificationService: {e}")
                raw_text = "{}"

            cleaned = self.clean_json_string(raw_text)
            data = json.loads(cleaned) if cleaned else {}
            
            classifications_list = []
            for item in data.get("classifications", []):
                classifications_list.append(
                    ClassificationDetail(
                        category=str(item.get("category", "TECHNICAL")),
                        confidence=float(item.get("confidence", 1.0))
                    )
                )
            if not classifications_list:
                classifications_list.append(ClassificationDetail(category="TECHNICAL", confidence=1.0))
            return ClassificationResponse(classifications=classifications_list)
            
        except Exception as e:
            logger.error(f"ClassificationService error: {e}")
            return ClassificationResponse(classifications=[ClassificationDetail(category="TECHNICAL", confidence=1.0)])

def get_classification_service() -> ClassificationService:
    return ClassificationService()
