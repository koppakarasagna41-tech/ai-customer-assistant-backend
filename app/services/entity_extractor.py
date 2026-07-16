import os
import json
import logging
import re
from app.services.gemini_client import get_gemini_client, GeminiClient
from app.schemas.entities import ExtractedEntities, Entity

logger = logging.getLogger("app.services.entity_extractor")

class EntityExtractor:
    def __init__(self, gemini_client: GeminiClient = None):
        self.client = gemini_client or get_gemini_client()
        self.prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts", "entity_prompt.txt"
        )
        self.prompt = ""
        self._load_prompt()

    def _load_prompt(self):
        try:
            if os.path.exists(self.prompt_path):
                with open(self.prompt_path, "r", encoding="utf-8") as f:
                    self.prompt = f.read()
            else:
                self.prompt = "Extract entities from support messages."
        except Exception as e:
            logger.error(f"Error loading entity prompt: {e}")
            self.prompt = "Extract entities from support messages."

    def clean_json_string(self, text: str) -> str:
        if not text:
            return ""
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    async def extract_entities(self, text: str) -> ExtractedEntities:
        if not text:
            return ExtractedEntities(entities=[])

        try:
            schema = ExtractedEntities.model_json_schema()
            contents = [
                {"role": "user", "parts": [{"text": f"Message to extract entities from:\n\n{text}"}]}
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
                logger.error(f"Malformed response format from Gemini client in EntityExtractor: {e}")
                raw_text = "{}"

            cleaned = self.clean_json_string(raw_text)
            data = json.loads(cleaned) if cleaned else {}
            
            entities_list = []
            for item in data.get("entities", []):
                entities_list.append(
                    Entity(
                        name=str(item.get("name", "")),
                        type=str(item.get("type", "UNKNOWN")),
                        confidence=float(item.get("confidence", 1.0))
                    )
                )
            return ExtractedEntities(entities=entities_list)
            
        except Exception as e:
            logger.error(f"EntityExtractor error: {e}")
            return ExtractedEntities(entities=[])

def get_entity_extractor() -> EntityExtractor:
    return EntityExtractor()
