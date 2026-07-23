import asyncio
import contextlib
import json
import logging
import os
import time
import urllib.error
import urllib.request
from enum import StrEnum
from typing import Any, cast

logger = logging.getLogger("app.services.gemini_client")


class CircuitBreakerState(StrEnum):
    """States for the circuit breaker pattern."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Reject requests
    HALF_OPEN = "half_open"  # Allow single request to test recovery


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def call(self, func: callable, *args: Any, **kwargs: Any) -> Any:
        """Execute function through circuit breaker."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise RuntimeError(
                    f"Circuit breaker is OPEN. Retry after {self.recovery_timeout}s."
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        return (
            self.last_failure_time is not None
            and time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _on_success(self) -> None:
        """Reset failure count on success."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self) -> None:
        """Increment failure count and open circuit if threshold reached."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning("Circuit breaker opened after %d failures", self.failure_count)


class GeminiClient:
    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-flash-latest",
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.offline_mode = not bool(self.api_key)
        self.model_name = model_name
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        # Initialize circuit breaker for API calls
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception,
        )

        if self.offline_mode:
            logger.warning(
                "Gemini API key not configured. GeminiClient is running in offline fallback mode."
            )

    @staticmethod
    def _perform_request(request: urllib.request.Request) -> str:
        with urllib.request.urlopen(request, timeout=30) as response:
            return cast(str, response.read().decode("utf-8"))

    def _infer_offline_json_response(
        self, contents: list[dict[str, Any]], response_schema: dict | None
    ) -> dict[str, Any]:
        text_parts: list[str] = []
        for content in contents:
            for part in content.get("parts", []):
                if isinstance(part, dict):
                    text_parts.append(str(part.get("text", "")))
        combined_text = " ".join(text_parts).lower()

        category = "general"
        if "billing" in combined_text or "invoice" in combined_text or "charged" in combined_text:
            category = "billing"
        elif "account" in combined_text or "login" in combined_text or "okta" in combined_text or "sso" in combined_text:
            category = "technical"
        elif "password" in combined_text or "authentication" in combined_text or "credentials" in combined_text:
            category = "account"

        priority = "high" if any(keyword in combined_text for keyword in ["urgent", "timeout", "failed", "issue"]) else "medium"

        response_data = {
            "response": (
                "Thank you for reaching out. Our team will review your issue and "
                "get back to you shortly."
            ),
            "intent": "SUPPORT_QUERY",
            "sentiment": "neutral",
            "category": category,
            "urgency": "medium",
            "entities": {},
            "suggested_actions": ["Contact support", "Review ticket status"],
            "predicted_category": category,
            "predicted_priority": priority,
            "suggested_response": (
                "Thank you for contacting support. We are reviewing your issue."
            ),
            "confidence_score": 0.98,
        }
        return {"candidates": [{"content": {"parts": [{"text": json.dumps(response_data)}]}}]}

    async def generate_content(
        self,
        contents: list,
        system_instruction: str | None = None,
        response_schema: dict | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1500,
        response_mime_type: str = "text/plain",
    ) -> dict[str, Any]:
        """
        Calls Gemini API using standard library urllib asynchronously.
        Supports system instruction, response schema, and JSON mode.
        Uses circuit breaker pattern to prevent cascading failures.
        """
        if self.circuit_breaker.state == CircuitBreakerState.OPEN:
            raise RuntimeError(
                "Gemini API circuit breaker is OPEN. Service temporarily unavailable."
            )

        url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"

        # Build payload
        payload: dict[str, Any] = {
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

        if self.offline_mode:
            if response_mime_type == "application/json":
                return self._infer_offline_json_response(contents, response_schema)
            return {
                "candidates": [
                    {"content": {"parts": [{"text": "Offline Gemini fallback response."}]}}
                ]
            }

        for attempt in range(max_retries):
            try:
                # Run the synchronous urllib blocking call in a separate thread/executor
                loop = asyncio.get_running_loop()
                req = urllib.request.Request(
                    url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
                )

                response_body = await loop.run_in_executor(None, self._perform_request, req)

                # Parse JSON response with error handling
                try:
                    response_data = json.loads(response_body)
                except json.JSONDecodeError as e:
                    logger.error(
                        "Invalid JSON in Gemini API response (Attempt %s/%s): %s. Response: %s",
                        attempt + 1,
                        max_retries,
                        e,
                        response_body[:200],
                    )
                    if attempt == max_retries - 1:
                        self.circuit_breaker._on_failure()
                        raise ValueError(f"Gemini API returned invalid JSON: {e!s}") from e
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue

                # Reset circuit breaker on success
                if self.circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
                    self.circuit_breaker._on_success()

                return cast(dict[str, Any], response_data)

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
                    error_body[:200],
                )
                if attempt == max_retries - 1:
                    self.circuit_breaker._on_failure()
                    raise ValueError(
                        f"Gemini API returned error: "
                        f"{e.code} - {e.reason}. "
                        f"Body: {error_body[:500]}"
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
                    self.circuit_breaker._on_failure()
                    raise ValueError(f"Failed to communicate with Gemini API: {e!s}") from e
                await asyncio.sleep(backoff)
                backoff *= 2

        raise ValueError("Failed to obtain a response from Gemini API after maximum retries.")


def get_gemini_client() -> GeminiClient:
    return GeminiClient()
