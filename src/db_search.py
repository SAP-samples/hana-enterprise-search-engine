import uuid
import json
import re


from db_connection_pool import DBConnection
import server_globals as glob
from constants import (DBUserType, ENTITY_PREFIX)
import query_mapping
import convert
from column_view import ColumnView
from esh_objects import map_query, PropertyInternal
from db_crud import read_data
import server_globals as glob


ANNO_RANKING = '@com.sap.vocabularies.Search.v1.Ranking'
ANNO_WHYFOUND = '@com.sap.vocabularies.Search.v1.WhyFound'
ANNO_WHEREFOUND = '@com.sap.vocabularies.Search.v1.WhereFound'

class SearchException(Exception):
    """ Exception during search"""

def _get_esh_version(version):
    if version == 'latest' or version == '':
        return glob.esh_apiversion
    return version


def _cleanse_output(res):
    if '@com.sap.vocabularies.Search.v1.SearchStatistics' in res \
            and 'ConnectorStatistics' in res['@com.sap.vocabularies.Search.v1.SearchStatistics']:
        for c in res['@com.sap.vocabularies.Search.v1.SearchStatistics']['ConnectorStatistics']:
            del c['Schema']
            del c['Name']
    return res
    

def _get_column_view(mapping, anchor_entity_name, schema_name, path_list):
    view_id = str(uuid.uuid4()).replace('-', '').upper()
    view_name = f'DYNAMICVIEW/{view_id}'
    odata_name = f'DYNAMICVIEW_{view_id}'
    anchor_entity = mapping['entities'][anchor_entity_name]
    if 'annotations' in anchor_entity and '@EnterpriseSearch.enabled' in anchor_entity['annotations'] and anchor_entity['annotations']['@EnterpriseSearch.enabled']:
        cv = ColumnView(mapping, anchor_entity_name, schema_name, False)
    else:
        cv = ColumnView(mapping, anchor_entity_name, schema_name, True)
    cv.by_default_and_path_list(path_list, view_name, odata_name)
    return cv


def perform_search(esh_version, schema_name, esh_query, is_metadata=False):
    # logging.info(search_query)
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        search_params = (json.dumps(
            [f'/{_get_esh_version(esh_version)}/{schema_name}{esh_query}']), None)
        db.cur.callproc('esh_search', search_params)
        for row in db.cur.fetchall():
            if is_metadata:
                return row[0]
            else:
                return _cleanse_output(json.loads(row[0]))
    return None


def perform_bulk_search(esh_version, schema_name, esh_query):
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        payload = [
            f'/{_get_esh_version(esh_version)}/{schema_name}/{w}' for w in esh_query]
        params = (json.dumps([{'URI': payload}]), None)
        db.cur.callproc('esh_search', params)
        return [_cleanse_output(json.loads(w[0])) for w in db.cur.fetchall()]


