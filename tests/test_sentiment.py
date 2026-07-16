import pytest
from fastapi.testclient import TestClient

def test_sentiment_analysis(base_client: TestClient):
    payload = {
        "text": "I am extremely angry about this duplicate charge on my account!"
    }
    response = base_client.post("/api/v1/sentiment", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["message"] == "Sentiment analysis complete"
    
    data = res_data["data"]
    assert "sentiment" in data
    assert "label" in data["sentiment"]
    assert "score" in data["sentiment"]
    assert "escalation_recommended" in data
