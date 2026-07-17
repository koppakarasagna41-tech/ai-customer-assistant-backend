import asyncio
import contextlib
import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger("app.services.gemini_client")


class GeminiClient:
    def __init__(self, api_key: str | None = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured in the environment.")
        self.model_name = model_name
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @staticmethod
    def _perform_request(request: urllib.request.Request) -> str:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8")

    async def generate_content(
        self,
        contents: list,
        system_instruction: str | None = None,
        response_schema: dict | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1500,
        response_mime_type: str = "text/plain",
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
                "responseMimeType": response_mime_type,
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        if response_schema and response_mime_type == "application/json":
            payload["generationConfig"]["responseSchema"] = response_schema

        headers = {"Content-Type": "application/json", "User-Agent": "aistudio-build"}

        # Retry logic with exponential backoff
        max_retries = 3
        backoff = 1.0

        for attempt in range(max_retries):
            try:
                # Run the synchronous urllib blocking call in a separate thread/executor
                loop = asyncio.get_running_loop()
                req = urllib.request.Request(
                    url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
                )

                response_body = await loop.run_in_executor(None, self._perform_request, req)
                return json.loads(response_body)

            except urllib.error.HTTPError as e:
                error_body = ""
                with contextlib.suppress(Exception):
                    error_body = e.read().decode("utf-8")
                logger.error(
                    "Gemini API HTTP Error (Attempt %s/%s): %s - %s. Body: %s",
                    attempt + 1,
                    max_retries,
                    e.code,
                    e.reason,
                    error_body,
                )
                if attempt == max_retries - 1:
                    raise ValueError(
                        f"Gemini API returned error: {e.code} - {e.reason}. Body: {error_body}"
                    ) from e
                await asyncio.sleep(backoff)
                backoff *= 2

            except Exception as e:
                logger.error(
                    "Gemini API Network Exception (Attempt %s/%s): %s",
                    attempt + 1,
                    max_retries,
                    e,
                )
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to communicate with Gemini API: {e!s}") from e
                await asyncio.sleep(backoff)
                backoff *= 2

        raise ValueError("Failed to obtain a response from Gemini API after maximum retries.")


def get_gemini_client() -> GeminiClient:
    return GeminiClient()
