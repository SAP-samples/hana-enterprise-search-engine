'''
Provides HTTP(S) interfaces
'''
from datetime import datetime
from fastapi import FastAPI, Request, Body, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
import json
import uuid
from db_connection_pool import DBConnection, ConnectionPool, Credentials
import convert
import sqlcreate
from esh_objects import IESSearchOptions
import httpx
import uvicorn
from hdbcli.dbapi import Error as HDBException
from hdbcli.dbapi import DataError
import logging
from constants import DBUserType, TENANT_PREFIX, TENANT_ID_MAX_LENGTH, TYPES_B64_ENCODE, TYPES_SPATIAL
from config import get_user_name
import sys
#import logging
import server_globals as glob
import base64

# run with uvicorn src.server:app --reload
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def handle_error(msg: str = '', status_code: int = -1):
    if status_code == -1:
        correlation_id = str(uuid.uuid4())
        logging.error('%s: %s', correlation_id, msg)
        raise HTTPException(500, f'Error {correlation_id}')
    else:
        raise HTTPException(status_code, msg)

def validate_tenant_id(tenant_id: str):
    if not tenant_id.isalnum():
        handle_error('Tenant-ID must be alphanumeric', 400)
    if len(tenant_id) > TENANT_ID_MAX_LENGTH:
        handle_error('Tenant-ID is {TENANT_ID_MAX_LENGTH} characters maximum', 400)

def get_tenant_schema_name(tenant_id: str):
    validate_tenant_id(tenant_id)
    return f'{glob.db_tenant_prefix}{tenant_id}'

def esh_search_escape(s):
    return s.replace("'","''")

def cleanse_output(res_in):
    res_out = []
    for res in res_in:
        if '@com.sap.vocabularies.Search.v1.SearchStatistics' in res \
            and 'ConnectorStatistics' in res['@com.sap.vocabularies.Search.v1.SearchStatistics']:
            for c in res['@com.sap.vocabularies.Search.v1.SearchStatistics']['ConnectorStatistics']:
                del c['Schema']
                del c['Name']
        res_out.append(res)
    return res_out

@app.post('/v1/tenant/{tenant_id}')
async def post_tenant(tenant_id):
    """Create new tenant """
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    with DBConnection(glob.connection_pools[DBUserType.ADMIN]) as db:
        try:
            sql = f'create schema "{tenant_schema_name}"'
            db.cur.execute(sql)
        except HDBException as e:
            if e.errorcode == 386:
                handle_error(f"Tenant creation failed. Tennant id '{tenant_id}' already exists", 422)
            else:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
        try:
            db.cur.execute(\
                f'create table "{tenant_schema_name}"."_MODEL" (CREATED_AT TIMESTAMP, CSON NCLOB, MAPPING NCLOB)')
        except HDBException as e:
            handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
        try:
            read_user_name = get_user_name(glob.db_schema_prefix, DBUserType.DATA_READ)
            write_user_name = get_user_name(glob.db_schema_prefix, DBUserType.DATA_WRITE)
            schema_modify_user_name = get_user_name(glob.db_schema_prefix, DBUserType.SCHEMA_MODIFY)
            db.cur.execute(f'GRANT SELECT ON SCHEMA "{tenant_schema_name}" TO {read_user_name}')
            db.cur.execute(f'GRANT SELECT ON "{tenant_schema_name}"."_MODEL" TO {read_user_name}')
            db.cur.execute(f'GRANT INSERT ON SCHEMA "{tenant_schema_name}" TO {write_user_name}')
            db.cur.execute(f'GRANT SELECT ON SCHEMA "{tenant_schema_name}" TO {write_user_name}')
            db.cur.execute(f'GRANT DELETE ON SCHEMA "{tenant_schema_name}" TO {write_user_name}')
            db.cur.execute(f'GRANT SELECT ON "{tenant_schema_name}"."_MODEL" TO {schema_modify_user_name}')
            db.cur.execute(f'GRANT INSERT ON "{tenant_schema_name}"."_MODEL" TO {schema_modify_user_name}')
            db.cur.execute(f'GRANT DELETE ON "{tenant_schema_name}"."_MODEL" TO {schema_modify_user_name}')
            db.cur.execute(f'GRANT CREATE ANY ON SCHEMA "{tenant_schema_name}" TO {schema_modify_user_name}')
            db.cur.execute(f'GRANT DROP ON SCHEMA "{tenant_schema_name}" TO {schema_modify_user_name}')
            db.cur.execute(f'GRANT ALTER ON SCHEMA "{tenant_schema_name}" TO {schema_modify_user_name}')
            logging.info('Tenant schema created %s', tenant_schema_name)
        except HDBException as e:
            handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')

    return {'detail': f"Tenant '{tenant_id}' successfully created"}

