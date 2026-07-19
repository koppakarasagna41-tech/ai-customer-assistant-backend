import logging

from app.schemas.document import Document
from app.services.chunker import DocumentChunker
from app.services.document_loader import DocumentLoader
from app.services.embedding_service import get_embedding_service
from app.services.vector_store import get_vector_store

logger = logging.getLogger("app.services.document_indexer")


class DocumentIndexer:
    """
    Coordinates Pillar 4 Information Processing:
    Document loading -> Semantic chunking -> Batch Embedding -> Indexing in Vector Database.
    """

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        # Keep an active register of documents indexed
        self._document_registry: dict[str, Document] = {}

    def index_document(self, file_content: bytes, filename: str) -> Document:
        """Loads, chunks, embeds, and indexes a document in the vector store."""
        logger.info(f"Indexing new file: {filename}")

        # 1. Load document text and format metadata
        document = DocumentLoader.load_document(file_content, filename)

        # 2. Split document into sliding-window chunks
        chunks = DocumentChunker.chunk_by_sentences(document, chunk_size=800, chunk_overlap=150)

        if not chunks:
            logger.warning(f"No chunks generated for document: {filename}")
            return document

        # 3. Generate embeddings in batches (Pillar 4 Optimization)
        chunk_texts = [c.content for c in chunks]
        embeddings = self.embedding_service.embed_batch(chunk_texts)

        # Assign embeddings to chunks
        for idx, embedding in enumerate(embeddings):
            chunks[idx].embedding = embedding

        # 4. Save chunks to the Vector Store database
        self.vector_store.add_chunks(chunks)

        # 5. Register document
        document.chunk_count = len(chunks)
        self._document_registry[document.document_id] = document

        logger.info(
            f"Successfully indexed document {document.document_id} ({filename}) with {len(chunks)} chunks."
        )
        return document

    def list_indexed_documents(self) -> list[Document]:
        return list(self._document_registry.values())

    def delete_document(self, document_id: str) -> bool:
        if document_id in self._document_registry:
            self.vector_store.delete_document(document_id)
            del self._document_registry[document_id]
            logger.info(f"Successfully deleted document {document_id} from index registry.")
            return True
        return False


# Single global instance for memory persistence across endpoints
_document_indexer_instance = DocumentIndexer()


def get_document_indexer() -> DocumentIndexer:
    return _document_indexer_instance
