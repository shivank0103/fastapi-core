from starlette.middleware.base import BaseHTTPMiddleware
from app.config.logger import CashifyLogger


async def set_body(request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body}

    request._receive = receive


async def get_body(request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        await set_body(request, await request.body())

        CashifyLogger.debug(f'Request URL : {request.method} {request.url}')
        CashifyLogger.debug(f'Request Headers : {request.headers}')
        CashifyLogger.debug(f'Request Body : {await get_body(request)}')

        response = await call_next(request)
        return response