@app.delete('/v1/tenant/{tenant_id}')
async def delete_tenant(tenant_id: str):
    """Delete tenant"""
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    with DBConnection(glob.connection_pools[DBUserType.ADMIN]) as db:
        try:
            db.cur.execute(f'drop schema "{tenant_schema_name}" cascade')
        except HDBException as e:
            if e.errorcode == 362:
                handle_error(f"Tenant deletion failed. Tennant id '{tenant_id}' does not exist", 404)
            else:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
    return {'detail': f"Tenant '{tenant_id}' successfully deleted"}

@app.get('/v1/tenant')
async def get_tenants():
    """Get all tenants"""
    return get_tenants_sync()


def get_tenants_sync():
    with DBConnection(glob.connection_pools[DBUserType.ADMIN]) as db:
        try:
            sql = f'select schema_name, create_time from sys.schemas \
                where schema_name like \'{glob.db_tenant_prefix}%\' order by CREATE_TIME'
            db.cur.execute(sql)
            return [{'name': w[0][len(glob.db_tenant_prefix):], 'createdAt':  w[1]}  for w in db.cur.fetchall()]
        except HDBException as e:
            handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')



@app.post('/v1/deploy/{tenant_id}')
async def post_model(tenant_id: str, cson=Body(...)):
    """ Deploy model """
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    with DBConnection(glob.connection_pools[DBUserType.SCHEMA_MODIFY]) as db:
        db.cur.execute(f'set schema "{tenant_schema_name}"')
        db.cur.execute('select count(*) from "_MODEL"')
        num_deployments = db.cur.fetchone()[0]
        if num_deployments == 0:
            created_at = datetime.now()
            try:
                mapping = convert.cson_to_mapping(cson)
                ddl = sqlcreate.mapping_to_ddl(mapping, tenant_schema_name)
            except convert.ModelException as e:
                handle_error(str(e), 400)
            try:
                for sql in ddl['tables']:
                    db.cur.execute(sql)
                for sql in ddl['views']:
                    db.cur.execute(sql)
                db.cur.execute(f"CALL ESH_CONFIG('{json.dumps(ddl['eshConfig'])}',?)")
                sql = 'insert into _MODEL (CREATED_AT, CSON, MAPPING) VALUES (?, ?, ?)'
                db.cur.execute(sql, (created_at, json.dumps(cson), json.dumps(mapping)))
                db.con.commit()
            except HDBException as e:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext} for:\n\t{sql}')
            return {'detail': 'Model successfully deployed'}
        else:
            handle_error('Model already deployed', 422)

def get_mapping(tenant_id):
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        db.cur.execute(f'set schema "{tenant_schema_name}"')
        sql = f'select top 1 MAPPING from "{tenant_schema_name}"."_MODEL" order by CREATED_AT desc'
        db.cur.execute(sql)
        res = db.cur.fetchone()
        if not (res and len(res) == 1):
            logging.error('Tenant %s has no entries in the _MODEL table', tenant_id)
            handle_error('Configuration inconsistent', 500)
    return json.loads(res[0])


@app.post('/v1/data/{tenant_id}')
async def post_data(tenant_id, objects=Body(...)):
    """CREATE Data"""
    if not isinstance(objects, dict):
        handle_error('provide dictionary of object types', 400)
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    mapping = get_mapping(tenant_id)
    with DBConnection(glob.connection_pools[DBUserType.DATA_WRITE]) as db:
        db.cur.execute(f'set schema "{tenant_schema_name}"')
        try:
            dml = convert.objects_to_dml(mapping, objects)
        except convert.DataException as e:
            handle_error(str(e), 400)
        try:
            for table_name, v in dml['inserts'].items():
                column_names = ','.join([f'"{k}"' for k in v['columns'].keys()])
                cp = []
                table = mapping['tables'][table_name]
                for column_name in v['columns'].keys():
                    if table['columns'][column_name]['type'] in TYPES_SPATIAL:
                        srid = table['columns'][column_name]['srid']
                        cp.append(f'ST_GeomFromGeoJSON(?, {srid})')
                    else:
                        cp.append('?')
                column_placeholders = ','.join(cp)
                sql = f'insert into "{table_name}" ({column_names}) values ({column_placeholders})'
                db.cur.executemany(sql, v['rows'])
            db.con.commit()
        except DataError as e:
            db.con.rollback()
            handle_error(f'Data Error: {e.errortext}', 400)

    response = {}
    for object_type, obj_list in objects.items():
        if not isinstance(obj_list, list):
            handle_error('provide list of objects per object type', 400)
        if object_type not in mapping['entities']:
            handle_error(f'unknown object type {object_type}', 400)
        root_table = mapping['tables'][mapping['entities'][object_type]['table_name']]
        key_property = root_table['columns'][root_table['pk']]['external_path'][0]
        for obj in obj_list:
            res = {}
            if key_property in obj:
                res[key_property] = obj[key_property]
            if 'source' in obj:
                res['source'] = obj['source']
            if res:
                if not object_type in response:
                    response[object_type] = []
                response[object_type].append(res)
    return response


