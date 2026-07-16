import re
from typing import List
from app.schemas.document import Document
from app.schemas.chunk import Chunk

class DocumentChunker:
    @staticmethod
    def chunk_by_words(
        document: Document,
        chunk_size: int = 200,
        chunk_overlap: int = 40
    ) -> List[Chunk]:
        """
        Splits a document's content into chunk objects based on word counts.
        Provides a flexible overlap window.
        """
        content = document.content
        words = content.split()
        total_words = len(words)
        
        if total_words == 0:
            return []
            
        chunks = []
        chunk_index = 0
        
        start = 0
        while start < total_words:
            end = min(start + chunk_size, total_words)
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunk_id = f"{document.id}-CH-{chunk_index:03d}"
            
            # Formulate metadata dictionary
            metadata = {
                "title": document.metadata.title,
                "source": document.metadata.source,
                "category": document.metadata.category,
                "product": document.metadata.product,
                "word_count": len(chunk_words)
            }
            if document.metadata.custom_metadata:
                metadata.update(document.metadata.custom_metadata)
                
            chunks.append(Chunk(
                id=chunk_id,
                document_id=document.id,
                index=chunk_index,
                content=chunk_text,
                metadata=metadata
            ))
            
            chunk_index += 1
            
            # Advance start pointer by (chunk_size - overlap)
            # Ensure we make progress
            if end == total_words:
                break
            start += max(chunk_size - chunk_overlap, 1)
            
        return chunks

    @staticmethod
    def chunk_by_sentences(
        document: Document,
        chunk_size: int = 1000, # target characters
        chunk_overlap: int = 200
    ) -> List[Chunk]:
        """
        Alternative semantic chunker that splits text at sentence boundaries
        to preserve coherent semantic meaning in each chunk.
        """
        content = document.content
        # Split by periods, question marks, exclamation marks followed by whitespace
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        chunks = []
        current_chunk_sentences = []
        current_length = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            if not sentence.strip():
                continue
                
            # If a single sentence exceeds size, add what we have, then add this sentence
            if current_length + sentence_len > chunk_size and current_chunk_sentences:
                chunk_text = " ".join(current_chunk_sentences)
                chunk_id = f"{document.id}-CH-{chunk_index:03d}"
                
                metadata = {
                    "title": document.metadata.title,
                    "source": document.metadata.source,
                    "category": document.metadata.category,
                    "product": document.metadata.product,
                    "char_count": len(chunk_text)
                }
                if document.metadata.custom_metadata:
                    metadata.update(document.metadata.custom_metadata)
                
                chunks.append(Chunk(
                    id=chunk_id,
                    document_id=document.id,
                    index=chunk_index,
                    content=chunk_text,
                    metadata=metadata
                ))
                
                chunk_index += 1
                
                # Overlap logic: keep some of the last sentences
                overlap_length = 0
                overlap_sentences = []
                for s in reversed(current_chunk_sentences):
                    if overlap_length + len(s) < chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_length += len(s)
                    else:
                        break
                current_chunk_sentences = overlap_sentences
                current_length = sum(len(s) for s in current_chunk_sentences)
                
            current_chunk_sentences.append(sentence)
            current_length += sentence_len
            
        # Add remaining text
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunk_id = f"{document.id}-CH-{chunk_index:03d}"
            metadata = {
                "title": document.metadata.title,
                "source": document.metadata.source,
                "category": document.metadata.category,
                "product": document.metadata.product,
                "char_count": len(chunk_text)
            }
            if document.metadata.custom_metadata:
                metadata.update(document.metadata.custom_metadata)
                
            chunks.append(Chunk(
                id=chunk_id,
                document_id=document.id,
                index=chunk_index,
                content=chunk_text,
                metadata=metadata
            ))
            
        return chunks
