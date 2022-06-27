"""DB Connection Pool for SAP HANA via hdbcli
Usage:
credentials = Credentials(host, port, user, password)
db_con_pool_ddl = ConnectionPool(credentials)
with DBConnection(db_con_pool_ddl) as db:
    db.cur.execute('select * from dummy')
"""
from hdbcli import dbapi

class Credentials():
    def __init__(self, host:str, port:int, user:str, password:str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

class SharedConnection():
    """Represents the actual connection to the DB"""
    def __init__(self, credentials: Credentials):
        self.con = dbapi.connect(
            address = credentials.host,
            port = credentials.port,
            user = credentials.user,
            password = credentials.password,
            autocommit = False
        )
        self.cur = self.con.cursor()
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        self.cur.close()
        self.con.close()

class ConnectionPool():
    """Connection Pool"""
    def __init__(self, credentials, min_connections: int = 1) -> None:
        self.credentials = credentials
        self.min_connections = min_connections
        self.idle_connections = []
        for _ in range(min_connections):
            self.idle_connections.append(SharedConnection(self.credentials))
        self.num_used_connections = min_connections
    def get_connection(self):
        if len(self.idle_connections) == 0:
            return SharedConnection(self.credentials)
        else:
            self.num_used_connections += 1
            return self.idle_connections.pop()
    def return_connection(self, connection: SharedConnection):
        self.idle_connections.append(connection)
        self.num_used_connections -= 1

class DBConnection():
    """DB connection reference"""
    def __init__(self, pool: ConnectionPool):
        self.pool = pool
    def __enter__(self):
        self.connection = self.pool.get_connection()
        return self.connection
    def __exit__(self, exception_type, exception_value, traceback):
        self.pool.return_connection(self.connection)

