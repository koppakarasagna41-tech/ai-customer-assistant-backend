from fastapi import APIRouter
from app.api.v1 import (
    health,
    auth,
    chat,
    tickets,
    sentiment,
    intent,
    rag,
    analytics,
    reports,
    analysis,
    security
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(chat.router, tags=["Chat"])
api_router.include_router(tickets.router, tags=["Tickets"])
api_router.include_router(sentiment.router, tags=["Sentiment"])
api_router.include_router(intent.router, tags=["Intent"])
api_router.include_router(rag.router, tags=["RAG"])
api_router.include_router(analytics.router, tags=["Analytics"])
api_router.include_router(reports.router, tags=["Reports"])
api_router.include_router(analysis.router, tags=["Analysis"])
api_router.include_router(security.router, tags=["Security"])
