from cashifyetcd import CashifyETCD as CoreETCD
from app.config import settings


class SingleTonETCD(object):
    _instance = None
    _etcd = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingleTonETCD, cls).__new__(cls)
            cls._etcd = CoreETCD(
                host=settings.etcd_host, protocol=settings.etcd_protocol, port=settings.etcd_port,
                service_version=settings.app_version, service_name=settings.app_name
            )
        return cls._etcd


class CashifyETCD:

    @staticmethod
    def etcd_get_value_cached(key):
        etcd = SingleTonETCD()
        return etcd.get_property_value(key)

    @staticmethod
    def etcd_get_value_uncached(key):
        etcd = SingleTonETCD()
        return etcd.get_value(key)
