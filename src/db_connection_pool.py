"""DB Connection Pool for SAP HANA via hdbcli
Usage:
credentials = Credentials(host, port, user, password)
db_con_pool_ddl = ConnectionPool(credentials)
with DBConnection(db_con_pool_ddl) as db:
    db.cur.execute('select * from dummy')
"""
from asyncio import gather, get_event_loop
from functools import partial
from typing import List, Tuple
import time
from hdbcli import dbapi

class Credentials():
    def __init__(self, host:str, port:int, user:str, password:str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password


async def execute_async(self, operation):
    loop = get_event_loop()
    return await loop.run_in_executor(None, partial(self.execute, operation))
dbapi.Cursor.execute_async = execute_async

async def executemany_async(self, operation):
    loop = get_event_loop()
    return await loop.run_in_executor(None, partial(self.executemany, operation[0], operation[1]))
dbapi.Cursor.executemany_async = executemany_async

async def commit_async(self):
    loop = get_event_loop()
    return await loop.run_in_executor(None, self.commit)
dbapi.Connection.commit_async = commit_async

async def rollback_async(self):
    loop = get_event_loop()
    return await loop.run_in_executor(None, self.rollback)
dbapi.Connection.rollback_async = rollback_async

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

    def refresh_cursor(self):
        self.cur.close()
        self.cur = self.con.cursor()

class ConnectionPool():
    """Connection Pool"""
    def __init__(self, credentials, min_connections: int = 1) -> None:
        self.credentials = credentials
        self.min_connections = min_connections
        self.idle_connections = []
        for _ in range(min_connections):
            self.idle_connections.append(SharedConnection(self.credentials))
        self.num_used_connections = 0
    def get_connection(self):
        self.num_used_connections += 1
        if len(self.idle_connections) == 0:
            return SharedConnection(self.credentials)
        else:
            return self.idle_connections.pop()
    def return_connection(self, connection: SharedConnection):
        connection.refresh_cursor()
        self.idle_connections.append(connection)
        self.num_used_connections -= 1

class DBConnection():
    """DB connection reference"""
    def __init__(self, pool:ConnectionPool):
        self.pool = pool
    def __enter__(self):
        self.connection = self.pool.get_connection()
        return self.connection
    def __exit__(self, exception_type, exception_value, traceback):
        self.pool.return_connection(self.connection)


class DBBulkProcessing():
    """Asynchronous bulk processing of DB statements"""
    def __init__(self, connection_pool: ConnectionPool, block_size: int) -> None:
        self.connection_pool = connection_pool
        self.block_size = block_size
        self.connections = [connection_pool.get_connection() for w in range(block_size)]
    def __enter__(self):
        return self
    @staticmethod
    def blockify(operations, block_size: int):
        start = 0
        while True:
            yield operations[start:start + block_size]
            start += block_size
            if start >= len(operations):
                return
    async def execute(self, operations:List[str]):
        if self.block_size == 1:
            for operation in operations:
                self.connections[0].cur.execute(operation)
        else:
            for block in DBBulkProcessing.blockify(operations, self.block_size):
                await gather(*[self.connections[i].cur.execute_async(sql) for i, sql in enumerate(block)])
    async def executemany(self, operations:List[Tuple[str, dict]]):
        if self.block_size == 1:
            for operation in operations:
                self.connections[0].cur.executemany(operation[0], operation[1])
        else:
            for block in DBBulkProcessing.blockify(operations, self.block_size):
                await gather(*[self.connections[i].cur.executemany_async(operation) for i, operation in enumerate(block)])
    async def commit(self):
        if self.block_size == 1:
            self.connections[0].con.commit()
        else:
            await gather(*[c.con.commit_async() for c in self.connections])
    async def rollback(self):
        if self.block_size == 1:
            self.connections[0].con.commit()
        else:
            await gather(*[c.con.rollback_async() for c in self.connections])
    def __exit__(self, exception_type, exception_value, traceback):
        for db in self.connections:
            self.connection_pool.return_connection(db)