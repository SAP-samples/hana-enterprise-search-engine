'''
Provides HTTP(S) interfaces
'''
import base64
import json
import logging
import sys
import uuid
#from asyncio import gather, get_event_loop
from datetime import datetime
from typing import List

import httpx
import uvicorn
from fastapi import Body, FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
#from hdbcli.dbapi import DataError
from hdbcli.dbapi import Error as HDBException
#from hdbcli.dbapi import IntegrityError
from starlette.responses import RedirectResponse

import consistency_check
import convert
import query_mapping
import server_globals as glob
import sqlcreate
from column_view import ColumnView
from config import get_user_name
from constants import (CONCURRENT_CONNECTIONS, TENANT_ID_MAX_LENGTH,
                       TENANT_PREFIX, TYPES_B64_ENCODE, TYPES_SPATIAL,
                       DBUserType)
from db_connection_pool import (ConnectionPool, Credentials, DBBulkProcessing,
                                DBConnection)
from esh_objects import EshObject
from request_mapping import map_request

# run with uvicorn src.server:app --reload
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

LENGTH_ODATA_METADATA_PREFIX = len('$metadata#')

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
            db.cur.connection.rollback()
            if e.errorcode == 386:
                handle_error(f"Tenant creation failed. Tennant id '{tenant_id}' already exists", 422)
            else:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
        try:
            db.cur.execute(\
                f'create table "{tenant_schema_name}"."_MODEL" (CREATED_AT TIMESTAMP, CSON NCLOB, MAPPING NCLOB)')
            glob.mapping.pop(tenant_schema_name, None)
        except HDBException as e:
            db.cur.connection.rollback()
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
            db.cur.connection.rollback()
            handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
        db.cur.connection.commit()
    return {'detail': f"Tenant '{tenant_id}' successfully created"}

@app.delete('/v1/tenant/{tenant_id}')
async def delete_tenant(tenant_id: str):
    """Delete tenant"""
    with DBConnection(glob.connection_pools[DBUserType.ADMIN]) as db:
        tenant_schema_name = get_tenant_schema_name(tenant_id)
        try:
            db.cur.execute(f'drop schema "{tenant_schema_name}" cascade')
            if tenant_schema_name in glob.mapping:
                glob.mapping.pop(tenant_schema_name, None)
        except HDBException as e:
            db.cur.connection.rollback()
            if e.errorcode == 362:
                handle_error(f"Tenant deletion failed. Tennant id '{tenant_id}' does not exist", 404)
            else:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
        db.cur.connection.commit()
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
async def post_model(tenant_id: str, cson = Body(...), simulate: bool = False):
    """ Deploy model """
    errors = consistency_check.check_cson(cson)
    if errors:
        raise HTTPException(422, errors)
    if simulate:
        return {'detail': 'Model is consistent'}
    else:
        with DBConnection(glob.connection_pools[DBUserType.SCHEMA_MODIFY]) as db:
            tenant_schema_name = get_tenant_schema_name(tenant_id)
            db.cur.execute(f'select count(*) from "{tenant_schema_name}"."_MODEL"')
            num_deployments = db.cur.fetchone()[0]
            if num_deployments != 0:
                handle_error('Model already deployed', 422)
        created_at = datetime.now()
        try:
            mapping = convert.cson_to_mapping(cson)
            ddl = sqlcreate.mapping_to_ddl(mapping, tenant_schema_name)
        except convert.ModelException as e:
            handle_error(str(e), 400)
        try:
            block_size = CONCURRENT_CONNECTIONS if len(ddl['tables']) > CONCURRENT_CONNECTIONS else len(ddl['tables'])
            with DBBulkProcessing(glob.connection_pools[DBUserType.SCHEMA_MODIFY], block_size) as db_bulk:
                try:
                    await db_bulk.execute(ddl['tables'])
                    await db_bulk.execute(ddl['views'])
                    await db_bulk.commit()
                except HDBException as e:
                    await db_bulk.rollback()
                    handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
            with DBConnection(glob.connection_pools[DBUserType.SCHEMA_MODIFY]) as db:
                db.cur.callproc('ESH_CONFIG', (json.dumps(ddl['eshConfig']),None))
                sql = f'insert into "{tenant_schema_name}"._MODEL (CREATED_AT, CSON, MAPPING) VALUES (?, ?, ?)'
                db.cur.execute(sql, (created_at, json.dumps(cson), json.dumps(mapping)))
                db.cur.connection.commit()
                glob.mapping[tenant_schema_name] = mapping
        except HDBException as e:
            db.cur.connection.rollback()
            if e.errorcode == 362:
                handle_error(f"Tennant id '{tenant_id}' does not exist", 404)
            else:
                handle_error(f'dbapi Error: {e.errorcode}, {e.errortext}')
        return {'detail': 'Model successfully deployed'}