def value_int_to_ext(typ, value):
    if typ in TYPES_B64_ENCODE:
        return base64.encodebytes(value).decode('utf-8')
    elif typ in TYPES_SPATIAL:
        return json.loads(value)
    return value



@app.post('/v1/read/{tenant_id}')
async def read_data(tenant_id, objects=Body(...)):
    """READ Data"""
    if not isinstance(objects, dict):
        handle_error('provide dictionary of object types', 400)
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    mapping = get_mapping(tenant_id)
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        db.cur.execute(f'set schema "{tenant_schema_name}"')
        response = {}
        for object_type, obj_list  in objects.items():
            if not isinstance(obj_list, list):
                handle_error('provide list of objects per object type', 400)
            if object_type not in mapping['entities']:
                handle_error(f'unknown object type {object_type}', 400)
            root_table = mapping['tables'][mapping['entities'][object_type]['table_name']]
            ids = []
            primary_key_property_name = \
                root_table['columns'][root_table['pk']]['external_path'][0]
            table_sequence = []
            get_table_sequence(mapping, table_sequence, root_table)
            for obj in obj_list:
                if not primary_key_property_name in obj:
                    handle_error(f'primary key {primary_key_property_name} not found', 400)
                ids.append(obj[primary_key_property_name])
            id_list = ', '.join([f"'{w}'" for w in ids])
            all_objects = {}

            for table in table_sequence:
                all_objects[table['table_name']] = {}
                sql = table['sql']['select'].format(id_list = id_list)
                db.cur.execute(sql)
                if '_VALUE' in table['columns']:
                    for row in db.cur:
                        key, _ , val_int = row
                        value = value_int_to_ext(table['columns']['_VALUE']['type'], val_int)
                        if key in all_objects[table['table_name']]:
                            all_objects[table['table_name']][key].append(value)
                        else:
                            all_objects[table['table_name']][key] = [value]
                else:
                    for row in db.cur:
                        i = 0
                        res_obj = {}
                        for prop_name, prop in table['columns'].items():
                            if prop_name == table['pk']:
                                sub_obj_key = row[i]
                                if table['level'] == 0:
                                    res_key = row[i]
                                    add_value(prop, res_obj, prop['external_path'], row[i])
                            elif table['level'] > 0 and prop_name == table['pkParent']:
                                res_key = row[i]
                            elif 'isVirtual' in prop and prop['isVirtual']:
                                if prop['rel']['type'] == 'containment':
                                    if sub_obj_key in all_objects[prop['rel']['table_name']]:
                                        sub_obj = all_objects[prop['rel']['table_name']][sub_obj_key]
                                        add_value(prop, res_obj, prop['external_path'], sub_obj)
                                continue
                            elif 'rel' in prop and prop['rel']['type'] == 'association':
                                rel_table = mapping['tables'][prop['rel']['table_name']]
                                path = prop['external_path']\
                                    + rel_table['columns'][rel_table['pk']]['external_path']
                                add_value(prop, res_obj, path, row[i])
                            else:
                                add_value(prop, res_obj, prop['external_path'], row[i])
                            i += 1
                        if table['level'] > 0:
                            if not res_key in all_objects[table['table_name']]:
                                all_objects[table['table_name']][res_key] = []
                            all_objects[table['table_name']][res_key].append(res_obj)
                        else:
                            all_objects[table['table_name']][res_key] = res_obj
            response[object_type] = []
            for i in ids:
                response[object_type].append(all_objects[root_table['table_name']][i])
    return response

