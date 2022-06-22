'''Setup and configuration'''
from argparse import ArgumentParser
from db_connection_pool import Credentials, ConnectionPool, DBConnection
from constants import DBUserType, CURRENT_VERSION, SCHEMA_PREFIX_MAX_LENGTH, CONFIG_FILE_NAME
from enum import Enum
import logging
import sys
import os
import json
import string
import secrets
from hdbcli.dbapi import Error as HDBException

class SetupAction(Enum):
    INSTALL = 'install'
    DELETE = 'delete'
    CLEANUP = 'cleanup'

def generate_secure_alphanum_string(l:int = 32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(l))

def check_if_exists(db:DBConnection, sql:str, desc:str): #pylint: disable=redefined-outer-name
    db.cur.execute(sql)
    existing_items = [w[0] for w in db.cur.fetchall()]
    if existing_items:
        for existing_item in existing_items:
            logging.error('%s %s already exists on database', desc, existing_item)
        return True
    return False

def get_user_name(db_schema_prefix:str, user_type:DBUserType): #pylint: disable=redefined-outer-name
    return f'{db_schema_prefix}_{user_type.name}'

if __name__ == '__main__':
    config_file_full_name = os.path.join(sys.path[0], CONFIG_FILE_NAME)
    parser = ArgumentParser(description='Runs test cases for mapper')
    parser.add_argument('--action', type=str, choices=['install', 'delete', 'cleanup'], default='install',\
        help="Configuration action. Warning: 'delete' or 'cleanup' will delete all data of all tentants!")
    parser.add_argument('--db-host', help='HANA host', type=str, metavar='db_host')
    parser.add_argument('--db-port', help='HANA port', type=int, metavar='db_port')
    parser.add_argument('--db-setup-user', help='Admin user for setup', type=str, metavar='db_setup_user')
    parser.add_argument('--db-setup-password', help='Password for admin user', type=str, metavar='db_setup_password')
    parser.add_argument('--db-schema-prefix', help='Schema prefix for this installation', metavar='db_schema_prefix')
    parser.add_argument('--srv-host', help='Server host', type=str, metavar='srv_host', default='127.0.0.1')
    parser.add_argument('--srv-port', help='Server port', type=int, metavar='srv_port', default=8000)
    parser.add_argument('--srv-log-level', type=str, help='Server log level', metavar='srv_log_level',\
        choices=['critical', 'error', 'warning', 'info', 'debug', 'trace'], default='info')
    parser.add_argument('--srv-reload', help='Server reload after program changes (for development only!)',\
        type=bool, metavar='srv_reload', default=False)

    args = parser.parse_args()
    setup_action = SetupAction(args.action)
    try:
        match setup_action:
            case SetupAction.INSTALL:
                if os.path.exists(config_file_full_name):
                    logging.error('existing installation detected. Config file %s already exists.',\
                        config_file_full_name)
                    msg = ('instead use --action delete or --action cleanup. '
                    'Warning: this will delete all data of all tenants')
                    logging.error(msg)
                    sys.exit(-1)
                config = {'version': CURRENT_VERSION}
                config['server'] = {}
                config['server']['host'] = args.srv_host
                config['server']['port'] = args.srv_port
                config['server']['logLevel'] = args.srv_log_level
                config['server']['reload'] = args.srv_reload
                config['deployment'] = {}
                config['deployment']['schemaPrefix'] = args.db_schema_prefix
                config['deployment']['testTenant'] = generate_secure_alphanum_string()
                config['db'] = {'connection':{'host': args.db_host, 'port': args.db_port}, 'user':{}}
                exceeded_by = len(args.db_schema_prefix) - SCHEMA_PREFIX_MAX_LENGTH
                if exceeded_by > 0:
                    msg = (f'schema-prefex max length {SCHEMA_PREFIX_MAX_LENGTH} '
                        f'exceeded by {exceeded_by} with {args.db_schema_prefix}')
                    logging.error(msg)
                    sys.exit(-1)
                if not (args.db_host and args.db_port and args.db_setup_user and \
                    args.db_setup_password and args.db_schema_prefix):
                    args_list = ['db-host', 'db-port', 'db-setup-user', 'db-setup-password', 'schema-prefix']
                    args_needed = ' '.join([f'--{w}' for w in args_list])
                    logging.error('the following arguments are required for installation: %s', args_needed)
                    sys.exit(-1)
                else:
                    config_admin_credentials = \
                        Credentials(args.db_host, args.db_port, args.db_setup_user, args.db_setup_password)
                    config_admin_pool = ConnectionPool(config_admin_credentials)
                    with DBConnection(config_admin_pool) as db:
                        sql = f"SELECT USER_NAME FROM SYS.USERS WHERE USER_NAME like '{args.db_schema_prefix}%'"
                        error = check_if_exists(db, sql, 'user')
                        sql = f"SELECT SCHEMA_NAME FROM SYS.SCHEMAS WHERE SCHEMA_NAME like '{args.db_schema_prefix}%'"
                        error |= check_if_exists(db, sql, 'schema')
                        if error:
                            msg = (f'Schemas/users starting with {args.db_schema_prefix} already exist. '
                            'Cleanup DB or choose other schema-prefix. Installation aborted')
                            logging.error(msg)
                            sys.exit(-1)
                        sql = "select value from M_HOST_INFORMATION where key = 'build_version'"
                        db.cur.execute(sql)
                        release = db.cur.fetchone()[0].split('.')[0]
                        match release:
                            case '2':
                                schema = '_SYS_RT'
                            case '4':
                                schema = 'SYS'
                            case _:
                                raise NotImplementedError
                        for user_type in DBUserType:
                            user_name = get_user_name(args.db_schema_prefix, user_type)
                            user_password = generate_secure_alphanum_string()
                            sql = f'CREATE USER {user_name} PASSWORD {user_password} NO FORCE_FIRST_PASSWORD_CHANGE'
                            db.cur.execute(sql)
                            logging.info('DB User %s created', user_name)
                            config['db']['user'][user_type.value] = {'name': user_name, 'password': user_password}
                            match user_type:
                                case DBUserType.ADMIN:
                                    sqls = [f'GRANT CREATE SCHEMA TO {user_name}']
                                case DBUserType.SCHEMA_MODIFY:
                                    sqls = [\
                                        f'GRANT EXECUTE ON SYS.ESH_CONFIG TO {user_name} WITH GRANT OPTION',\
                                        f'GRANT SELECT ON {schema}.ESH_MODEL TO {user_name} WITH GRANT OPTION',\
                                        f'GRANT SELECT ON {schema}.ESH_MODEL_PROPERTY TO {user_name} WITH GRANT OPTION'\
                                        ]
                                case DBUserType.DATA_READ:
                                    sqls = [\
                                        f'GRANT EXECUTE ON SYS.ESH_SEARCH TO {user_name} WITH GRANT OPTION',\
                                        f'GRANT SELECT ON {schema}.ESH_MODEL TO {user_name} WITH GRANT OPTION',\
                                        f'GRANT SELECT ON {schema}.ESH_MODEL_PROPERTY TO {user_name} WITH GRANT OPTION'\
                                        ]
                            for sql in sqls:
                                db.cur.execute(sql)
                        with open(config_file_full_name, 'w', encoding = 'utf-8') as fw:
                            json.dump(config, fw, indent = 4)
            case SetupAction.DELETE:
                if not os.path.exists(config_file_full_name):
                    logging.error('Config file %s does not exist.', config_file_full_name)
                    sys.exit(-1)
                if not (args.db_setup_user and args.db_setup_password):
                    args_needed = ' '.join([f'--{w}' for w in ['db-setup-user', 'db-setup-password']])
                    logging.error('the following arguments are required for delete: %s', args_needed)
                    sys.exit(-1)
                else:
                    with open(config_file_full_name, 'r', encoding = 'utf-8') as fr:
                        stored_config = json.load(fr)
                    config_admin_credentials = Credentials(stored_config['db']['connection']['host'], \
                        stored_config['db']['connection']['port'], args.db_setup_user, args.db_setup_password)
                    config_admin_pool = ConnectionPool(config_admin_credentials)
                    with DBConnection(config_admin_pool) as db:
                        for user_type_value, user in stored_config['db']['user'].items():
                            user_type = DBUserType(user_type_value)
                            user_name = get_user_name(stored_config['deployment']['schemaPrefix'], user_type)
                            sql = f'DROP USER {user_name} CASCADE'
                            db.cur.execute(f'DROP USER {user_name} CASCADE')
                            logging.info('DB User %s dropped', user_name)
                    os.remove(config_file_full_name)
                    logging.info('Deletion successful')
    except HDBException as e:
        if e.errorcode == 10:
            logging.error('Authentication failed. Check provided db-setup-user / db-setup-passord')
        else:
            logging.error(e.errortext)