def get_mapping(tenant_id, schema_name):
    if schema_name in glob.mapping:
        return glob.mapping[schema_name]
    else:
        with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
            sql = f'select top 1 MAPPING from "{schema_name}"."_MODEL" order by CREATED_AT desc'
            db.cur.execute(sql)
            res = db.cur.fetchone()
            if not (res and len(res) == 1):
                logging.error('Tenant %s has no entries in the _MODEL table', tenant_id)
                handle_error('Configuration inconsistent', 500)
        mapping = json.loads(res[0])
        glob.mapping[schema_name] = mapping
        return mapping


@app.post('/v1/data/{tenant_id}')
async def post_data(tenant_id, objects=Body(...)):
    """CREATE Data"""
    if not isinstance(objects, dict):
        handle_error('provide dictionary of object types', 400)
    schema_name = get_tenant_schema_name(tenant_id)
    mapping = get_mapping(tenant_id, schema_name)
    try:
        dml = convert.objects_to_dml(mapping, objects)
    except convert.DataException as e:
        handle_error(str(e), 400)

    operations = []
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
        sql = f'insert into "{schema_name}"."{table_name}" ({column_names}) values ({column_placeholders})'
        operations.append((sql, v['rows']))

    parallel_count = len(operations) if len(operations) < CONCURRENT_CONNECTIONS else CONCURRENT_CONNECTIONS
    with DBBulkProcessing(glob.connection_pools[DBUserType.DATA_WRITE], parallel_count) as db_bulk:
        try:
            await db_bulk.executemany(operations)
            await db_bulk.commit()
        except HDBException as e:
            await db_bulk.rollback()
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
async def read_data(tenant_id:str, objects:dict=Body(...), type_annotation:bool = False):
    """READ Data"""
    if not isinstance(objects, dict):
        handle_error('provide dictionary of object types', 400)
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        schema_name = get_tenant_schema_name(tenant_id)
        mapping = get_mapping(tenant_id, schema_name)
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
                sql = table['sql']['select'].format(schema_name = schema_name, id_list = id_list)
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
                        if table['level'] == 0 and type_annotation:
                            res_obj = {'@type':object_type}
                        else:
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
    with DBConnection(glob.connection_pools[DBUserType.DATA_WRITE]) as db:
        schema_name = get_tenant_schema_name(tenant_id)
        mapping = get_mapping(tenant_id, schema_name)
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
                sql = table['sql']['delete'].format(schema_name = schema_name, id_list = id_list)
                db.cur.execute(sql)
        db.cur.connection.commit()

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
    #logging.info(search_query)
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        tenant_schema_name = get_tenant_schema_name(tenant_id)
        params = (json.dumps([f"/{esh_version}/{tenant_schema_name}{esh_query}"]), None)
        db.cur.callproc('esh_search', params)
        for row in db.cur.fetchall():
            if is_metadata:
                return row[0]
            else:
                return json.loads(row[0])
    return None

def perform_bulk_search(esh_version, tenant_id, esh_query):
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        tenant_schema_name = get_tenant_schema_name(tenant_id)
        payload = [f'/{esh_version}/{tenant_schema_name}/{w}' for w in esh_query]
        params = (json.dumps([{'URI': payload}]), None)
        db.cur.callproc('esh_search', params)
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
            
