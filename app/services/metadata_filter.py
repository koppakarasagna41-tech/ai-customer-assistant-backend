import logging
from typing import Any

from app.schemas.retrieval import RetrievalFilter

logger = logging.getLogger("app.services.metadata_filter")


class MetadataFilterBuilder:
    """
    Builds clean metadata filter dictionaries for vector store queries.
    Enforces category or product restrictions automatically if matched in the query.
    """

    @staticmethod
    def build_filters(
        request_filter: RetrievalFilter | None = None,
        extracted_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        filters = {}

        # 1. Apply explicit request filters
        if request_filter:
            if request_filter.category:
                filters["category"] = request_filter.category
            if request_filter.product:
                filters["product"] = request_filter.product
            if request_filter.custom_filters:
                filters.update(request_filter.custom_filters)

        # 2. Enrich with extracted query entities if not explicitly overridden
        if extracted_metadata:
            if "product" in extracted_metadata.get("entities", {}) and "product" not in filters:
                filters["product"] = extracted_metadata["entities"]["product"]
            if (
                extracted_metadata.get("category")
                and extracted_metadata["category"] != "general"
                and "category" not in filters
                and extracted_metadata["category"] in ["billing", "account"]
            ):
                filters["category"] = extracted_metadata["category"]

        return filters


def get_metadata_filter_builder() -> MetadataFilterBuilder:
    return MetadataFilterBuilder()