async def search_query(schema_name, mapping, esh_version, queries):
    dynamic_views = {}
    odata_map = {}
    esh_queries = []
    for query in queries:
        uris = []
        configurations = []
        pathes = query_mapping.extract_pathes(query)
        if query.scope:
            if isinstance(query.scope, str):
                scopes = [query.scope]
            elif isinstance(query.scope, list):
                scopes = query.scope
        else:
            scopes = []
        esh_scopes = []
        for scope in scopes:
            if not scope in mapping['entities']:
                raise SearchException(f'unknown entity {scope}')
                #handle_error(f'unknown entity {scope}', 400)
            is_cross_entity = False
            for path in pathes:
                is_valid, is_cross = convert.check_path(
                    mapping, mapping['entities'][scope], path)
                if not is_valid:
                    raise SearchException(f'invalid path {path} for entity {scope}')
                    #handle_error(f'invalid path {path} for entity {scope}', 400)
                is_cross_entity = is_cross_entity or is_cross
            # if is_cross_entity:
                # ToDo: support free-style
            cv = _get_column_view(mapping, scope, schema_name, pathes.keys())
            esh_scopes.append(cv.odata_name)
            view_ddl, esh_config = cv.data_definition()
            configurations.append(esh_config['content'])
            view_map = {k: v for k, _, _, _, v in cv.view_attribute}
            odata_map['$metadata#' +
                      cv.odata_name] = {'entity_type': scope, 'view_map': view_map}
            dynamic_views[cv.view_name] = {'ddl': view_ddl}
            # else:
            #    esh_scopes.append(mapping['entities'][scope]['table_name'][len(ENTITY_PREFIX):])
            for path in pathes.keys():
                pathes[path] = cv.column_name_by_path(path)

        query_mapping.map_query(query, pathes)
        query.scope = esh_scopes
        search_object = map_query(query)
        search_object.select = PropertyInternal(property='ID')
        esh_query = search_object.to_statement()[1:]
        uris.append(
            f'/{_get_esh_version(esh_version)}/{schema_name}/{esh_query}')
        esh_query = {'URI': uris}
        if configurations:
            esh_query['Configuration'] = configurations
        esh_queries.append(esh_query)
    if dynamic_views:
        with DBConnection(glob.connection_pools[DBUserType.SCHEMA_MODIFY]) as db:
            for dynamic_view in dynamic_views.values():
                db.cur.execute(dynamic_view['ddl'])
    with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
        params = (json.dumps(esh_queries), None)
        db.cur.callproc('esh_search', params)
        search_results = [json.loads(w[0]) for w in db.cur.fetchall()]
    if dynamic_views:
        with DBConnection(glob.connection_pools[DBUserType.SCHEMA_MODIFY]) as db:
            for view_name in dynamic_views:
                sql = f'drop view "{schema_name}"."{view_name}"'
                db.cur.execute(sql)
    read_request = {}
    for search_result in search_results:
        if 'error' in search_result:
            raise SearchException(json.dumps(search_results))
            #handle_error(json.dumps(search_results))
        for itm in search_result['value']:
            if itm['@odata.context'] in odata_map:
                entity_type = odata_map[itm['@odata.context']]['entity_type']
            else:
                entity_type = mapping['tables'][ENTITY_PREFIX +
                                                itm['@odata.context'][10:]]['external_path'][0]
                odata_map[itm['@odata.context']]['entity_type'] = entity_type
            if not entity_type in read_request:
                read_request[entity_type] = []
            read_request[entity_type].append({'id': itm['ID']})

    full_objects = await read_data(schema_name, mapping, read_request, True)
    full_objects_idx = {}
    for k, v in full_objects.items():
        full_objects_idx[k] = {}
        for i in v:
            full_objects_idx[k][i['id']] = i

    results = []
    for i, search_result in enumerate(search_results):
        result = {'value': []}
        for itm in search_result['value']:
            r = {}
            if ANNO_RANKING in itm and itm[ANNO_RANKING]:
                r[ANNO_RANKING] = itm[ANNO_RANKING]
            if ANNO_WHYFOUND in itm and itm[ANNO_RANKING]:
                r[ANNO_WHYFOUND] = []
                for k, v in itm[ANNO_WHYFOUND].items():
                    wf = {
                        'found': odata_map[itm['@odata.context']]['view_map'][k], 'term': v}
                    r[ANNO_WHYFOUND].append(wf)
            if ANNO_WHEREFOUND in itm and itm[ANNO_WHEREFOUND]:
                wf = itm[ANNO_WHEREFOUND]
                for prop_name_int in re.findall('(?<=<FOUND>)(.*?)(?=</FOUND>)', itm[ANNO_WHEREFOUND], re.S):
                    prop_name_ext = '.'.join(
                        odata_map[itm['@odata.context']]['view_map'][prop_name_int])
                    wf = wf.replace(
                        f'<FOUND>{prop_name_int}</FOUND>', f'<FOUND>{prop_name_ext}</FOUND>')
            res_item = r | full_objects_idx[odata_map[itm['@odata.context']]
                                            ['entity_type']][itm['ID']]
            result['value'].append(res_item)
        if '@odata.count' in search_result:
            result['@odata.count'] = search_result['@odata.count']
        results.append(result)
    return results
