import json

from datetime import datetime
from urllib.parse import unquote

from sqlalchemy import and_, or_, not_, desc, asc
from cashifycore.database.DBConnection import MySQLConnection
from cashifycore.exception import CashifyApiException


class CashifyCrudService:

    LEFT_JOIN = 'LEFT'
    FULL_JOIN = 'FULL'

    def __init__(self, request, model_name, foreign_tables):
        self.request = request
        self.model_name = model_name
        self.foreign_tables = foreign_tables
        self.db_connection = MySQLConnection.get_database_session()
        self.query = self.db_connection.query(model_name)

    def get_response(self, filters=None, sort=None):
        if sort is None:
            sort = []
        if filters is None:
            filters = []
        pagination_params = '{"pageSize": 10,"page": 0}'
        filter_params = filters
        sort_params = sort

        data = self.query
        for fk in self.foreign_tables:
            try:
                if fk[2] == 'LEFT':
                    data = data.join(fk, isouter=True)
                else:
                    data = data.join(fk, full=True)
            except IndexError:
                data = data.join(fk)
            except TypeError:
                data = data.join(fk)

        filter_params_url = unquote(self.request.query_params.get('filter')) \
            if self.request.query_params and self.request.query_params.get('filter') else {}
        if filter_params_url:
            filter_params_url = json.loads(filter_params_url)
            filter_params.extend(filter_params_url)

        for filter_param in filter_params:
            table_search = self.model_name
            column_name = filter_param.get('field')
            if '.' in filter_param.get('field'):
                fields = filter_param.get('field').split('.')
                table_name = fields[0]
                column_name = fields[1]
                for idx, fk_table_name in enumerate(self.foreign_tables):
                    if type(fk_table_name) == tuple:
                        fk_table = fk_table_name[0].__name__
                    else:
                        fk_table = fk_table_name.__name__
                    if fk_table == table_name:
                        table_search = self.foreign_tables[idx]
                        if type(table_search) == tuple:
                            table_search = table_search[0]
            if filter_param.get('type') == 'EQUALITY':
                # filter_dict = {
                #     column_name: filter_param.get('value').get('search')
                # }
                # data = data.filter_by(**filter_dict)

                # data = data.join(self.model_name.channel).filter(
                #     self.model_name.channel.has(is_active=True)
                # )
                data = data.filter(
                    getattr(table_search, column_name) == filter_param.get('value').get('search')
                )
            if filter_param.get('type') == 'STARTS_WITH':
                data = data.filter(
                    getattr(table_search, column_name).startswith(
                        filter_param.get('value').get('search'))
                )
            if filter_param.get('type') == 'ENDS_WITH':
                data = data.filter(
                    getattr(table_search, column_name).endswith(filter_param.get('value').get('search'))
                )
            if filter_param.get('type') == 'CONTAINS':
                data = data.filter(
                    getattr(table_search, column_name).contains(filter_param.get('value').get('search'))
                )
            if filter_param.get('type') == 'LIKE':
                data = data.filter(
                    getattr(table_search, column_name).like(filter_param.get('value').get('search'))
                )
            if filter_param.get('type') == 'NEGATION':
                data = data.filter(
                    getattr(table_search, column_name) != (filter_param.get('value').get('search'))
                )
            if filter_param.get('type') == 'MULTI_SELECT':
                data = data.filter(
                    getattr(table_search, column_name).in_(filter_param.get('value').get('list'))
                )
            if filter_param.get('type') == 'GREATER_THAN':
                data = data.filter(
                    getattr(table_search, column_name) > filter_param.get('value').get('search')
                )
            if filter_param.get('type') == 'GREATER_THAN_EQUAL':
                data = data.filter(
                    getattr(table_search, column_name) >= filter_param.get('value').get('search')
                )
            if filter_param.get('type') == 'LESS_THAN':
                data = data.filter(
                    getattr(table_search, column_name) < filter_param.get('value').get('search')
                )
            if filter_param.get('type') == 'LESS_THAN_EQUAL':
                data = data.filter(
                    getattr(table_search, column_name) <= filter_param.get('value').get('search')
                )
            if filter_param.get('type') == 'BETWEEN_DATE':
                data = data.filter(
                    getattr(table_search, column_name).between(
                        datetime.fromtimestamp(int(filter_param.get('value').get('start'))/1000),
                        datetime.fromtimestamp(int(filter_param.get('value').get('end'))/1000)
                    )
                )
            if filter_param.get('type') == 'GROUP_BY':
                data = data.group_by(
                    getattr(table_search, column_name)
                )
            if filter_param.get('type') == 'DISTINCT':
                data = data.distinct(
                    getattr(table_search, column_name)
                )
        data_count = data.count()

        sort_params_url = unquote(self.request.query_params.get('sort')) \
            if self.request.query_params and self.request.query_params.get('sort') else {}
        if sort_params_url:
            sort_params_url = json.loads(sort_params_url)
            sort_params.extend(sort_params_url)

        for sort_param in sort_params:
            fk_table = None
            if '.' in sort_param.get('field'):
                fields = sort_param.get('field').split('.')
                table_name = fields[0]
                column_name = fields[1]
            else:
                table_name = self.model_name.__name__
                column_name = sort_param.get('field')
            if table_name == self.model_name.__name__:
                fk_table = self.model_name
            else:
                for idx, fk_table_name in enumerate(self.foreign_tables):
                    if type(fk_table_name) == tuple:
                        fk_table = fk_table_name[0].__name__
                    else:
                        fk_table = fk_table_name.__name__
            if type(fk_table) == str:
                raise CashifyApiException(error=('0002', 'Wrong table provided'),
                                          diagno_code=('PCORE02', 'Wrong table provided'))

            if sort_param.get('type') == 'asc':
                data = data.order_by(asc(getattr(fk_table, column_name)))
            else:
                data = data.order_by(desc(getattr(fk_table, column_name)))

        pagination_params = unquote(self.request.query_params.get('pagination')) \
            if self.request.query_params and self.request.query_params.get('pagination') else pagination_params
        pagination_params = json.loads(pagination_params) if pagination_params else {}
        data = data.limit(
            pagination_params.get('pageSize')
        ).offset(
            (pagination_params.get('page')) * pagination_params.get('pageSize')
        )
        print(data.statement)
        response_dict = {
            'data': data.all(),
            'hasNext': True if data_count - ((pagination_params.get('page'))*pagination_params.get('pageSize')) > pagination_params.get('pageSize') else False,
            'totalCount': data_count,
            'currentPageSize': pagination_params.get('pageSize'),
            'currentPageNumber': pagination_params.get('page')
        }
        return response_dict