@app.get('/v1/search/{tenant_id:path}/{esh_version:path}/$all/{path:path}')
def get_search_all_suggestion(tenant_id, esh_version, path):
    return Response(\
        content=perform_search(get_esh_version(esh_version), tenant_id, f'/$all/{path}', True)\
            , media_type='application/json')

@app.post("/eshobject")
async def update_eshobject(esh_object: EshObject):
# async def update_eshobject(esh_object: EshObject, points: Point | LineString):
    # print(esh_object)
    return {'query': esh_object.to_statement(), 'eshobject': esh_object}

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
async def search_v2(tenant_id, esh_version, queries: List[EshObject]):
    # esh_query = [IESSearchOptions(w).to_statement()[1:] for w in query]
    #esh_query = [EshObject.parse_obj(w).to_statement()[1:] for w in queries]
    #search_object = EshObject.parse_obj(queries)
    esh_query = [w.to_statement()[1:] for w in queries]
    return perform_bulk_search(get_esh_version(esh_version), tenant_id, esh_query)

def get_list_of_substrings_term_found(string_subject):
    startterm = '<TERM>'
    endterm = '</TERM>'
    startfound= '<FOUND>'
    endfound = '</FOUND>'
    intstart=0
    strlength=len(string_subject)
    continueloop = 1
    found_terms = {}

    while intstart < strlength and continueloop == 1:
        intindex_startterm=string_subject.find(startterm,intstart)
        if intindex_startterm != -1: #The substring was found, lets proceed
            intindex_startterm = intindex_startterm+len(startterm)
            intindex_endterm = string_subject.find(endterm,intindex_startterm)
            if intindex_endterm != -1:
                subsequence=string_subject[intindex_startterm:intindex_endterm]
                found_terms[subsequence] = []
                intindex_startfound=string_subject.find(startfound,intindex_endterm)
                intindex_endfound=string_subject.find(endfound,intindex_endterm)
                intindex_startterm_next=string_subject.find(startterm,intindex_endterm)
                while intindex_startterm_next == -1 or intindex_startfound < intindex_startterm_next:
                    if intindex_startfound != -1 and intindex_endfound != 1:
                        found=string_subject[intindex_startfound+len(startfound):intindex_endfound]
                        found_terms[subsequence].append(found)
                    intindex_startfound=string_subject.find(startfound,intindex_startfound+1)
                    if intindex_startfound == -1:
                        break
                    intindex_endfound=string_subject.find(endfound,intindex_endfound+1)
                intstart=intindex_endterm+len(endterm)
            else:
                continueloop=0
        else:
            continueloop=0
    return found_terms

