import logging
import re
from typing import Any

logger = logging.getLogger("app.services.query_classifier")


class QueryClassifier:
    """
    Classifies queries locally using pattern matching and regular expressions.
    Extracts key product entities, categories, and ticket IDs to optimize routing.
    """

    @staticmethod
    def classify_query(query: str) -> dict[str, Any]:
        q = query.lower()

        # Default classification
        category = "general"
        urgency = "medium"
        entities = {}

        # Regex Entity Extraction
        # Ticket ID pattern (e.g., TCK-12345 or TCK-999)
        ticket_match = re.search(r"tck-\d{3,6}", q)
        if ticket_match:
            entities["ticket_id"] = ticket_match.group(0).upper()
            category = "ticket_inquiry"
            urgency = "high"

        # Product matching
        products = ["cloud", "billing_system", "database", "portal", "agent_app"]
        for p in products:
            if p in q or p.replace("_", " ") in q:
                entities["product"] = p

        # Intent categorization
        if any(
            w in q
            for w in ["refund", "billing", "pricing", "cost", "invoice", "payment", "subscription"]
        ):
            category = "billing"
            if any(w in q for w in ["charge twice", "wrong charge", "fraud"]):
                urgency = "high"
        elif any(
            w in q for w in ["password", "reset", "login", "account", "mfa", "sign in", "signup"]
        ):
            category = "account"
        elif any(
            w in q
            for w in ["bug", "error", "crash", "broken", "fail", "slow", "down", "not working"]
        ):
            category = "troubleshooting"
            urgency = "high"
        elif any(
            w in q for w in ["how to", "guide", "documentation", "manual", "setup", "install"]
        ):
            category = "documentation"
            urgency = "low"

        return {"category": category, "urgency": urgency, "entities": entities}


def get_query_classifier() -> QueryClassifier:
    return QueryClassifier()
