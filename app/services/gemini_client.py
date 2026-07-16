import os
import urllib.request
import urllib.error
import json
import logging
import asyncio

logger = logging.getLogger("app.services.gemini_client")

class GeminiClient:
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in the environment.")
        self.model_name = model_name
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate_content(
        self,
        contents: list,
        system_instruction: str = None,
        response_schema: dict = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1500,
        response_mime_type: str = "text/plain"
    ) -> dict:
        """
        Calls Gemini API using standard library urllib asynchronously.
        Supports system instruction, response schema, and JSON mode.
        """
        url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
        
        # Build payload
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
                "responseMimeType": response_mime_type
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
            
        if response_schema and response_mime_type == "application/json":
            payload["generationConfig"]["responseSchema"] = response_schema

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "aistudio-build"
        }
        
        # Retry logic with exponential backoff
        max_retries = 3
        backoff = 1.0
        
        for attempt in range(max_retries):
            try:
                # Run the synchronous urllib blocking call in a separate thread/executor
                loop = asyncio.get_running_loop()
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                
                def perform_request():
                    with urllib.request.urlopen(req, timeout=30) as response:
                        return response.read().decode("utf-8")
                
                response_body = await loop.run_in_executor(None, perform_request)
                return json.loads(response_body)
                
            except urllib.error.HTTPError as e:
                error_body = ""
                try:
                    error_body = e.read().decode("utf-8")
                except Exception:
                    pass
                logger.error(f"Gemini API HTTP Error (Attempt {attempt+1}/{max_retries}): {e.code} - {e.reason}. Body: {error_body}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Gemini API returned error: {e.code} - {e.reason}. Body: {error_body}")
                await asyncio.sleep(backoff)
                backoff *= 2
                
            except Exception as e:
                logger.error(f"Gemini API Network Exception (Attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to communicate with Gemini API: {str(e)}")
                await asyncio.sleep(backoff)
                backoff *= 2
                
        raise ValueError("Failed to obtain a response from Gemini API after maximum retries.")

def get_gemini_client() -> GeminiClient:
    return GeminiClient()
