from app.config import settings
from cashifylogger import CashifyLogger as CoreLogger
from cashifylogger import CashifyFluentLogger as CoreFluentLogger


class SingleTonLogger:
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingleTonLogger, cls).__new__(cls)
            cls._logger = CoreLogger(
                etcd_host=settings.etcd_host, etcd_protocol=settings.etcd_protocol, etcd_port=settings.etcd_port,
                service_version=settings.app_version, service_name=settings.app_name
            )
        return cls._logger


class CashifyLogger:

    @staticmethod
    def debug(msg):
        log = SingleTonLogger()
        log.debug(msg)

    @staticmethod
    def info(msg):
        log = SingleTonLogger()
        log.info(msg)

    @staticmethod
    def warning(msg):
        log = SingleTonLogger()
        log.warning(msg)

    @staticmethod
    def error(msg):
        log = SingleTonLogger()
        log.error(msg)

    @staticmethod
    def critical(msg):
        log = SingleTonLogger()
        log.critical(msg)


class SingleTonFluentLogger:
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingleTonFluentLogger, cls).__new__(cls)
            cls._logger = CoreFluentLogger(
                etcd_host=settings.etcd_host, etcd_protocol=settings.etcd_protocol, etcd_port=settings.etcd_port,
                service_version=settings.app_version, service_name=settings.app_name
            )
        return cls._logger


class CashifyFluentLogger:

    @staticmethod
    def log(msg):
        try:
            logger = SingleTonFluentLogger()
            msg['elastic_index'] = settings.app_name + '_' + settings.app_version
            logger.log(msg)
        except Exception as e:
            print(e)
