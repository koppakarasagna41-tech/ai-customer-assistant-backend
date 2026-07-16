import json
import unicodedata
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

class RequestValidatorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body_str = body_bytes.decode("utf-8")
                    normalized = unicodedata.normalize("NFKC", body_str)
                    cleaned = "".join(ch for ch in normalized if unicodedata.category(ch)[0] != "C" or ch in "\t\n\r")
                    
                    cleaned_bytes = cleaned.encode("utf-8")
                    async def receive():
                        return {"type": "http.request", "body": cleaned_bytes, "more_body": False}
                    request._receive = receive
            except Exception:
                pass
                
        return await call_next(request)
