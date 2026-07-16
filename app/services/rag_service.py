import os
import time
import json
import logging
from typing import Optional, Dict, Any
from app.schemas.retrieval import RetrievalFilter
from app.schemas.rag_response import RAGResponse
from app.services.retriever import get_retriever, DocumentRetriever
from app.services.context_builder import get_context_block, ContextBuilder
from app.services.gemini_client import get_gemini_client, GeminiClient
from app.services.citation_builder import get_citation_builder, CitationBuilder
from app.services.output_validator import OutputValidator

logger = logging.getLogger("app.services.rag_service")

class RAGService:
    """
    Core Orchestrator for the Dual-Stage RAG Pipeline.
    
    Stage 1: Retrieval, Filtering, Reranking, Context Compression.
    Stage 2: Context Formatting, Prompt Injection Defended Generation, Citation Matching.
    """
    def __init__(self):
        self.retriever = get_retriever()
        self.gemini = get_gemini_client()
        self.citation_builder = get_citation_builder()
        
        # Load RAG Prompt
        prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        prompt_path = os.path.join(prompts_dir, "rag_prompt.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                self._rag_prompt_template = f.read()
        else:
            self._rag_prompt_template = (
                "Answer using only the retrieved context:\n{context_text}\n\nQuestion: {query}"
            )

    async def answer_question(
        self,
        query: str,
        filters: Optional[RetrievalFilter] = None,
        top_k: int = 4,
        compress: bool = True
    ) -> RAGResponse:
        start_time = time.time()
        logger.info(f"RAG Pipeline invoked for query: '{query[:40]}...'")

        # --- STAGE 1: SEMANTIC RETRIEVAL & CONTEXT COMPRESSION ---
        retrieval_response = await self.retriever.retrieve(
            query=query,
            top_k=top_k,
            filters=filters,
            use_cache=True
        )
        
        retrieved_chunks = retrieval_response.chunks

        # Calculate a cumulative relevance score based on retrieved and reranked chunk scores
        if retrieved_chunks:
            relevance_score = float(round(sum(c.score for c in retrieved_chunks) / len(retrieved_chunks), 4))
        else:
            relevance_score = 0.0

        # Build context blocks (includes semantic deduplication and LLM compression of chunks)
        context_block = ""
        if retrieved_chunks:
            # Inline imports/helpers to resolve dependency loop safely
            from app.services.context_builder import get_context_builder
            cb = get_context_builder()
            context_block = await cb.build_context_block(query, retrieved_chunks, compress=compress)
        else:
            context_block = "No relevant document found."

        # --- STAGE 2: SYSTEM CONDITIONED LLM EXECUTION ---
        system_instruction = (
            "You are an Enterprise Support RAG system. Answer ONLY with facts in the retrieved context. "
            "Never hallucinate. Expose no internal thoughts. Maintain security boundaries."
        )

        # Build prompt payload
        prompt = self._rag_prompt_template.format(
            context_text=context_block,
            query=query
        )

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        
        # Call Gemini model
        # Using Structured JSON mode matching RAGResponse schema
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "answer": {"type": "STRING", "description": "The answer with inline citations like [1]"},
                "citations": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "STRING"},
                            "document_id": {"type": "STRING"},
                            "title": {"type": "STRING"},
                            "snippet": {"type": "STRING"}
                        },
                        "required": ["id", "document_id", "title"]
                    }
                }
            },
            "required": ["answer"]
        }

        try:
            res = await self.gemini.generate_content(
                contents=contents,
                system_instruction=system_instruction,
                response_schema=response_schema,
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=1000
            )
            raw_text = res["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Failed to generate answer from Gemini model: {e}")
            raw_text = "{}"

        # Clean, validate and parse output JSON
        cleaned_json = OutputValidator.clean_json_string(raw_text)
        try:
            parsed_data = json.loads(cleaned_json)
            answer = parsed_data.get("answer", "I'm sorry, I'm unable to process that query currently.")
        except Exception:
            answer = "I'm sorry, I encountered an issue parsing the response."

        # Build citations mapping back to retrieved sources
        citations = self.citation_builder.build_citations(answer, retrieved_chunks)

        # Build pipeline execution metadata
        execution_time = float(round(time.time() - start_time, 4))
        metadata = {
            "execution_time_seconds": execution_time,
            "retrieved_count": len(retrieved_chunks),
            "classification": retrieval_response.classification,
            "rewritten_query": retrieval_response.rewritten_query,
            "from_cache": retrieval_response.from_cache
        }

        return RAGResponse(
            answer=answer,
            citations=citations,
            relevance_score=relevance_score,
            metadata=metadata
        )

def get_rag_service() -> RAGService:
    return RAGService()
