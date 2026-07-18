import logging
import os
from typing import cast

from app.services.gemini_client import get_gemini_client

logger = logging.getLogger("app.services.query_rewriter")


class QueryRewriter:
    def __init__(self, prompts_dir: str | None = None):
        self.gemini = get_gemini_client()
        self.prompts_dir = prompts_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts"
        )
        self._prompt_template = ""
        self._load_template()

    def _load_template(self):
        prompt_path = os.path.join(self.prompts_dir, "query_rewrite.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, encoding="utf-8") as f:
                self._prompt_template = f.read()
        else:
            self._prompt_template = (
                "Rewrite this query for vector similarity search. "
                "Remove greetings and filler words. "
                "Output ONLY the final query: {query}"
            )

    async def rewrite(self, query: str) -> str:
        """
        Rewrites a raw user query.
        Cleans greetings locally first, then uses Gemini to semantically expand and structure.
        """
        cleaned = self._local_clean(query)
        if not cleaned:
            return query

        try:
            prompt = self._prompt_template.format(query=cleaned)
            contents = [{"role": "user", "parts": [{"text": prompt}]}]

            res = await self.gemini.generate_content(
                contents=contents,
                system_instruction=(
                    "You are a professional query rewritter. "
                    "Output only the rewritten plain text."
                ),
                temperature=0.1,
                max_output_tokens=100,
            )
            rewritten = cast(str, res["candidates"][0]["content"]["parts"][0]["text"].strip())
            # Safety fallback: if rewritten is empty or error, use cleaned
            if rewritten:
                logger.info(f"Query rewritten: '{query}' -> '{rewritten}'")
                return rewritten
        except Exception as e:
            logger.warning(f"Failed to rewrite query via Gemini: {e}. Using locally cleaned query.")

        return cleaned

    def _local_clean(self, query: str) -> str:
        """Removes greetings and conversational filler words locally to optimize latency."""
        q = query.strip()
        # Common conversational prefixes and filler phrases to strip
        fillers = [
            (
                r"^(hi|hello|hey|greetings|good morning|good afternoon|excuse me)"
                r"\s*(assistant|ai|there)?\s*[\,\.\!\?]*\s*"
            ),
            r"^can you please tell me\s*",
            r"^could you please help me with\s*",
            r"^i want to know\s*",
            r"^do you know\s*",
            r"^i am looking for information on\s*",
            r"^please explain\s*",
        ]

        import re

        for pattern in fillers:
            q = re.sub(pattern, "", q, flags=re.IGNORECASE)

        return q.strip()


def get_query_rewriter() -> QueryRewriter:
    return QueryRewriter()
