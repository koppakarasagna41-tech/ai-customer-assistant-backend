import logging

from app.schemas.message import Message

logger = logging.getLogger("app.services.token_optimizer")


class TokenOptimizer:
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimates the number of tokens in a string.
        A good rule of thumb is 1 token = 4 characters or ~0.75 words.
        """
        if not text:
            return 0
        return len(text) // 4 + 1

    @staticmethod
    def estimate_message_tokens(message: Message) -> int:
        return TokenOptimizer.estimate_tokens(message.content) + 4

    @staticmethod
    def optimize_history(history: list[Message], max_tokens: int = 4000) -> list[Message]:
        """
        Optimizes history by removing older messages or duplicate messages
        until the total token count is within max_tokens.
        Always keeps system instructions or first message if crucial,
        but for chat context, we retain the most recent messages.
        """
        optimized = []
        total_tokens = 0
        seen_contents = set()

        # Iterate backwards to preserve the most recent messages
        for msg in reversed(history):
            # Input Optimization: Prevent duplicate or consecutive duplicate messages
            normalized_content = " ".join(msg.content.strip().lower().split())
            if normalized_content in seen_contents:
                logger.info(f"Omitting duplicate historical message: {msg.content[:30]}...")
                continue

            seen_contents.add(normalized_content)

            tokens = TokenOptimizer.estimate_message_tokens(msg)
            if total_tokens + tokens > max_tokens:
                logger.info(
                    "Optimizing context window: Truncating history after reaching "
                    f"limit of {max_tokens} tokens."
                )
                break

            optimized.insert(0, msg)
            total_tokens += tokens

        return optimized

    @staticmethod
    def should_summarize(history: list[Message], threshold_tokens: int = 3000) -> bool:
        """
        Determines whether the conversation is long enough to trigger auto-summarization.
        """
        total = sum(TokenOptimizer.estimate_message_tokens(m) for m in history)
        return total > threshold_tokens
