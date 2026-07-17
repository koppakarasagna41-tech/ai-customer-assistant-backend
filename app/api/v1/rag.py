from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.schemas.document import Document
from app.schemas.rag_response import RAGResponse
from app.schemas.response import BaseResponse
from app.schemas.retrieval import RetrievalFilter
from app.services.document_indexer import DocumentIndexer, get_document_indexer
from app.services.rag_service import RAGService, get_rag_service
from app.services.retriever import DocumentRetriever, get_retriever

router = APIRouter()


# Schema for search request
class RagSearchRequest(BaseModel):
    query: str = Field(..., description="Search terms or query")
    top_k: int | None = Field(4, description="Number of document chunks to retrieve")
    filter: RetrievalFilter | None = Field(None, description="Metadata filtering criteria")


class SearchResult(BaseModel):
    chunk_id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Parent document ID")
    title: str = Field(..., description="Document title")
    text: str = Field(..., description="Document text snippet")
    score: float = Field(..., description="Relevance similarity score")


class RagSearchResponse(BaseModel):
    query: str = Field(..., description="Original user query")
    classification: str = Field(..., description="Query classification category")
    results: list[SearchResult] = Field(..., description="Retrieved search result items")


# Schema for query request
class RagQueryRequest(BaseModel):
    query: str = Field(..., description="Question to answer using the Knowledge Base")
    top_k: int | None = Field(4, description="Number of chunks to retrieve for context")
    filter: RetrievalFilter | None = Field(None, description="Metadata filtering criteria")
    compress: bool | None = Field(True, description="Whether to compress chunks using LLM")


# Schema for text document index request
class IndexTextRequest(BaseModel):
    content: str = Field(..., description="The raw text content of the document")
    filename: str = Field(..., description="The file name representing the document")


@router.post(
    "/rag/search",
    response_model=BaseResponse[RagSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Knowledge Base",
    description=(
        "Searches the vector store database for matching document chunks " "(Stage 1 retrieval)."
    ),
)
async def search_rag(
    payload: RagSearchRequest, retriever: DocumentRetriever = Depends(get_retriever)
):
    try:
        retrieval_res = await retriever.retrieve(
            query=payload.query, top_k=payload.top_k, filters=payload.filter
        )

        results = [
            SearchResult(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                title=c.metadata.get("title", "Reference"),
                text=c.content,
                score=c.score,
            )
            for c in retrieval_res.chunks
        ]

        return BaseResponse(
            success=True,
            message="RAG search complete",
            data=RagSearchResponse(
                query=retrieval_res.query,
                classification=retrieval_res.classification or "general",
                results=results,
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform search: {e!s}",
        ) from e


@router.post(
    "/rag/query",
    response_model=BaseResponse[RAGResponse],
    status_code=status.HTTP_200_OK,
    summary="Query RAG Pipeline",
    description=(
        "Full dual-stage RAG pipeline. Retrieves, reranks, compresses "
        "context, and generates citation-grounded answers."
    ),
)
async def query_rag(payload: RagQueryRequest, rag_service: RAGService = Depends(get_rag_service)):
    try:
        response = await rag_service.answer_question(
            query=payload.query,
            filters=payload.filter,
            top_k=payload.top_k,
            compress=payload.compress,
        )
        return BaseResponse(success=True, message="RAG query complete", data=response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query pipeline execution failed: {e!s}",
        ) from e


@router.post(
    "/rag/index",
    response_model=BaseResponse[Document],
    status_code=status.HTTP_201_CREATED,
    summary="Index Document (Multipart File)",
    description=(
        "Accepts PDF, DOCX, TXT, CSV, JSON, HTML files, chunks them, "
        "generates embeddings, and indexes them."
    ),
)
async def index_file(
    file: UploadFile = File(...), indexer: DocumentIndexer = Depends(get_document_indexer)
):
    try:
        content_bytes = await file.read()
        filename = file.filename or "unknown.txt"

        indexed_doc = indexer.index_document(content_bytes, filename)
        return BaseResponse(
            success=True, message=f"Document '{filename}' indexed successfully", data=indexed_doc
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document indexing failed: {e!s}",
        ) from e


@router.post(
    "/rag/index/text",
    response_model=BaseResponse[Document],
    status_code=status.HTTP_201_CREATED,
    summary="Index Document (Plain Text)",
    description="Allows sending plain text content directly as a JSON payload to index.",
)
async def index_text(
    payload: IndexTextRequest, indexer: DocumentIndexer = Depends(get_document_indexer)
):
    try:
        content_bytes = payload.content.encode("utf-8")
        indexed_doc = indexer.index_document(content_bytes, payload.filename)
        return BaseResponse(
            success=True,
            message=f"Document '{payload.filename}' indexed successfully",
            data=indexed_doc,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document indexing failed: {e!s}",
        ) from e


@router.get(
    "/rag/documents",
    response_model=BaseResponse[list[Document]],
    status_code=status.HTTP_200_OK,
    summary="List Indexed Documents",
    description="Returns a list of all currently indexed files and metadata.",
)
async def list_documents(indexer: DocumentIndexer = Depends(get_document_indexer)):
    docs = indexer.list_indexed_documents()
    return BaseResponse(success=True, message="Documents list retrieved", data=docs)


@router.delete(
    "/rag/documents/{document_id}",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Delete Indexed Document",
    description="Deletes a document and all its corresponding chunks from the index database.",
)
async def delete_document(
    document_id: str, indexer: DocumentIndexer = Depends(get_document_indexer)
):
    success = indexer.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found.",
        )
    return BaseResponse(
        success=True, message=f"Document {document_id} deleted successfully", data={}
    )
