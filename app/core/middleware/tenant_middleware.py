from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.modules.auth.utils import decode_token


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):

        request.state.tenant_id = None
        request.state.user_id = None
        request.state.role = None

        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_token(token)

            if payload:
                request.state.user_id = payload.get("sub")
                request.state.tenant_id = payload.get("tenant_id")
                request.state.role = payload.get("role")

        response = await call_next(request)

        return response