import json
from uuid import uuid4
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.config.logger import CashifyLogger


REQUEST_HEADER_ID = 'x-request-id'
REQUEST_HEADER_SERVICE_NAME = 'X-Service'


class CashifyCommonMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        previous_uuid = request.headers.get(REQUEST_HEADER_ID)
        if previous_uuid:
            request.scope['r_id'] = previous_uuid
        else:
            request.scope['r_id'] = str(uuid4())
        response = await call_next(request)
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        CashifyLogger.debug(f'Response Retuned : {body}')
        if response.headers.get('Content-Type') == 'text/html; charset=utf-8':
            return Response(content=body, status_code=response.status_code,
                            headers=dict(response.headers), media_type=response.media_type)
        if response.headers.get('Content-Type') == 'application/json':
            response_json = json.loads(body)
            if response_json is not None:
                response_json['r_id'] = request.scope.get('r_id')
                if request.query_params.get('scm'):
                    crud_filters = request.scope.get('crud_filter')
                    crud_sort = request.scope.get('crud_sort')
                    if crud_filters:
                        response_json['allowedFilters'] = crud_filters
                    if crud_sort:
                        response_json['allowedSorts'] = crud_sort
            response_string = json.dumps(response_json).encode('utf-8')
            custom_headers = dict(response.headers)
            custom_headers['content-length'] = str(len(response_string))
            custom_headers[REQUEST_HEADER_SERVICE_NAME] = settings.app_name
            return Response(content=response_string, status_code=response.status_code,
                            headers=dict(custom_headers), media_type=response.media_type)
        return response
