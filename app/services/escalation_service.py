import os
import json
import logging
import re
from app.services.gemini_client import get_gemini_client, GeminiClient
from app.schemas.escalation import EscalationResponse

logger = logging.getLogger("app.services.escalation_service")

class EscalationService:
    def __init__(self, gemini_client: GeminiClient = None):
        self.client = gemini_client or get_gemini_client()
        self.prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts", "escalation_prompt.txt"
        )
        self.prompt = ""
        self._load_prompt()

    def _load_prompt(self):
        try:
            if os.path.exists(self.prompt_path):
                with open(self.prompt_path, "r", encoding="utf-8") as f:
                    self.prompt = f.read()
            else:
                self.prompt = "Assess risk and escalation probability for support tickets."
        except Exception as e:
            logger.error(f"Error loading escalation prompt: {e}")
            self.prompt = "Assess risk and escalation probability for support tickets."

    def clean_json_string(self, text: str) -> str:
        if not text:
            return ""
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    async def assess_escalation(self, text: str) -> EscalationResponse:
        if not text:
            return EscalationResponse(
                escalation_score=0.0,
                escalation_recommended=False,
                reasons=[]
            )

        try:
            schema = EscalationResponse.model_json_schema()
            contents = [
                {"role": "user", "parts": [{"text": f"Message to assess risk and escalation from:\n\n{text}"}]}
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
                logger.error(f"Malformed response format from Gemini client in EscalationService: {e}")
                raw_text = "{}"

            cleaned = self.clean_json_string(raw_text)
            data = json.loads(cleaned) if cleaned else {}
            
            return EscalationResponse(
                escalation_score=float(data.get("escalation_score", 0.0)),
                escalation_recommended=bool(data.get("escalation_recommended", False)),
                reasons=list(data.get("reasons", []))
            )
            
        except Exception as e:
            logger.error(f"EscalationService error: {e}")
            return EscalationResponse(
                escalation_score=0.0,
                escalation_recommended=False,
                reasons=[]
            )

def get_escalation_service() -> EscalationService:
    return EscalationService()
