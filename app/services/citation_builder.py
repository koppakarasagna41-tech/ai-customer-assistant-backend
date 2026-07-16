import re
import logging
from typing import List
from app.schemas.retrieval import RetrievedChunk
from app.schemas.rag_response import Citation

logger = logging.getLogger("app.services.citation_builder")

class CitationBuilder:
    """
    Parses generated answer text for citation brackets (e.g., [1], [2])
    and builds strict Citation schema objects mapping back to actual retrieved chunks.
    """
    @staticmethod
    def build_citations(
        answer: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> List[Citation]:
        citations = []
        if not retrieved_chunks:
            return citations

        # Match [1], [2], etc.
        citation_matches = re.findall(r"\[(\d+)\]", answer)
        unique_indices = sorted(list(set([int(m) for m in citation_matches])))

        for idx in unique_indices:
            # Shift 1-indexed citation back to 0-indexed chunk list
            list_idx = idx - 1
            if 0 <= list_idx < len(retrieved_chunks):
                chunk = retrieved_chunks[list_idx]
                citation_id = f"[{idx}]"
                
                # Check if this citation is already created
                if not any(c.id == citation_id for c in citations):
                    citations.append(Citation(
                        id=citation_id,
                        document_id=chunk.document_id,
                        title=chunk.metadata.get("title", "Reference Source"),
                        snippet=chunk.content[:200] + "...", # Snippet from chunk
                        chunk_id=chunk.chunk_id
                    ))
                    
        return citations

def get_citation_builder() -> CitationBuilder:
    return CitationBuilder()
