import io
import pytest
from fastapi.testclient import TestClient

def test_rag_index_text_success(base_client: TestClient):
    payload = {
        "content": "Enterprise AI platform provides end-to-end RAG support and intelligent analysis.",
        "filename": "ai_platform_guide.txt"
    }
    response = base_client.post("/api/v1/rag/index/text", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert "document_id" in res_data["data"]
    assert res_data["data"]["title"] == "ai_platform_guide.txt"

def test_rag_index_file_multipart_success(base_client: TestClient):
    file_content = b"This is some text in a mock upload file for testing multiparts."
    file_payload = {"file": ("test_upload_doc.txt", file_content, "text/plain")}
    response = base_client.post("/api/v1/rag/index", files=file_payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["title"] == "test_upload_doc.txt"

def test_rag_list_documents(base_client: TestClient):
    # Ensure there's at least one document
    base_client.post("/api/v1/rag/index/text", json={
        "content": "Sample document listing test.",
        "filename": "list_test.txt"
    })
    
    response = base_client.get("/api/v1/rag/documents")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert len(res_data["data"]) > 0
    assert any(doc["title"] == "list_test.txt" for doc in res_data["data"])

def test_rag_search_endpoint(base_client: TestClient):
    # Index some content first
    base_client.post("/api/v1/rag/index/text", json={
        "content": "Vulnerability scanning is a core process in AI Security and continuous compliance.",
        "filename": "security_vulnerability.txt"
    })

    payload = {
        "query": "vulnerability scanning",
        "top_k": 2
    }
    response = base_client.post("/api/v1/rag/search", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["query"] == "vulnerability scanning"
    assert "results" in data

def test_rag_query_endpoint(base_client: TestClient):
    # Full query pipeline
    payload = {
        "query": "What is security vulnerability scan?",
        "top_k": 3,
        "compress": True
    }
    response = base_client.post("/api/v1/rag/query", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert "response" in res_data["data"]

def test_rag_delete_document_success(base_client: TestClient):
    # Index one
    idx_res = base_client.post("/api/v1/rag/index/text", json={
        "content": "To be deleted soon.",
        "filename": "delete_test.txt"
    })
    doc_id = idx_res.json()["data"]["document_id"]

    # Delete it
    del_res = base_client.delete(f"/api/v1/rag/documents/{doc_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

def test_rag_delete_document_not_found(base_client: TestClient):
    response = base_client.delete("/api/v1/rag/documents/DOC-NONEXISTENT")
    assert response.status_code == 404
