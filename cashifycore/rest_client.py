import time
from app.config import settings
from restclient.client import RestClient
from cashifycore.logger import CashifyFluentLogger
from fastapi import Request

REQUEST_HEADER_ID = 'x-request-id'


class CashifyClient:
    rest_client = None
    debug_enabled = False
    monitoring_enable = False
    base_url = None

    def __init__(
            self, service_name: str = None, base_url: str = None, is_internal: bool = False,
            enable_debug: bool = False, enable_monitoring: bool = False
    ):
        self.debug_enabled = enable_debug
        self.monitoring_enable = enable_monitoring
        self.base_url = base_url
        self.service_name = service_name
        if service_name and base_url:
            raise Exception("Either one should be provided")
        if service_name:
            self.rest_client = RestClient(
                app_name=settings.app_name, service_name=service_name, app_version=settings.app_version,
                etcd_host=settings.etcd_host, etcd_protocol=settings.etcd_protocol, etcd_port=settings.etcd_port,
                is_internal=is_internal
            )
        else:
            self.rest_client = RestClient(
                base_url=base_url, app_name=settings.app_name, app_version=settings.app_version,
                etcd_host=settings.etcd_host, etcd_protocol=settings.etcd_protocol, etcd_port=settings.etcd_port,
            )

    def get_response(
            self, request: Request, request_method: str, endpoint: str,
            headers: dict = None, post_data: dict = None, json_data: dict = None, params: dict = None
    ):
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        if request:
            headers[REQUEST_HEADER_ID] = request.scope.get('r_id')

        time_started = int(round(time.time() * 1000))
        response = self.rest_client.response(
            request_method=request_method, endpoint=endpoint, headers=headers, post_data=post_data, json_data=json_data, params=params
        )
        if self.monitoring_enable or self.base_url:
            log_dict = {
                'requestId': request.scope.get('r_id'),
                'url': request.url.path,
                'request_method': request.method,
                'headers': dict(request.headers),
                'query_params': dict(request.query_params),
                'path_params': dict(request.path_params),
                'elastic_type': 'request',
                'request': {
                    'base_url': self.base_url,
                    'service_name': self.service_name,
                    'endpoint': endpoint,
                    'request_method': request_method,
                    'data': post_data,
                    'params': params,
                    'headers': headers
                },
                'response': {
                    'data': response[0],
                    'headers': dict(response[1]),
                    'status_code': response[2]
                },
                'time_taken_in_milliseconds': int(round(time.time() * 1000)) - time_started,
                'current_time': int(round(time.time() * 1000)),
                'host': request.client.host
            }
            CashifyFluentLogger.log(log_dict)
        return response