@app.delete('/v1/data/{tenant_id}')
async def delete_data(tenant_id, objects=Body(...)):
    """DELETE Data"""
    if not isinstance(objects, dict):
        handle_error('provide dictionary of object types', 400)
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    mapping = get_mapping(tenant_id)
    with DBConnection(glob.connection_pools[DBUserType.DATA_WRITE]) as db:
        db.cur.execute(f'set schema "{tenant_schema_name}"')
        for object_type, obj_list  in objects.items():
            if not isinstance(obj_list, list):
                handle_error('provide list of objects per object type', 400)
            if object_type not in mapping['entities']:
                handle_error(f'unknown object type {object_type}', 400)
            root_table = mapping['tables'][mapping['entities'][object_type]['table_name']]
            ids = []
            primary_key_property_name = \
                root_table['columns'][root_table['pk']]['external_path'][0]
            table_sequence = []
            get_table_sequence(mapping, table_sequence, root_table)
            for obj in obj_list:
                if not primary_key_property_name in obj:
                    handle_error(f'primary key {primary_key_property_name} not found', 400)
                ids.append(obj[primary_key_property_name])
            id_list = ', '.join([f"'{w}'" for w in ids])

            for table in table_sequence:
                sql = table['sql']['delete'].format(id_list = id_list)
                db.cur.execute(sql)
        db.con.commit()

def add_value(column, obj, path, value):
    if value is None:
        return
    if len(path) == 1:
        if 'type' in column:
            obj[path[0]] = value_int_to_ext(column['type'], value)
        else:
            obj[path[0]] = value
    else:
        if not path[0] in obj:
            obj[path[0]] = {}
        add_value(column, obj[path[0]], path[1:], value)

def get_table_sequence(mapping, table_sequence, current_table):
    for prop in current_table['columns'].values():
        if 'rel' in prop and prop['rel']['type'] == 'containment':
            next_table = mapping['tables'][prop['rel']['table_name']]
            get_table_sequence(mapping, table_sequence, next_table)
    table_sequence.append(current_table)


def perform_search(esh_version, tenant_id, esh_query, is_metadata = False):
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    sql = f'''CALL ESH_SEARCH('["/{esh_version}/{tenant_schema_name}{esh_search_escape(esh_query)}"]',?)'''
    #logging.info(search_query)
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        _ = db.cur.execute(sql)
        for row in db.cur.fetchall():
            if is_metadata:
                return row[0]
            else:
                return json.loads(row[0])
    return None

def perform_bulk_search(esh_version, tenant_id, esh_query):
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    payload = [f'/{esh_version}/{tenant_schema_name}/{w}' for w in esh_query]
    bulk_request = esh_search_escape(json.dumps([{'URI': payload}]))
    sql = f"CALL ESH_SEARCH('{bulk_request}',?)"
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        _ = db.cur.execute(sql)
        #res = '[' + ','.join([w[0] for w in db.cur.fetchall()]) + ']'
        #return Response(content=res, media_type="application/json")
        res = [json.loads(w[0]) for w in db.cur.fetchall()]
        return cleanse_output(res)

def get_esh_version(version):
    if version == 'latest' or version == '':
        return glob.esh_apiversion
    return version

@app.get('/',response_class=RedirectResponse, status_code=302)
async def get_static_index():
    redirect_url = (
        '/static/index.html'
    )
    return RedirectResponse(redirect_url)

@app.get('/v1/searchui/{tenant_id:path}',response_class=RedirectResponse, status_code=302)
async def get_search_by_tenant(tenant_id):
    redirect_url = (
        '/sap/esh/search/ui/container/SearchUI.html?sinaConfiguration='
        f'{{"provider":"hana_odata","url":"/v1/search/{tenant_id}"}}#Action-search&/top=10'
    )
    return RedirectResponse(redirect_url)

@app.get('/v1/search/{tenant_id:path}/{esh_version:path}/$metadata')
def get_search_metadata(tenant_id,esh_version):
    return Response(\
        content=perform_search(get_esh_version(esh_version), tenant_id, '/$metadata', True)\
            , media_type='application/xml')

@app.get('/v1/search/{tenant_id:path}/{esh_version:path}/$metadata/{path:path}')
def get_search_metadata_entity_set(tenant_id, esh_version, path):
    return Response(\
        content=perform_search(get_esh_version(esh_version), tenant_id, '/$metadata/{}' + path, True)\
            , media_type='application/xml')

