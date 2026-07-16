import json
import re
import logging
from typing import Dict, Any, Optional
from app.schemas.ai_response import StructuredAIResponse

logger = logging.getLogger("app.services.output_validator")

class OutputValidator:
    @staticmethod
    def clean_json_string(text: str) -> str:
        """
        Cleans markdown wrappers like ```json ... ``` and leading/trailing whitespace
        to ensure we parse pure JSON strings.
        """
        if not text:
            return ""
        
        cleaned = text.strip()
        # Remove markdown code block delimiters
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    @staticmethod
    def validate_and_parse(raw_output: str) -> StructuredAIResponse:
        """
        Parses raw text into StructuredAIResponse.
        If parsing fails, performs sanitization and provides a valid fallback response.
        """
        cleaned = OutputValidator.clean_json_string(raw_output)
        
        try:
            data = json.loads(cleaned)
            # Ensure required keys exist with safe defaults
            validated_data = {
                "response": str(data.get("response", "Thank you for reaching out. How can I assist you today?")),
                "intent": str(data.get("intent", "general_inquiry")),
                "sentiment": str(data.get("sentiment", "neutral")),
                "category": str(data.get("category", "general")),
                "urgency": str(data.get("urgency", "medium")),
                "entities": dict(data.get("entities", {})),
                "suggested_actions": list(data.get("suggested_actions", ["Get support", "View tickets"]))
            }
            return StructuredAIResponse(**validated_data)
        except Exception as e:
            logger.error(f"Validation failed for raw output: {raw_output}. Error: {e}")
            
            # If JSON parsing completely fails, we use a regex heuristic to extract response
            response_match = re.search(r'"response"\s*:\s*"([^"]+)"', cleaned)
            extracted_response = response_match.group(1) if response_match else "I'm having trouble processing that request right now. Let me know how I can help you."
            
            return StructuredAIResponse(
                response=extracted_response,
                intent="general_inquiry",
                sentiment="neutral",
                category="general",
                urgency="medium",
                entities={},
                suggested_actions=["Check status", "Raise support ticket"]
            )
