import os
import sys
import json
from pathlib import Path
sys.path.insert(0, os.path.abspath('.'))
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['GEMINI_API_KEY'] = 'mock-gemini-api-key-for-testing'
os.environ['JWT_SECRET'] = 'mock-jwt-secret-key'
os.environ['JWT_ALGORITHM'] = 'HS256'
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.v1.router import api_router
from app.services.vector_store import VectorStoreFactory
from app.services.gemini_client import GeminiClient
import app.database.create_tables
VectorStoreFactory.set_provider('in_memory')

async def mock_generate_content(self, contents, system_instruction=None, response_schema=None, temperature=0.2, max_output_tokens=1500, response_mime_type='text/plain'):
    mock_response = {
        'response': 'Thank you for contacting customer support. We are looking into your query.',
        'intent': 'SUPPORT_QUERY',
        'predicted_category': 'technical',
        'confidence_score': 0.98,
        'priority': 'high',
        'sentiment': 'neutral',
        'urgency': 'medium',
        'escalated': False,
        'reasoning': 'Mock AI response',
    }
    if response_mime_type == 'application/json':
        text_content = json.dumps(mock_response)
    else:
        text_content = 'This is a mock text response from Gemini.'
    return {
        'candidates': [
            {'content': {'parts': [{'text': text_content}]}, 'finishReason': 'STOP'}
        ]
}

setattr(GeminiClient, 'generate_content', mock_generate_content)

app = FastAPI()
app.include_router(api_router, prefix='/api/v1')
client = TestClient(app)
payload = {
    'title': 'SSO integration fail',
    'description': 'We are getting a login timeout from Okta.',
    'category': 'technical',
    'priority': 'urgent',
}
resp = client.post('/api/v1/tickets/create', json=payload)
print(resp.status_code)
print(resp.text)
