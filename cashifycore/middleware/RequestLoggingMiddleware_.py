from starlette.requests import Request


# Steps to Apply
# my_middleware = RequestLoggingMiddleware()
# app.add_middleware(BaseHTTPMiddleware, dispatch=my_middleware)

async def set_body(request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body}

    request._receive = receive


async def get_body(request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body


class RequestLoggingMiddleware:
    def __init__(
            self
    ) -> None:
        pass

    async def __call__(self, request: Request, call_next):
        await set_body(request, await request.body())

        print(await get_body(request))

        response = await call_next(request)
        return response