# Search v21
@app.post('/v21/search/{tenant_id}/{esh_version:path}')
async def search_v21(tenant_id, esh_version, query=Body(...)):
    try:
        with DBConnection(glob.connection_pools[DBUserType.SCHEMA_MODIFY]) as db:
            tenant_schema_name = get_tenant_schema_name(tenant_id)
            sql = f'select top 1 MAPPING from "{tenant_schema_name}"."_MODEL" order by CREATED_AT desc'
            db.cur.execute(sql)
            res = db.cur.fetchone()
            if not (res and len(res) == 1):
                logging.error('Tenant %s has no entries in the _MODEL table', tenant_id)
                handle_error('Configuration inconsistent', 500)
            mapping = json.loads(res[0])
            # ddl = sqlcreate.mapping_to_ddl(mapping, tenant_schema_name)
            # for create_view in ddl['views']:
            #     db.cur.execute(create_view)
            # sql = f"CALL ESH_CONFIG('{json.dumps(ddl['eshConfig'])}', ?)"
            esh_mapped_queries = map_request(mapping, query)
            if 'scope' in esh_mapped_queries:
                anchor_entity_name = esh_mapped_queries['scope']
                cv = ColumnView(mapping, anchor_entity_name, tenant_schema_name)
                # for free style elements in query take by_default
                if 'comparison_paths' in esh_mapped_queries and 'exist_free_style' not in esh_mapped_queries:
                    cv.by_path_list([['id']] + esh_mapped_queries['comparison_paths']\
                        , mapping['views'][anchor_entity_name]['view_name']\
                        , mapping['views'][anchor_entity_name]['odata_name'])
                else:
                    cv.by_default()
                view, esh_config = cv.data_definition()
                print(view)
                print(esh_config)
                print(cv.selector)
                db.cur.execute(view)
                #db.cur.execute(f"CALL ESH_CONFIG('{json.dumps([esh_config])}', ?)")
                db.cur.callproc('ESH_CONFIG', (json.dumps([esh_config]), None))

        # esh_mapped_queries = map_request(mapping, query)
        for w in esh_mapped_queries['incoming_requests']:
            a = EshObject.parse_obj(w)
            print(a.to_statement())
        esh_query = [EshObject.parse_obj(w).to_statement()[1:] for w in esh_mapped_queries['incoming_requests']]


        # esh_query = [IESSearchOptions(w).to_statement()[1:] for w in query]
        # return perform_bulk_search(get_esh_version(esh_version), tenant_id, esh_query)
        search_results = perform_bulk_search(get_esh_version(esh_version), tenant_id, esh_query)
        for search_result in search_results:
            if 'value' in search_result:
                for matched_object in search_result['value']:
                    odata_name = matched_object['@odata.context'][LENGTH_ODATA_METADATA_PREFIX:]
                    if 'views' in mapping:
                        for view_value in mapping['views'].values():
                            if view_value['odata_name'] == odata_name:
                                entity_name = view_value['entity_name']
                                break
                    data_request = {
                        entity_name: [
                            {
                                'id': matched_object['ID']
                            }
                        ]
                    }
                    read_data_query = await read_data(tenant_id, data_request)
                    for key in read_data_query[entity_name][0]:
                        matched_object[key] = read_data_query[entity_name][0][key]
                    del matched_object['ID']
                    del matched_object['@odata.context']
                    # matched_object = read_data_query[entity_name][0]
                    matched_object['@esh.context'] = entity_name
                    if '@com.sap.vocabularies.Search.v1.WhyFound' in matched_object:
                        why_found_list = []
                        for key, values in matched_object['@com.sap.vocabularies.Search.v1.WhyFound'].items():
                            why_found_list.append({
                                'selector':  mapping['views'][entity_name]['columns'][key]['path'],
                                'values': values
                            })
                        matched_object['@com.sap.vocabularies.Search.v1.WhyFound'] = why_found_list
                    if '@com.sap.vocabularies.Search.v1.WhereFound' in matched_object\
                         and matched_object['@com.sap.vocabularies.Search.v1.WhereFound']:
                        #alias_list = []
                        where_found = matched_object['@com.sap.vocabularies.Search.v1.WhereFound']
                        found_terms = get_list_of_substrings_term_found(where_found)
                        new_where = {}
                        for term, where_array in found_terms.items():
                            new_where[term] = []
                            for item in where_array:
                                new_where[term].append(mapping['views'][entity_name]['columns'][item]['path'])
                            '''
                            alias_list.append({
                                'alias': [found_property],
                                'selector': mapping['views'][entity_name]['columns'][found_property]['path']
                            })
                            '''
                        # matched_object["@com.sap.vocabularies.Search.v1.Aliases"] = alias_list
                        # matched_object["@com.sap.vocabularies.Search.v1.WhereFoundOriginal"] \
                        # = matched_object["@com.sap.vocabularies.Search.v1.WhereFound"]
                        matched_object['@com.sap.vocabularies.Search.v1.WhereFound'] = new_where
                    for connector_statistic \
                    in search_result['@com.sap.vocabularies.Search.v1.SearchStatistics']['ConnectorStatistics']:
                        if 'OdataID' in connector_statistic and connector_statistic['OdataID'] == odata_name:
                            connector_statistic['@esh.context'] = entity_name
                            del connector_statistic['OdataID']
        return search_results
    except Exception as e:
        return {'error': f'{e}'}

