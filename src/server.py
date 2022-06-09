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

# run with uvicorn src.server:app --reload

TENANT_PREFIX = 'HANA_SERVICES_TENANT_'
ENTITY_PREFIX = 'ENTITY_'
DML_USER_NAME = 'TESTHANASERVICESDML'
UI_TEST_TENANT = 'abc'

def handle_error(msg: str = '', status_code: int = -1):
    if status_code == -1:
        correlation_id = str(uuid.uuid4())
        print(f'{correlation_id}: {msg}')
        raise HTTPException(500, f'Error {correlation_id}')
    else:
        raise HTTPException(status_code, msg)

def validate_tenant_id(tenant_id: str):
    if not tenant_id.isalnum():
        handle_error('Tenant-ID must be alphanumeric', 400)
    if len(tenant_id) > 100:
        handle_error('Tenant-ID is 100 characters maximum', 400)

app = FastAPI()
with open('.config.json', encoding = 'utf-8') as fr:
    config = json.load(fr)
db_con_pool_ddl = ConnectionPool(Credentials(config, 'ddl'))
db_con_pool_dml = ConnectionPool(Credentials(config, 'dml'))

@app.post('/v1/tenant/{tenant_id}')
async def post_tenant(tenant_id):
    """Create new tenant """
    validate_tenant_id(tenant_id)
    with DBConnection(db_con_pool_ddl) as db:
        try:
            db.cur.execute(f'create schema "{TENANT_PREFIX}{tenant_id}"')
        except Exception as e:
            if e.errorcode == 386:
                handle_error(f"Tenant creation failed. Tennant id '{tenant_id}' already exists", 422)
            else:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
        try:
            db.cur.execute(\
                f'create table "{TENANT_PREFIX}{tenant_id}"."_MODEL" (CREATED_AT TIMESTAMP, CSON NCLOB, NODES NCLOB)')
        except Exception as e:
            handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
        try:
            db.cur.execute(f'GRANT SELECT ON SCHEMA "{TENANT_PREFIX}{tenant_id}" TO {DML_USER_NAME}')
            db.cur.execute(f'GRANT INSERT ON SCHEMA "{TENANT_PREFIX}{tenant_id}" TO {DML_USER_NAME}')
            db.cur.execute(f'GRANT DELETE ON SCHEMA "{TENANT_PREFIX}{tenant_id}" TO {DML_USER_NAME}')
        except Exception as e:
            handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')

    return {'detail': f"Tenant '{tenant_id}' successfully created"}

@app.delete('/v1/tenant/{tenant_id}')
async def delete_tenant(tenant_id: str):
    """Delete tenant"""
    validate_tenant_id(tenant_id)
    with DBConnection(db_con_pool_ddl) as db:
        try:
            db.cur.execute(f'drop schema "{TENANT_PREFIX}{tenant_id}" cascade')
        except Exception as e:
            if e.errorcode == 362:
                handle_error(f"Tenant deletion failed. Tennant id '{tenant_id}' does not exist", 404)
            else:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
    return {'detail': f"Tenant '{tenant_id}' successfully deleted"}

@app.get('/v1/tenant')
async def get_tenants():
    """Get all tenants"""
    with DBConnection(db_con_pool_ddl) as db:
        try:
            sql = f'select schema_name, create_time from sys.schemas \
                where schema_name like \'{TENANT_PREFIX}%\' order by CREATE_TIME'
            db.cur.execute(sql)
            return [{'name': w[0][len(TENANT_PREFIX):], 'createdAt':  w[1]}  for w in db.cur.fetchall()]
        except Exception as e:
            handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')


@app.post('/v1/deploy/{tenant_id}')
async def post_model(tenant_id: str, cson=Body(...)):
    """ Deploy model """
    validate_tenant_id(tenant_id)
    with DBConnection(db_con_pool_ddl) as db:
        schema_name = f'{TENANT_PREFIX}{tenant_id}'
        db.cur.execute(f'select count(*) from "{schema_name}"."_MODEL"')
        num_deployments = db.cur.fetchone()[0]
        if num_deployments == 0:
            created_at = datetime.now()
            nodes = mapping.cson_to_nodes(cson)
            ddl = sqlcreate.nodes_to_ddl(nodes, schema_name)
            try:
                db.cur.execute(f'set schema "{schema_name}"')
                for sql in ddl['tables']:
                    db.cur.execute(sql)
                for sql in ddl['views']:
                    db.cur.execute(sql)
                db.cur.execute(f"CALL ESH_CONFIG('{json.dumps(ddl['eshConfig'])}',?)")
                sql = 'insert into _MODEL (CREATED_AT, CSON, NODES) VALUES (?, ?, ?)'
                db.cur.execute(sql, (created_at, json.dumps(cson), json.dumps(nodes)))
            except Exception as e:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext} for:\n\t{sql}')
            return {'detail': 'Model successfully deployed'}
        else:
            handle_error('Model already deployed', 422)

@app.post('/v1/data/{tenant_id}')
async def post_data(tenant_id, objects=Body(...)):
    """POST Data"""
    validate_tenant_id(tenant_id)
    schema_name = f'{TENANT_PREFIX}{tenant_id}'
    with DBConnection(db_con_pool_dml) as db:
        sql = f'select top 1 NODES from "{schema_name}"."_MODEL" order by CREATED_AT desc'
        db.cur.execute(sql)
        nodes = json.loads(db.cur.fetchone()[0])
        dml = mapping.objects_to_dml(nodes, objects)
        for table_name, v in dml['inserts'].items():
            column_names = ','.join([f'"{k}"' for k in v['columns'].keys()])
            column_placeholders = ','.join(['?']*len(v['columns']))
            sql = f'insert into "{TENANT_PREFIX}{tenant_id}"."{table_name}" ({column_names})\
                 values ({column_placeholders})'
            db.cur.executemany(sql, v['rows'])


def perform_search(esh_version, tenant_id, esh_query, is_metadata = False):
    schema_name = f'{TENANT_PREFIX}{tenant_id}'
    search_query = f'''CALL ESH_SEARCH('["/{esh_version}/{schema_name}{esh_query.replace("'","''")}"]',?)'''
    print(search_query)
    with DBConnection(db_con_pool_dml) as db:
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
    with DBConnection(db_con_pool_dml) as db:
        schema_name = f'{TENANT_PREFIX}{tenant_id}'
        es_statements  = [f'/v20401/{schema_name}' + \
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