@app.get('/v1/search/{tenant_id:path}/{esh_version:path}/{path:path}')
def get_search(tenant_id, esh_version, path, req: Request):
    request_args = dict(req.query_params)
    if '$top' not in request_args:
        request_args['$top'] = 10
    esh_query_string = f'/{path}?' + '&'.join(f'{key}={value}' for key, value in request_args.items())
    return cleanse_output([perform_search(get_esh_version(esh_version), tenant_id, esh_query_string)])[0]

@app.post('/v1/search/{tenant_id:path}/{esh_version:path}')
#def post_search(root=Body(...), db: Session = Depends(get_db)):
def post_search(tenant_id, esh_version, body=Body(...)):
    return perform_bulk_search(get_esh_version(esh_version), tenant_id, body)

# v2 Search
@app.post('/v2/search/{tenant_id}/{esh_version:path}')
async def search_v2(tenant_id, esh_version, query=Body(...)):
    validate_tenant_id(tenant_id)
    esh_query = [IESSearchOptions(w).to_statement()[1:] for w in query]
    return perform_bulk_search(get_esh_version(esh_version), tenant_id, esh_query)

@app.get('/{path:path}')
async def tile_request(path: str, response: Response):
    logging.info(path)
    logging.info('https://sapui5.hana.ondemand.com/%s', path)
    async with httpx.AsyncClient() as client:
        proxy = await client.get(f'https://sapui5.hana.ondemand.com/{path}')
    response.body = proxy.content
    response.status_code = proxy.status_code
    return response

def reinstall_needed(l_versions, l_config):
    reinstall = [k for k, v in l_versions.items()\
        if k > l_config['version'] and 'reinstall' in v and v['reinstall']]
    return len(reinstall) > 0

def reindex_needed(l_versions, l_config):
    reinstall = [k for k, v in l_versions.items()\
        if k > l_config['version'] and 'reindex' in v and v['reindex']]
    return len(reinstall) > 0 and get_tenants_sync()

def new_version(l_versions, l_config):
    new_v = [k for k, v in l_versions.items() if k > l_config['version']]
    return len(new_v) > 0


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    with open('src/versions.json', encoding = 'utf-8') as fr:
        versions = json.load(fr)
    try:
        with open('src/.config.json', encoding = 'utf-8') as fr:
            config = json.load(fr)
    except FileNotFoundError:
        logging.error('Inconsistent or missing installation. src/.config.json not found.')
        exit(-1)
    if reinstall_needed(versions, config):
        logging.error('Reset needed due to software changes')
        logging.error('Delete all tenants by running python src/config.py --action delete')
        logging.error('Install new version by running python src/config.py --action install')
        logging.error('Warning: System needs to be setup from scratch again!')
        sys.exit(-1)
    db_host = config['db']['connection']['host']
    db_port = config['db']['connection']['port']
    glob.db_schema_prefix = config['deployment']['schemaPrefix']
    glob.db_tenant_prefix = glob.db_schema_prefix + TENANT_PREFIX
    for user_type_value, user_item in config['db']['user'].items():
        user_type = DBUserType(user_type_value)
        user_name = user_item['name']
        user_password = user_item['password']
        credentials = Credentials(db_host, db_port, user_name, user_password)
        glob.connection_pools[user_type] = ConnectionPool(credentials)
        with DBConnection(glob.connection_pools[user_type]) as db_main:
            db_main.cur.execute('select * from dummy')

    if new_version(versions, config):
        if reindex_needed(versions, config):
            logging.error('Reset needed due to software changes')
            logging.error('Delete all tenants by running python src/config.py --action delete')
            logging.error('Install new version by running python src/config.py --action install')
            logging.error('Warning: System needs to be setup from scratch again!')
            sys.exit(-1)
        else:
            config['version'] = [k for k in versions.keys()][-1]
            with open('src/.config.json', 'w', encoding = 'utf-8') as fr:
                json.dump(config, fr, indent = 4)

    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db_read:
        r = [ { 'URI': [ '/$apiversion' ] } ]
        search_query = f'''CALL ESH_SEARCH('{json.dumps(r)}',?)'''
        _ = db_read.cur.execute(search_query)
        glob.esh_apiversion = 'v' + str(json.loads(db_read.cur.fetchone()[0])['apiversion'])
        #logging.info('ESH_SEARCH calls will use API-version %s', glob.esh_apiversion)

    #ui_default_tenant = config['UIDefaultTenant']
    cs = config['server']
    uvicorn.run('server:app', host = cs['host'], port = cs['port'], log_level = cs['logLevel'], reload = cs['reload'])
