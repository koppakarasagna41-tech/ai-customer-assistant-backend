import json
import logging
import os
from typing import Any

logger = logging.getLogger("app.services.prompt_builder")


class PromptBuilder:
    def __init__(self, prompts_dir: str | None = None):
        self.prompts_dir = prompts_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts"
        )
        self._system_prompt = ""
        self._fewshot_examples: list[dict[str, Any]] = []
        self._reflection_prompt = ""
        self._security_prompt = ""
        self._load_prompts()

    def _load_prompts(self):
        # Load system prompt
        sys_path = os.path.join(self.prompts_dir, "system_prompt.txt")
        if os.path.exists(sys_path):
            with open(sys_path, encoding="utf-8") as f:
                self._system_prompt = f.read()
        else:
            self._system_prompt = "You are a customer support AI assistant."

        # Load fewshot examples
        fewshot_path = os.path.join(self.prompts_dir, "fewshot_examples.json")
        if os.path.exists(fewshot_path):
            try:
                with open(fewshot_path, encoding="utf-8") as f:
                    self._fewshot_examples = json.load(f)
            except Exception as e:
                logger.error(f"Error loading fewshot_examples.json: {e}")
                self._fewshot_examples = []

        # Load reflection prompt
        reflection_path = os.path.join(self.prompts_dir, "reflection_prompt.txt")
        if os.path.exists(reflection_path):
            with open(reflection_path, encoding="utf-8") as f:
                self._reflection_prompt = f.read()

        # Load security prompt
        security_path = os.path.join(self.prompts_dir, "security_prompt.txt")
        if os.path.exists(security_path):
            with open(security_path, encoding="utf-8") as f:
                self._security_prompt = f.read()

    def build_system_instruction(self) -> str:
        """
        Combines System Prompt, Security Guidelines, and Reflection Guidelines.
        """
        prompt_parts = [
            self._system_prompt,
            "\n" + "=" * 40,
            "SECURITY GUIDELINES & PROMPT INJECTION DEFENSE",
            self._security_prompt,
            "\n" + "=" * 40,
            "SELF-VERIFICATION & QUALITY CHECK",
            self._reflection_prompt,
        ]
        return "\n".join(prompt_parts)

    def build_contents(
        self,
        user_message: str,
        history: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> list:
        """
        Builds the contents array for Gemini generateContent, applying few-shot formatting,
        and structuring the context correctly.
        """
        contents = []

        # 1. Add Fewshot examples as training context (using user/model turns)
        for ex in self._fewshot_examples:
            ex_user_text = (
                f"Context: {json.dumps(ex.get('context', {}))}\nMessage: {ex['user_input']}"
            )
            contents.append({"role": "user", "parts": [{"text": ex_user_text}]})
            contents.append(
                {"role": "model", "parts": [{"text": json.dumps(ex["expected_output"])}]}
            )

        # 2. Add historical conversation
        for h in history:
            role = "user" if h["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": h["content"]}]})

        # 3. Add current user message wrapped in its context
        ctx_data = context or {}
        current_input = f"Context: {json.dumps(ctx_data)}\nMessage: {user_message}"
        contents.append({"role": "user", "parts": [{"text": current_input}]})

        return contents

    def build_summary_prompt(
        self, current_summary: str, last_messages: list[dict[str, Any]]
    ) -> str:
        """
        Generates a concise instruction to summarize the conversations.
        """
        return (
            "Given the current conversation summary:\n"
            f"'{current_summary or 'No current summary'}'\n\n"
            f"And the recent messages:\n{json.dumps(last_messages)}\n\n"
            "Please output an updated, very short conversation summary "
            "(max 3 sentences) in plain text."
        )
