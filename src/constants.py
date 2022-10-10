'''Helper classes and functions'''
from enum import Enum
from db_connection_pool import Credentials

ENTITY_PREFIX = 'ENTITY/'
VIEW_PREFIX = 'VIEW/'

SCHEMA_PREFIX_MAX_LENGTH = 50
TENANT_ID_MAX_LENGTH = 50
CONFIG_FILE_NAME = '.config.json'
TENANT_PREFIX = '_TENANT_'

TYPES_B64_DECODE = set(['VARBINARY', 'BINTEXT', 'BLOB', 'BINARY'])
TYPES_B64_ENCODE = set(['VARBINARY', 'BLOB', 'BINARY'])
TYPES_SPATIAL = set(['ST_POINT', 'ST_GEOMETRY'])

SPATIAL_DEFAULT_SRID = 4326
CONCURRENT_CONNECTIONS = 12

CSON_TYPES = set(['cds.UUID','cds.String','cds.LargeString','cds.Varchar','cds.Integer64'\
    ,'cds.Timestamp','cds.Boolean','cds.Date','cds.Integer','cds.Decimal','cds.Double'\
    ,'cds.Time','cds.DateTime','cds.Timestamp','cds.Binary','cds.LargeBinary'\
    ,'cds.hana.BINARY','cds.hana.VARCHAR','cds.hana.SMALLINT','cds.hana.TINYINT'\
    ,'cds.hana.SMALLDECIMAL','cds.hana.REAL','cds.hana.CLOB','cds.hana.CHAR','cds.hana.NCHAR'\
    ,'cds.hana.ST_POINT','cds.hana.ST_GEOMETRY','cds.Association',
])

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


