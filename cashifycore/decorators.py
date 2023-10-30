import asyncio
import json
import threading
from functools import wraps

from cashifycore import CashifyClient
from cashifycore.exception import CashifyApiException


def roles_allowed(permission_list: list[str]):
    def inner_roles_allowed(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            allowed_permissions = kwargs.get('request').scope.get('permissions') if kwargs.get('request').scope else None
            if allowed_permissions and any(item in allowed_permissions for item in permission_list):
                return func(*args, **kwargs)
            raise CashifyApiException(error=('0001', 'User dont have permissions'), diagno_code=('PCORE01', 'User dont have permissions'))

        return wrapper

    return inner_roles_allowed


def crud_filter(filters: dict):
    def inner_crud_filter(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs.get('request').scope['crud_filter'] = filters
            return func(*args, **kwargs)

        return wrapper

    return inner_crud_filter


def crud_sort(sort: dict):
    def inner_crud_sort(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs.get('request').scope['crud_sort'] = sort
            return func(*args, **kwargs)

        return wrapper

    return inner_crud_sort


def scheduler_task(func):
    """
    Use this task for jobs which are called using scheduler service
    :param func:
    :return: This will hit to scheduler at end i.e. after executing the task
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_response = None
        try:
            api_response = {"status": "SUCCESS", "msg": "success"}
            thread = threading.Thread(name=func.__name__,
                                      target=func,
                                      args=(*args,),
                                      kwargs=kwargs
                                      )
            thread.start()
        except Exception as e:
            api_response = {"status": "FAILURE", "msg": "failure"}
            print(e)
        finally:
            request_body = json.loads(asyncio.run(args[0].body()))
            url = request_body.get('cbu').split("cashify.in")
            client = CashifyClient(base_url=url[0] + 'cashify.in')
            print(client.get_response(args[0], 'POST', url[1][1:], json_data=api_response, headers={
                'Content-Type': 'application/json'
            }))
    return wrapper


# def background_task(func):
#     """
#     Use this decorator to make task run in the background
#     :param func:
#     :return: Nothing it will just execute and exit
#     """
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         try:
#             thread = threading.Thread(name=func.__name__,
#                                       target=func,
#                                       args=(*args,),
#                                       kwargs=kwargs
#                                       )
#             thread.start()
#         except Exception as e:
#             print(e)
#     return wrapper
