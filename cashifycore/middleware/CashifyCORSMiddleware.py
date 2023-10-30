from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.middleware.cors import CORSMiddleware


class CashifyCORSMiddleware:
    def __init__(
            self,
            app: ASGIApp
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await CORSMiddleware(
            self.app,
            allow_origins=['*'],
            allow_headers=[
                'origin', 'content-type', 'accept', 'x-authorization', 'authorization', 'x-user-auth',
                'x-app-installer', 'x-at-auth-user', 'x-user-agent', 'x-app-version', 'x-app-os', 'x-enterprise-auth',
                'x-jira-auth', 'x-session-id', 'x-console-auth', 'x-app-lang', 'x-sso-token'],
            allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD'],
            allow_credentials=True,
            allow_origin_regex='(https|http):\/\/.*\.cashify\.in'
        ).__call__(scope, receive, send)
        return
