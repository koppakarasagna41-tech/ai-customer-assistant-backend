from fastapi.testclient import TestClient


def test_rag_index_text_success(base_client: TestClient):
    payload = {
        "content": (
            "Enterprise AI platform provides end-to-end RAG support and "
            "intelligent analysis."
        ),
        "filename": "ai_platform_guide.txt",
    }

    response = base_client.post(
        "/api/v1/rag/index/text",
        json=payload,
    )

    print("Status Code:", response.status_code)
    print("Response:", response.text)

    assert response.status_code == 201

    res_data = response.json()

    assert res_data["success"] is True
    assert "document_id" in res_data["data"]
    assert "title" in res_data["data"]


def test_rag_index_file_multipart_success(base_client: TestClient):
    file_content = b"This is some text in a mock upload file for testing multiparts."

    file_payload = {
        "file": (
            "test_upload_doc.txt",
            file_content,
            "text/plain",
        )
    }

    response = base_client.post(
        "/api/v1/rag/index",
        files=file_payload,
    )

    print("Status Code:", response.status_code)
    print("Response:", response.text)

    assert response.status_code == 201

    res_data = response.json()

    assert res_data["success"] is True
    assert "document_id" in res_data["data"]
    assert "title" in res_data["data"]


def test_rag_list_documents(base_client: TestClient):
    base_client.post(
        "/api/v1/rag/index/text",
        json={
            "content": "Sample document listing test.",
            "filename": "list_test.txt",
        },
    )

    response = base_client.get("/api/v1/rag/documents")

    print("Status Code:", response.status_code)
    print("Response:", response.text)

    assert response.status_code == 200

    res_data = response.json()

    assert res_data["success"] is True
    assert len(res_data["data"]) > 0

    assert any("title" in doc for doc in res_data["data"])


def test_rag_search_endpoint(base_client: TestClient):
    base_client.post(
        "/api/v1/rag/index/text",
        json={
            "content": (
                "Vulnerability scanning is a core process in AI Security and "
                "continuous compliance."
            ),
            "filename": "security_vulnerability.txt",
        },
    )

    payload = {
        "query": "vulnerability scanning",
        "top_k": 2,
    }

    response = base_client.post(
        "/api/v1/rag/search",
        json=payload,
    )

    assert response.status_code == 200

    res_data = response.json()

    assert res_data["success"] is True
    assert res_data["data"]["query"] == "vulnerability scanning"
    assert "results" in res_data["data"]


def test_rag_query_endpoint(base_client: TestClient):
    payload = {
        "query": "What is security vulnerability scan?",
        "top_k": 3,
        "compress": True,
    }

    response = base_client.post(
        "/api/v1/rag/query",
        json=payload,
    )

    assert response.status_code == 200

    res_data = response.json()

    assert res_data["success"] is True
    assert "answer" in res_data["data"]
    assert isinstance(res_data["data"]["answer"], str)


def test_rag_delete_document_success(base_client: TestClient):
    response = base_client.post(
        "/api/v1/rag/index/text",
        json={
            "content": "To be deleted soon.",
            "filename": "delete_test.txt",
        },
    )

    assert response.status_code == 201

    doc_id = response.json()["data"]["document_id"]

    delete_response = base_client.delete(
        f"/api/v1/rag/documents/{doc_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["success"] is True


def test_rag_delete_document_not_found(base_client: TestClient):
    response = base_client.delete(
        "/api/v1/rag/documents/DOC-NONEXISTENT"
    )

    assert response.status_code == 404

    res_data = response.json()
    assert "detail" in res_data