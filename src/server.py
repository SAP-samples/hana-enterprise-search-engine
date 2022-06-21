'''
Provides HTTP(S) interfaces
'''
from datetime import datetime
from fastapi import FastAPI, Request, Body, HTTPException, Response
from starlette.responses import RedirectResponse
import json
import uuid
from db_connection_pool import DBConnection, ConnectionPool, ConnectionPools, Credentials
import mapping
import sqlcreate
from esh_objects import IESSearchOptions
import httpx
import uvicorn
from hdbcli.dbapi import Error as HDBException
import logging
from constants import DBUserType, TENANT_PREFIX, TENANT_ID_MAX_LENGTH
from config import get_user_name, Config
import sys

# run with uvicorn src.server:app --reload
app = FastAPI()

def handle_error(msg: str = '', status_code: int = -1):
    if status_code == -1:
        correlation_id = str(uuid.uuid4())
        logging.info('%s: %s', correlation_id, msg)
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
    return f'{Config.db_tenant_prefix}{tenant_id}'


@app.post('/v1/tenant/{tenant_id}')
async def post_tenant(tenant_id):
    """Create new tenant """
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    with DBConnection(ConnectionPools.pools[DBUserType.ADMIN]) as db:
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
                f'create table "{tenant_schema_name}"."_MODEL" (CREATED_AT TIMESTAMP, CSON NCLOB, NODES NCLOB)')
        except HDBException as e:
            handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
        try:
            read_user_name = get_user_name(Config.db_schema_prefix, DBUserType.DATA_READ)
            write_user_name = get_user_name(Config.db_schema_prefix, DBUserType.DATA_WRITE)
            schema_modify_user_name = get_user_name(Config.db_schema_prefix, DBUserType.SCHEMA_MODIFY)
            db.cur.execute(f'GRANT SELECT ON SCHEMA "{tenant_schema_name}" TO {read_user_name}')
            db.cur.execute(f'GRANT SELECT ON "{tenant_schema_name}"."_MODEL" TO {read_user_name}')
            db.cur.execute(f'GRANT INSERT ON SCHEMA "{tenant_schema_name}" TO {write_user_name}')
            db.cur.execute(f'GRANT DELETE ON SCHEMA "{tenant_schema_name}" TO {write_user_name}')
            db.cur.execute(f'GRANT SELECT ON "{tenant_schema_name}"."_MODEL" TO {write_user_name}')
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
    with DBConnection(ConnectionPools.pools[DBUserType.ADMIN]) as db:
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
    with DBConnection(ConnectionPools.pools[DBUserType.ADMIN]) as db:
        try:
            sql = f'select schema_name, create_time from sys.schemas \
                where schema_name like \'{Config.db_tenant_prefix}%\' order by CREATE_TIME'
            db.cur.execute(sql)
            return [{'name': w[0][len(Config.db_tenant_prefix):], 'createdAt':  w[1]}  for w in db.cur.fetchall()]
        except HDBException as e:
            handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')



@app.post('/v1/deploy/{tenant_id}')
async def post_model(tenant_id: str, cson=Body(...)):
    """ Deploy model """
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    with DBConnection(ConnectionPools.pools[DBUserType.SCHEMA_MODIFY]) as db:
        db.cur.execute(f'select count(*) from "{tenant_schema_name}"."_MODEL"')
        num_deployments = db.cur.fetchone()[0]
        if num_deployments == 0:
            created_at = datetime.now()
            nodes = mapping.cson_to_nodes(cson)
            ddl = sqlcreate.nodes_to_ddl(nodes, tenant_schema_name)
            try:
                db.cur.execute(f'set schema "{tenant_schema_name}"')
                for sql in ddl['tables']:
                    db.cur.execute(sql)
                for sql in ddl['views']:
                    db.cur.execute(sql)
                db.cur.execute(f"CALL ESH_CONFIG('{json.dumps(ddl['eshConfig'])}',?)")
                sql = 'insert into _MODEL (CREATED_AT, CSON, NODES) VALUES (?, ?, ?)'
                db.cur.execute(sql, (created_at, json.dumps(cson), json.dumps(nodes)))
            except HDBException as e:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext} for:\n\t{sql}')
            return {'detail': 'Model successfully deployed'}
        else:
            handle_error('Model already deployed', 422)

@app.post('/v1/data/{tenant_id}')
async def post_data(tenant_id, objects=Body(...)):
    """POST Data"""
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    with DBConnection(ConnectionPools.pools[DBUserType.DATA_WRITE]) as db:
        sql = f'select top 1 NODES from "{tenant_schema_name}"."_MODEL" order by CREATED_AT desc'
        db.cur.execute(sql)
        nodes = json.loads(db.cur.fetchone()[0])
        dml = mapping.objects_to_dml(nodes, objects)
        for table_name, v in dml['inserts'].items():
            column_names = ','.join([f'"{k}"' for k in v['columns'].keys()])
            column_placeholders = ','.join(['?']*len(v['columns']))
            sql = f'insert into "{tenant_schema_name}"."{table_name}" ({column_names})\
                 values ({column_placeholders})'
            db.cur.executemany(sql, v['rows'])


