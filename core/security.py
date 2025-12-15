from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow OPTIONS request for CORS (handled by CORSMiddleware)
        if request.method == "OPTIONS":
             return await call_next(request)

        # IP Check
        if settings.ENABLE_IP_CHECK:
            client_host = request.client.host if request.client else None
            if not client_host or (settings.ALLOWED_IPS and client_host not in settings.ALLOWED_IPS):
                logger.warning(f"Access denied for IP: {client_host}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Access denied: IP not allowed"}
                )

        # Token Check
        if settings.ENABLE_TOKEN_CHECK:
            token = request.headers.get("X-Service-Token")
            if not token or token != settings.SECURITY_TOKEN:
                logger.warning("Access denied: Invalid or missing token")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Access denied: Invalid or missing token"}
                )

        response = await call_next(request)
        return response
