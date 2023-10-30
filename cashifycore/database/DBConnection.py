from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from app.config.etcd import ETCD


class MySQLConnection:
    _instance = None
    _db_connection = None
    _db_connection_read = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MySQLConnection, cls).__new__(cls)
            db_url = URL.create(
                drivername="mysql+mysqlconnector",
                username=ETCD.get_value('db.mysql.user'),
                password=ETCD.get_value('db.mysql.password'),
                host=ETCD.get_value('db.mysql.host'),
                database=ETCD.get_value('db.mysql.name')
            )

            # Fallback added if not able to connect with Read DB
            connect_args = {
                'failover': [{
                    'user': ETCD.get_value('db.mysql.user'),
                    'password': ETCD.get_value('db.mysql.password'),
                    'host': ETCD.get_value('db.mysql.host'),
                    'database': ETCD.get_value('db.mysql.name')
                }]
            }
            db_url_read = URL.create(
                drivername="mysql+mysqlconnector",
                username=ETCD.get_value('db.mysql.user'),
                password=ETCD.get_value('db.mysql.password'),
                host=ETCD.get_value('db.read.mysql.host'),
                database=ETCD.get_value('db.mysql.name')
            )
            db_engine = create_engine(db_url, pool_pre_ping=True, poolclass=NullPool)
            db_engine_read = create_engine(db_url_read, pool_pre_ping=True, connect_args=connect_args, poolclass=NullPool)
            cls._db_connection = sessionmaker(autocommit=True, autoflush=True, bind=db_engine)
            cls._db_connection_read = sessionmaker(autocommit=True, autoflush=True, bind=db_engine_read)
        return cls._db_connection, cls._db_connection_read

    @staticmethod
    def get_database_session():
        db = MySQLConnection()[0]()
        try:
            return db
        except Exception as e:
            print(e)
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def get_database_read_session():
        db = MySQLConnection()[1]()
        try:
            return db
        except Exception as e:
            print(e)
            db.rollback()
        finally:
            db.close()


class MySQLConnectionV2:
    _instance = None
    _db_connection = None
    _db_connection_read = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MySQLConnectionV2, cls).__new__(cls)
            db_url = URL.create(
                drivername="mysql+mysqlconnector",
                username=ETCD.get_value('db.mysql.user'),
                password=ETCD.get_value('db.mysql.password'),
                host=ETCD.get_value('db.mysql.host'),
                database=ETCD.get_value('db.mysql.name')
            )

            # Fallback added if not able to connect with Read DB
            connect_args = {
                'failover': [{
                    'user': ETCD.get_value('db.mysql.user'),
                    'password': ETCD.get_value('db.mysql.password'),
                    'host': ETCD.get_value('db.mysql.host'),
                    'database': ETCD.get_value('db.mysql.name')
                }]
            }
            db_url_read = URL.create(
                drivername="mysql+mysqlconnector",
                username=ETCD.get_value('db.mysql.user'),
                password=ETCD.get_value('db.mysql.password'),
                host=ETCD.get_value('db.read.mysql.host'),
                database=ETCD.get_value('db.mysql.name')
            )
            cls._db_connection = create_engine(db_url, pool_pre_ping=True)
            cls._db_connection_read = create_engine(db_url_read, pool_pre_ping=True, connect_args=connect_args)
            # cls._db_connection = sessionmaker(autocommit=True, autoflush=True, bind=db_engine)
            # cls._db_connection_read = sessionmaker(autocommit=True, autoflush=True, bind=db_engine_read)
        # return cls._db_connection, cls._db_connection_read

    @classmethod
    def get_session_read_local(cls):
        if not cls._db_connection_read:
            MySQLConnectionV2()
        return sessionmaker(autocommit=True, autoflush=True, bind=cls._db_connection_read)

    @classmethod
    def get_session_local(cls):
        if not cls._db_connection:
            MySQLConnectionV2()
        return sessionmaker(autocommit=True, autoflush=True, bind=cls._db_connection)

    @staticmethod
    def get_database_session():
        try:
            db = MySQLConnectionV2.get_session_local()()
            return db
        except Exception as e:
            print(e)
            db.rollback()

    @staticmethod
    def get_database_read_session():
        try:
            db = MySQLConnectionV2.get_session_read_local()()
            return db
        except Exception as e:
            print(e)
            db.rollback()

    @staticmethod
    def close_session(session):
        session.close()


class PostgresConnection:
    _instance = None
    _db_connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresConnection, cls).__new__(cls)

            host_server = ETCD.get_value('db.postgres.host')
            db_server_port = '5432'
            database_name = ETCD.get_value('db.postgres.name')
            db_username = ETCD.get_value('db.postgres.user')
            db_password = ETCD.get_value('db.postgres.password')
            ssl_mode = 'prefer'
            db_url = 'postgresql+psycopg2://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server,
                                                                              db_server_port, database_name, ssl_mode)

            cls._db_connection = create_engine(db_url, pool_pre_ping=True, pool_size=20)
            # cls._db_connection = sessionmaker(autocommit=True, autoflush=True, bind=db_engine)
        # return cls._db_connection

    @classmethod
    def get_session_local(cls):
        if not cls._db_connection:
            PostgresConnection()
        return sessionmaker(autocommit=True, autoflush=True, bind=cls._db_connection)

    @staticmethod
    def get_database_session():
        try:
            db = PostgresConnection.get_session_local()()
            return db
        except Exception as e:
            print(e)
            db.rollback()

    @staticmethod
    def close_session(session):
        session.close()