def perform_search(esh_version, tenant_id, esh_query, is_metadata = False):
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    search_query = f'''CALL ESH_SEARCH('["/{esh_version}/{tenant_schema_name}{esh_query.replace("'","''")}"]',?)'''
    #logging.info(search_query)
    with DBConnection(ConnectionPools.pools[DBUserType.DATA_READ]) as db:
        _ = db.cur.execute(search_query)
        for row in db.cur.fetchall():
            if is_metadata:
                return row[0]
            else:
                return json.loads(row[0])
    return None

# Search
@app.post('/v1/search/{tenant_id}')
async def execute_search(tenant_id, query=Body(...)):
    validate_tenant_id(tenant_id)
    result = []
    with DBConnection(ConnectionPools.pools[DBUserType.DATA_READ]) as db:
        tenant_schema_name = get_tenant_schema_name(tenant_id)
        es_statements  = [f'/v20401/{tenant_schema_name}' + \
            IESSearchOptions(w).to_statement().replace("'","''") for w in query]
        search_query = f'''CALL ESH_SEARCH('{json.dumps(es_statements)}',?)'''
        _ = db.cur.execute(search_query)
        for row in db.cur.fetchall():
            res = json.loads(row[0])
            if '@com.sap.vocabularies.Search.v1.SearchStatistics' in res \
                and 'ConnectorStatistics' in res['@com.sap.vocabularies.Search.v1.SearchStatistics']:
                for c in res['@com.sap.vocabularies.Search.v1.SearchStatistics']['ConnectorStatistics']:
                    del c['Schema']
                    del c['Name']
            result.append(res)
    return result

'''
@app.get('/',response_class=RedirectResponse, status_code=302)
async def get_root():
    return RedirectResponse('/v1/searchui/' + UI_TEST_TENANT)
'''

@app.get('/v1/searchui/{tenant_id:path}',response_class=RedirectResponse, status_code=302)
async def get_search_by_tenant(tenant_id):
    redirect_url = (
        '/sap/esh/search/ui/container/SearchUI.html?sinaConfiguration='
        f'{{"provider":"hana_odata","url":"/sap/es/odata/{tenant_id}"}}#Action-search&/top=10'
    )
    return RedirectResponse(redirect_url)

@app.get('/sap/es/odata/{tenant_id:path}/{esh_version:path}/$metadata')
def get_search_metadata(tenant_id,esh_version):
    #print(tenant_id, esh_version)
    return Response(content=perform_search(esh_version, tenant_id, '/$metadata', True), media_type='application/xml')

@app.get('/sap/es/odata/{tenant_id:path}/{esh_version:path}/$metadata/{path:path}')
def get_search_metadata_entity_set(tenant_id, esh_version, path):
    return Response(\
        content=perform_search(esh_version, tenant_id, '/$metadata/{}' + path, True), media_type='application/xml')

@app.get('/sap/es/odata/{tenant_id:path}/{esh_version:path}/{path:path}')
def get_search(tenant_id, esh_version, path, req: Request):
    request_args = dict(req.query_params)
    if '$top' not in request_args:
        request_args['$top'] = 10
    esh_query_string = f'/{path}?' + '&'.join(f'{key}={value}' for key, value in request_args.items())
    return perform_search(esh_version, tenant_id, esh_query_string)

@app.post('/sap/es/odata/{tenant_id:path}/{esh_version:path}/$all')
#def post_search(root=Body(...), db: Session = Depends(get_db)):
def post_search(tenant_id, esh_version, root=Body(...)):
    es_search_options = IESSearchOptions(root)
    print(json.dumps(es_search_options.to_dict(), indent=4))
    print(es_search_options.to_statement())
    return perform_search(esh_version, tenant_id, es_search_options.to_statement())

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

if __name__ == '__main__':
    with open('src/versions.json', encoding = 'utf-8') as fr:
        versions = json.load(fr)
    with open('src/.config.json', encoding = 'utf-8') as fr:
        config = json.load(fr)
        if reinstall_needed(versions, config):
            logging.error('Reset needed due to sofftware changes')
            logging.error('Delete all tenants by running python src/config.py --action delete')
            logging.error('Install new version by running python src/config.py --action install')
            logging.error('Warning: System needs to be setup from scratch again!')
            sys.exit(-1)
        db_host = config['db']['connection']['host']
        db_port = config['db']['connection']['port']
        Config.db_schema_prefix = config['deployment']['schemaPrefix']
        Config.db_tenant_prefix = Config.db_schema_prefix + TENANT_PREFIX
        for user_type_value, user_item in config['db']['user'].items():
            user_type = DBUserType(user_type_value)
            user_name = user_item['name']
            user_password = user_item['password']
            credentials = Credentials(db_host, db_port, user_name, user_password)
            ConnectionPools.pools[user_type] = ConnectionPool(credentials)
            with DBConnection(ConnectionPools.pools[user_type]) as db_main:
                db_main.cur.execute('select * from dummy')

    #ui_default_tenant = config['UIDefaultTenant']
    cs = config['server']
    uvicorn.run('server:app', host = cs['host'], port = cs['port'], log_level = cs['logLevel'], reload = cs['reload'])

