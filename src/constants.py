'''Helper classes and functions'''
from enum import Enum
from db_connection_pool import Credentials

CURRENT_VERSION = '0.0.1'
SCHEMA_PREFIX_MAX_LENGTH = 50
TENANT_ID_MAX_LENGTH = 50
CONFIG_FILE_NAME = '.config.json'
TENANT_PREFIX = '_TENANT_'

class DBUserType(Enum):
    ADMIN = 'admin'
    SCHEMA_MODIFY = 'schema_modify'
    DATA_WRITE = 'data_write'
    DATA_READ = 'data_read'

class ConfigCredentials(Credentials):
    """Contains credentials of a single user.
    In: config, selected user"""
    def __init__(self, config) -> None:
        host = config['hana']['connection']['host']
        port = config['hana']['connection']['port']
        user = f"{config['deployment']['schemaPrefix']}_ADMIN"
        password = config['hana']['adminPassword']
        super(ConfigCredentials, self).__init__(host, port, user, password)


