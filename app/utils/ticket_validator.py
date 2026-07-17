# We will define standard exception classes locally or assume exceptions
# folder is used. Let's write standard custom exceptions inside
# utils/ticket_validator.py or create a simple exception file first, or raise
# ValueError / HTTPException directly. Wait, let's raise custom ValueError /
# standard ValueError and map them in the exception handler or handle them in
# service. Let's write custom validator rules that are easy to use.

VALID_STATUSES = {"open", "in_progress", "closed", "escalated"}
VALID_PRIORITIES = {"low", "medium", "high", "urgent"}


class TicketValidator:
    @staticmethod
    def validate_priority(priority: str) -> None:
        if priority.lower() not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of {VALID_PRIORITIES}")

    @staticmethod
    def validate_status(status: str) -> None:
        if status.lower() not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {VALID_STATUSES}")

    @staticmethod
    def validate_status_transition(current_status: str, new_status: str) -> None:
        current = current_status.lower()
        new = new_status.lower()

        if current == new:
            return

        # Closed tickets can only transition to open
        if current == "closed" and new != "open":
            raise ValueError("Closed tickets can only be transitioned back to 'open' status.")

        # Unchanged check
        if new not in VALID_STATUSES:
            raise ValueError(f"Target status '{new}' is invalid.")

    @staticmethod
    def sanitize_text(text: str) -> str:
        if not text:
            return ""
        # Simple HTML sanitization and strip whitespaces
        import html

        return html.escape(text.strip())
