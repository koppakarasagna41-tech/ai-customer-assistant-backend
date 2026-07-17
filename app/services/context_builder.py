import logging
import os

from app.schemas.retrieval import RetrievedChunk
from app.services.gemini_client import get_gemini_client

logger = logging.getLogger("app.services.context_builder")


class ContextBuilder:
    """
    Consolidates, deduplicates, and compresses retrieved chunks into a pristine
    formatted reference block for the LLM.
    """

    def __init__(self):
        self.gemini = get_gemini_client()
        self._compression_template = ""
        self._load_template()

    def _load_template(self):
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts", "context_compression.txt"
        )
        if os.path.exists(prompt_path):
            with open(prompt_path, encoding="utf-8") as f:
                self._compression_template = f.read()
        else:
            self._compression_template = (
                "Query: {query}\n"
                "Chunk: {chunk_text}\n"
                "Keep only relevant sentences to answer the query."
            )

    async def build_context_block(
        self, query: str, chunks: list[RetrievedChunk], compress: bool = True
    ) -> str:
        """
        Deduplicates, compresses, and builds a clean context block.
        """
        if not chunks:
            return "No relevant company documentation found."

        # 1. Deduplicate by content
        unique_chunks = []
        seen_texts = set()

        for chunk in chunks:
            normalized_text = " ".join(chunk.content.strip().lower().split())
            # Jaccard distance or exact check to filter near duplicates
            is_duplicate = False
            for seen in seen_texts:
                if normalized_text == seen or seen in normalized_text or normalized_text in seen:
                    is_duplicate = True
                    break
            if not is_duplicate:
                seen_texts.add(normalized_text)
                unique_chunks.append(chunk)

        # 2. Compress chunks asynchronously using Gemini if requested
        compressed_texts = []
        for idx, chunk in enumerate(unique_chunks, start=1):
            chunk_content = chunk.content
            if compress and len(chunk_content) > 300:  # only compress larger chunks
                try:
                    prompt = self._compression_template.format(
                        query=query, chunk_text=chunk_content
                    )
                    contents = [{"role": "user", "parts": [{"text": prompt}]}]
                    res = await self.gemini.generate_content(
                        contents=contents,
                        system_instruction=(
                            "You are an expert context compressor. Respond ONLY with "
                            "compressed sentences or 'IRRELEVANT'."
                        ),
                        temperature=0.1,
                        max_output_tokens=200,
                    )
                    compressed = res["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if compressed and "IRRELEVANT" not in compressed.upper():
                        chunk_content = compressed
                except Exception as e:
                    logger.warning(f"Compression failed for chunk {chunk.chunk_id}: {e}")

            # Format cleanly with index and source title
            title = chunk.metadata.get("title", "Reference Doc")
            compressed_texts.append(
                f"[{idx}] Source: {title} (Doc ID: {chunk.document_id})\n{chunk_content}\n"
            )

        return "\n".join(compressed_texts)


def get_context_builder() -> ContextBuilder:
    return ContextBuilder()


def get_context_block(query: str, chunks: list[RetrievedChunk], compress: bool = True) -> str:
    import asyncio

    builder = get_context_builder()
    return asyncio.run(builder.build_context_block(query, chunks, compress=compress))