def get_column_view(mapping, anchor_entity_name, schema_name, path_list):
    view_id = str(uuid.uuid4()).replace('-', '').upper()
    view_name = f'VIEW/{view_id}'
    odata_name = f'VIEW_{view_id}'
    cv = ColumnView(mapping, anchor_entity_name, schema_name)
    cv.by_path_list(path_list, view_name, odata_name)
    return cv

# Query v1
@app.post('/v1/query/{tenant_id}/{esh_version:path}')
async def query_v1(tenant_id, esh_version, queries: List[EshObject]):
    schema_name = get_tenant_schema_name(tenant_id)
    with DBConnection(glob.connection_pools[DBUserType.SCHEMA_MODIFY]) as db:
        mapping = get_mapping(tenant_id, schema_name)
        dynmaic_views = []
        configurations = []
        uris = []
        view_ddls = []
        requested_entity_types = []
        for query in queries:
            # query_object = EshObject.parse_obj(query)
            scopes, pathes = query_mapping.extract_pathes(query)
            if len(scopes) != 1:
                handle_error('Exactly one scope is needed', 400)
            scope = scopes[0]
            if not scope in mapping['entities']:
                handle_error(f'unknown entity {scope}', 400)
            requested_entity_types.append(scope)
            cv = get_column_view(mapping, scope, schema_name, pathes.keys())
            view_ddl, esh_config = cv.data_definition()
            configurations.append(esh_config['content'])
            for path in pathes.keys():
                pathes[path] = cv.column_name_by_path(path)
            query_mapping.map_query(query, [cv.odata_name], pathes)
            view_ddls.append(view_ddl)
            dynmaic_views.append(cv.view_name)
            search_object = EshObject.parse_obj(query)
            search_object.select = ['ID']
            esh_query = search_object.to_statement()[1:]
            uris.append(f'/{get_esh_version(esh_version)}/{schema_name}/{esh_query}')
        for view_ddl in view_ddls:
            db.cur.execute(view_ddl)
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        params = (json.dumps([{'Configuration': configurations, 'URI': uris}]), None)
        db.cur.callproc('esh_search', params)
        #search_results = cleanse_output([json.loads(w[0]) for w in db.cur.fetchall()])
        search_results = [json.loads(w[0]) for w in db.cur.fetchall()]
    with DBConnection(glob.connection_pools[DBUserType.SCHEMA_MODIFY]) as db:
        for view_name in dynmaic_views:
            sql = f'drop view "{schema_name}"."{view_name}"'
            db.cur.execute(sql)

    data_request = {}
    for i, search_result in enumerate(search_results):
        if 'value' in search_result and search_result['value']:
            requested_entity_type = requested_entity_types[i]
            if not requested_entity_type in data_request:
                data_request[requested_entity_type] = []
            for res_item in search_result['value']:
                data_request[requested_entity_type].append({'id':res_item['ID']})
    full_objects = await read_data(tenant_id, data_request, True)
    full_objects_idx = {}
    for k, v in full_objects.items():
        full_objects_idx[k] = {}
        for i in v:
            full_objects_idx[k][i['id']] = i

    results = []
    for i, search_result in enumerate(search_results):
        result = {'value': []}
        if 'value' in search_result and search_result['value']:
            requested_entity_type = requested_entity_types[i]
            for res_item in search_result['value']:
                result['value'].append(full_objects_idx[requested_entity_type][res_item['ID']])
        if '@odata.count' in search_result:
            result['@odata.count'] = search_result['@odata.count']
        results.append(result)
    return results

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
        params = (json.dumps([ { 'URI': [ '/$apiversion' ] } ]), None)
        db_read.cur.callproc('esh_search', params)
        glob.esh_apiversion = 'v' + str(json.loads(db_read.cur.fetchone()[0])['apiversion'])
        #logging.info('ESH_SEARCH calls will use API-version %s', glob.esh_apiversion)

    #ui_default_tenant = config['UIDefaultTenant']  
    cs = config['server']
    uvicorn.run('server:app', host = cs['host'], port = cs['port'], log_level = cs['logLevel'], reload = cs['reload'])
