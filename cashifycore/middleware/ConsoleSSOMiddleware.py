from typing import Any
from fastapi import status
from starlette.datastructures import URL, Headers
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send
from app.config import settings
from cashifycore.rest_client import CashifyClient
from cashifycore.cache import CashifyCache


SSO_TOKEN_KEY = 'x-sso-token'


class ConsoleSSOMiddleware:
    def __init__(
            self,
            app: ASGIApp,
            exclude_url_prefix: list[str] = None,
    ) -> None:
        self.app = app
        self.exclude_url_prefix = exclude_url_prefix + [
            '/docs', '/openapi.json', '/v1/health', '/health', '/favicon.ico', '/redoc', '/v1/bg', '/v1/ns'
        ]

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        url = URL(scope=scope)
        headers = Headers(scope=scope)
        token = headers.get(SSO_TOKEN_KEY)
        request = Request(scope, receive)
        for path in self.exclude_url_prefix:
            if url.path.startswith(path):
                await self.app(scope, receive, send)
                return
        if not token:
            response = JSONResponse({"message": "Please add SSO Token"}, status_code=409)
            await response(scope, receive, send)
            return
        headers = Headers(scope=scope)
        response = self.get_permissions(headers.get(SSO_TOKEN_KEY), request)
        if response[2] != status.HTTP_200_OK:
            response = JSONResponse(response[0], status_code=409)
            await response(scope, receive, send)
            return

        permissions = response[0].get('loginResponseVo').get('mp', [])
        scope['user'] = response[0].get('loginResponseVo')
        if permissions:
            scope['permissions'] = permissions[0].get('permissionList') if permissions[0].get('permissionList') else []
        await self.app(scope, receive, send)
        return

    @CashifyCache('LOCAL').cache().cache('console_middleware', 120, ['token'])
    def get_permissions(self, token: str, request) -> Any:
        data = {
            'grant_type': 'console',
            'jwt': token,
            'sern': settings.app_name,
            'serv': settings.app_version
        }
        cas_client = CashifyClient(service_name='cas')
        response = cas_client.get_response(request=request, request_method='POST', endpoint='v1/auth/otp/token',
                                           params={}, post_data=data, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        return response
