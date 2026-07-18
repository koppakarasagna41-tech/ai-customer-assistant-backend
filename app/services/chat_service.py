import logging
from datetime import datetime
from typing import Any

from app.schemas.ai_response import StructuredAIResponse
from app.schemas.chat import ChatMetadata, ChatResponse
from app.schemas.message import Message
from app.services.context_manager import ContextManager
from app.services.conversation_memory import ConversationMemory, get_conversation_memory
from app.services.gemini_client import GeminiClient, get_gemini_client
from app.services.output_validator import OutputValidator
from app.services.prompt_builder import PromptBuilder
from app.services.token_optimizer import TokenOptimizer

logger = logging.getLogger("app.services.chat_service")


class ChatService:
    def __init__(
        self,
        memory: ConversationMemory | None = None,
        context_manager: ContextManager | None = None,
        prompt_builder: PromptBuilder | None = None,
        gemini_client: GeminiClient | None = None,
    ):
        self.memory = memory or get_conversation_memory()
        self.context_manager = context_manager or ContextManager()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.gemini_client = gemini_client or get_gemini_client()

    async def process_chat_message(
        self,
        message_text: str,
        session_id: str,
        user_id: str | None = None,
        client_metadata: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """
        Processes a chat request using the Dual-Stage pipeline:
        Stage 1: Input Optimization, Context Compression, and Prompt Preparation.
        Stage 2: Gemini Execution, Output Validation, JSON parsing,
        Safety/Reflection checks, and Summary trigger.
        """
        logger.info(f"Processing chat message for session: {session_id}")

        # --- STAGE 1: INPUT OPTIMIZATION & PROMPT PREPARATION ---

        # 1. Normalize and Trim Whitespace
        sanitized_message = " ".join(message_text.strip().split())
        if not sanitized_message:
            raise ValueError("Input message cannot be empty or whitespace only.")

        # 2. Get or create conversation memory state
        state = await self.memory.get_or_create(session_id, user_id)

        # 3. Add user message to history
        user_message = Message(role="user", content=sanitized_message, timestamp=datetime.utcnow())
        await self.memory.add_message(session_id, user_message)

        # 4. Build enriched contextual knowledge
        enriched_context = await self.context_manager.build_enriched_context(
            user_id=user_id, session_id=session_id, client_metadata=client_metadata
        )
        if state.summary:
            enriched_context["conversation_summary"] = state.summary

        # 5. Compress context & optimize historical messages
        optimized_history = TokenOptimizer.optimize_history(state.messages, max_tokens=3000)

        # Convert history models to raw list for prompt builder
        history_list = [
            {"role": m.role, "content": m.content}
            for m in optimized_history[:-1]  # exclude the last user message we just appended
        ]

        # 6. Build prompts and contents
        system_instruction = self.prompt_builder.build_system_instruction()
        contents = self.prompt_builder.build_contents(
            user_message=sanitized_message, history=history_list, context=enriched_context
        )

        # Calculate input tokens estimate
        input_tokens = TokenOptimizer.estimate_tokens(system_instruction) + sum(
            TokenOptimizer.estimate_tokens(part["text"]) for c in contents for part in c["parts"]
        )

        # --- STAGE 2: GEMINI EXECUTION & OUTPUT VALIDATION ---

        # Define expected output schema for the structured JSON response
        # Using Type.OBJECT and properties
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "response": {"type": "STRING", "description": "Text response to user"},
                "intent": {"type": "STRING", "description": "Detected user intent"},
                "sentiment": {"type": "STRING", "description": "Detected user sentiment"},
                "category": {"type": "STRING", "description": "Detected category"},
                "urgency": {"type": "STRING", "description": "Detected urgency level"},
                "entities": {
                    "type": "OBJECT",
                    "description": "Extracted key-value pairs (e.g. ticket_id)",
                },
                "suggested_actions": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "1 to 3 actions",
                },
            },
            "required": [
                "response",
                "intent",
                "sentiment",
                "category",
                "urgency",
                "suggested_actions",
            ],
        }

        # Call Gemini
        raw_res = await self.gemini_client.generate_content(
            contents=contents,
            system_instruction=system_instruction,
            response_schema=response_schema,
            response_mime_type="application/json",
            temperature=0.2,
        )

        # Extract text from raw response
        try:
            raw_text = raw_res["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(
                f"Malformed response format from Gemini client: {e}. Raw response: {raw_res}"
            )
            raw_text = "{}"

        # Parse and validate structured output
        validated_ai: StructuredAIResponse = OutputValidator.validate_and_parse(raw_text)

        # 7. Add Assistant response to memory
        assistant_message = Message(
            role="assistant", content=validated_ai.response, timestamp=datetime.utcnow()
        )
        await self.memory.add_message(session_id, assistant_message)

        # --- AUTO-SUMMARIZATION TRIGGER ---
        updated_summary = state.summary
        if TokenOptimizer.should_summarize(state.messages, threshold_tokens=2500):
            logger.info(f"Triggering conversation auto-summarization for session: {session_id}")
            try:
                recent_msgs = [{"role": m.role, "content": m.content} for m in state.messages[-10:]]
                summary_prompt = self.prompt_builder.build_summary_prompt(
                    state.summary or "", recent_msgs
                )
                summary_contents = [{"role": "user", "parts": [{"text": summary_prompt}]}]

                sum_res = await self.gemini_client.generate_content(
                    contents=summary_contents,
                    system_instruction="You are a professional support summaries generator.",
                    response_mime_type="text/plain",
                    temperature=0.1,
                )

                new_summary = sum_res["candidates"][0]["content"]["parts"][0]["text"].strip()
                await self.memory.update_summary(session_id, new_summary)
                updated_summary = new_summary
            except Exception as e:
                logger.error(f"Auto-summarization failed: {e}")

        # Estimate output tokens
        output_tokens = TokenOptimizer.estimate_tokens(raw_text)

        # Build Metadata Response
        chat_metadata = ChatMetadata(
            sentiment=validated_ai.sentiment,
            category=validated_ai.category,
            urgency=validated_ai.urgency,
            entities=validated_ai.entities,
            token_usage={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            },
        )

        return ChatResponse(
            response=validated_ai.response,
            intent=validated_ai.intent,
            suggested_actions=validated_ai.suggested_actions,
            metadata=chat_metadata,
            summary=updated_summary,
        )


def get_chat_service() -> ChatService:
    return ChatService()
