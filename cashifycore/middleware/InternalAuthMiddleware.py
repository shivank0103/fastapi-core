from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.etcd import ETCD


AUTHORIZATION_HEADER = 'Authorization-I'


class InternalAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        if request.url.path.startswith('/internal'):
            header_value = request.headers.get(AUTHORIZATION_HEADER)
            if not header_value:
                return JSONResponse({"message": "Please add internal token"}, status_code=409)
            if header_value != ETCD.get_value('cas.internal.api.auth.secret'):
                return JSONResponse({"message": "Please provide correct internal token"}, status_code=409)
        response = await call_next(request)
        return response
