'''
Provides HTTP(S) interfaces
'''
from datetime import datetime
from fastapi import FastAPI, Request, Body, HTTPException, Response
from starlette.responses import RedirectResponse
import json
import uuid
from db_connection_pool import DBConnection, ConnectionPool, Credentials
import mapping
import sqlcreate
from esh_objects import IESSearchOptions
import httpx
import uvicorn
from hdbcli.dbapi import Error as HDBException
import logging
from constants import DBUserType, TENANT_PREFIX, TENANT_ID_MAX_LENGTH
from config import get_user_name
import sys
#import logging
import server_globals as glob

# run with uvicorn src.server:app --reload
app = FastAPI()

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
                f'create table "{tenant_schema_name}"."_MODEL" (CREATED_AT TIMESTAMP, CSON NCLOB, NODES NCLOB)')
        except HDBException as e:
            handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
        try:
            read_user_name = get_user_name(glob.db_schema_prefix, DBUserType.DATA_READ)
            write_user_name = get_user_name(glob.db_schema_prefix, DBUserType.DATA_WRITE)
            schema_modify_user_name = get_user_name(glob.db_schema_prefix, DBUserType.SCHEMA_MODIFY)
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
        db.cur.execute(f'select count(*) from "{tenant_schema_name}"."_MODEL"')
        num_deployments = db.cur.fetchone()[0]
        if num_deployments == 0:
            created_at = datetime.now()
            try:
                nodes = mapping.cson_to_nodes(cson)
                ddl = sqlcreate.nodes_to_ddl(nodes, tenant_schema_name)
            except mapping.ModelException as e:
                handle_error(str(e), 400)
            try:
                db.cur.execute(f'set schema "{tenant_schema_name}"')
                for sql in ddl['tables']:
                    db.cur.execute(sql)
                for sql in ddl['views']:
                    db.cur.execute(sql)
                db.cur.execute(f"CALL ESH_CONFIG('{json.dumps(ddl['eshConfig'])}',?)")
                sql = 'insert into _MODEL (CREATED_AT, CSON, NODES) VALUES (?, ?, ?)'
                db.cur.execute(sql, (created_at, json.dumps(cson), json.dumps(nodes)))
                db.con.commit()
            except HDBException as e:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext} for:\n\t{sql}')
            return {'detail': 'Model successfully deployed'}
        else:
            handle_error('Model already deployed', 422)

@app.post('/v1/data/{tenant_id}')
async def post_data(tenant_id, objects=Body(...)):
    """POST Data"""
    tenant_schema_name = get_tenant_schema_name(tenant_id)
    with DBConnection(glob.connection_pools[DBUserType.DATA_WRITE]) as db:
        sql = f'select top 1 NODES from "{tenant_schema_name}"."_MODEL" order by CREATED_AT desc'
        db.cur.execute(sql)
        res = db.cur.fetchone()
        if not (res and len(res) == 1):
            logging.error('Tenant %s has no entries in the _MODEL table', tenant_id)
            handle_error('Configuration inconsistent', 500)
        nodes = json.loads(res[0])
        try:
            dml = mapping.objects_to_dml(nodes, objects)
        except mapping.DataException as e:
            handle_error(str(e), 400)
        for table_name, v in dml['inserts'].items():
            column_names = ','.join([f'"{k}"' for k in v['columns'].keys()])
            column_placeholders = ','.join(['?']*len(v['columns']))
            sql = f'insert into "{tenant_schema_name}"."{table_name}" ({column_names})\
                 values ({column_placeholders})'
            db.cur.executemany(sql, v['rows'])
        db.con.commit()
    response = {}
    for object_type, objlist in objects.items():
        for obj in objlist:
            res = {}
            if 'id' in obj:
                res['id'] = obj['id']
            if 'source' in obj:
                res['source'] = obj['source']
            if res:
                if not object_type in response:
                    response[object_type] = []
                response[object_type].append(res)
    return response


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

# Search
@app.post('/v1/search/{tenant_id}')
async def execute_search(tenant_id, query=Body(...)):
    validate_tenant_id(tenant_id)
    esh_query = [IESSearchOptions(w).to_statement()[1:] for w in query]
    return perform_bulk_search(get_esh_version(''), tenant_id, esh_query)


#    result = []
#    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
#        tenant_schema_name = get_tenant_schema_name(tenant_id)
#        es_statements  = [f'/{glob.esh_apiversion}/{tenant_schema_name}' + \
#            esh_search_escape(IESSearchOptions(w).to_statement()) for w in query]
#        sql = f'''CALL ESH_SEARCH('{json.dumps(es_statements)}',?)'''
#        _ = db.cur.execute(sql)
#        for row in db.cur.fetchall():
#            res = json.loads(row[0])
#            if '@com.sap.vocabularies.Search.v1.SearchStatistics' in res \
#                and 'ConnectorStatistics' in res['@com.sap.vocabularies.Search.v1.SearchStatistics']:
#                for c in res['@com.sap.vocabularies.Search.v1.SearchStatistics']['ConnectorStatistics']:
#                    del c['Schema']
#                    del c['Name']
#            result.append(res)
#    return result


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
    return Response(\
        content=perform_search(get_esh_version(esh_version), tenant_id, '/$metadata', True)\
            , media_type='application/xml')

@app.get('/sap/es/odata/{tenant_id:path}/{esh_version:path}/$metadata/{path:path}')
def get_search_metadata_entity_set(tenant_id, esh_version, path):
    return Response(\
        content=perform_search(get_esh_version(esh_version), tenant_id, '/$metadata/{}' + path, True)\
            , media_type='application/xml')

@app.get('/sap/es/odata/{tenant_id:path}/{esh_version:path}/{path:path}')
def get_search(tenant_id, esh_version, path, req: Request):
    request_args = dict(req.query_params)
    if '$top' not in request_args:
        request_args['$top'] = 10
    esh_query_string = f'/{path}?' + '&'.join(f'{key}={value}' for key, value in request_args.items())
    return cleanse_output([perform_search(get_esh_version(esh_version), tenant_id, esh_query_string)])[0]

def get_esh_version(version):
    if version == 'latest' or version == '':
        return glob.esh_apiversion
    return version


@app.post('/sap/es/odata/{tenant_id:path}/{esh_version:path}')
#def post_search(root=Body(...), db: Session = Depends(get_db)):
def post_search(tenant_id, esh_version, body=Body(...)):
    return perform_bulk_search(get_esh_version(esh_version), tenant_id, body)


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
        logging.error('Reset needed due to sofftware changes')
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

    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db_read:
        r = [ { 'URI': [ '/$apiversion' ] } ]
        search_query = f'''CALL ESH_SEARCH('{json.dumps(r)}',?)'''
        _ = db_read.cur.execute(search_query)
        glob.esh_apiversion = 'v' + str(json.loads(db_read.cur.fetchone()[0])['apiversion'])
        #logging.info('ESH_SEARCH calls will use API-version %s', glob.esh_apiversion)

    #ui_default_tenant = config['UIDefaultTenant']
    cs = config['server']
    uvicorn.run('server:app', host = cs['host'], port = cs['port'], log_level = cs['logLevel'], reload = cs['reload'])

