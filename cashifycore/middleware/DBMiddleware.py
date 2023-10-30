from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from cashifycore.database.DBConnection import MySQLConnectionV2, PostgresConnection
from app.config.etcd import ETCD


class DBMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        request.scope['db_session'] = MySQLConnectionV2.get_database_session()
        request.scope['db_read_session'] = MySQLConnectionV2.get_database_read_session()
        response = await call_next(request)
        MySQLConnectionV2.close_session(request.scope['db_session'])
        MySQLConnectionV2.close_session(request.scope['db_read_session'])
        return response


class PostgresDBMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.scope['db_session'] = PostgresConnection.get_database_session()
        response = await call_next(request)
        PostgresConnection.close_session(request.scope['db_session'])
        return response
