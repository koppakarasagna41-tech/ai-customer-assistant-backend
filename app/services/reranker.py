import logging
import re

from app.schemas.retrieval import RetrievedChunk

logger = logging.getLogger("app.services.reranker")


class SemanticReranker:
    """
    Reranks candidate chunks by calculating a hybrid score combining:
    1. Base vector similarity score.
    2. Word intersection (lexical overlap).
    3. Exact phrase alignment of query tokens inside document body.
    """

    @staticmethod
    def rerank(
        query: str, candidates: list[RetrievedChunk], top_n: int = 3
    ) -> list[RetrievedChunk]:
        if not candidates:
            return []

        reranked = []
        normalized_query_words = set(re.findall(r"\w+", query.lower()))

        for item in candidates:
            content_lower = item.content.lower()
            content_words = set(re.findall(r"\w+", content_lower))

            # 1. Lexical overlap (Jaccard similarity)
            intersection = normalized_query_words.intersection(content_words)
            lexical_score = len(intersection) / max(len(normalized_query_words), 1)

            # 2. Exact phrase matching (bonus score if words appear sequentially)
            phrase_bonus = 0.0
            # Check matching of 2-word shingles from query
            query_word_list = list(re.findall(r"\w+", query.lower()))
            if len(query_word_list) >= 2:
                for i in range(len(query_word_list) - 1):
                    shingle = f"{query_word_list[i]} {query_word_list[i+1]}"
                    if shingle in content_lower:
                        phrase_bonus += 0.15

            # Limit max bonus
            phrase_bonus = min(phrase_bonus, 0.4)

            # 3. Compute hybrid score (e.g. 50% Vector similarity, 30% Lexical, 20% phrase matching)
            hybrid_score = (item.score * 0.5) + (lexical_score * 0.3) + phrase_bonus

            # Update chunk score and append
            item.score = float(round(hybrid_score, 4))
            reranked.append(item)

        # Sort descending by updated hybrid score
        reranked.sort(key=lambda x: x.score, reverse=True)

        logger.info(f"Reranked {len(candidates)} down to top {min(top_n, len(reranked))} chunks.")
        return reranked[:top_n]


def get_reranker() -> SemanticReranker:
    return SemanticReranker()
