import json

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.security_service import get_security_service


class AISecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if request.method in ["POST", "PUT"] and any(
            p in path for p in ["/chat", "/rag", "/message", "/tickets"]
        ):
            try:
                body_bytes = await request.body()

                async def receive():
                    return {"type": "http.request", "body": body_bytes, "more_body": False}

                request._receive = receive

                body_str = body_bytes.decode("utf-8")
                if body_str:
                    payload = json.loads(body_str)
                    prompt = ""
                    if isinstance(payload, dict):
                        prompt = (
                            payload.get("prompt")
                            or payload.get("message")
                            or payload.get("content")
                            or ""
                        )

                    if prompt and isinstance(prompt, str):
                        security_service = get_security_service()
                        eval_res = security_service.inspect_incoming_prompt(
                            prompt,
                            user_id=payload.get("user_id"),
                            ip=request.client.host if request.client else "127.0.0.1",
                        )
                        if not eval_res.is_safe and eval_res.severity in ["HIGH", "CRITICAL"]:
                            threat_type = (
                                eval_res.jailbreak_analysis.threat_type
                                or eval_res.injection_analysis.threat_type
                            )
                            return Response(
                                content=json.dumps(
                                    {
                                        "success": False,
                                        "message": (
                                            "AI Security Violation: Dangerous prompt detected "
                                            f"[{eval_res.severity} Risk: {threat_type}]. "
                                            "Request terminated."
                                        ),
                                        "data": None,
                                    }
                                ),
                                status_code=status.HTTP_400_BAD_REQUEST,
                                media_type="application/json",
                            )
            except Exception:
                pass

        return await call_next(request)
