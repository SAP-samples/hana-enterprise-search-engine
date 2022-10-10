"""Mapping between external objects and internal tables using 'tables' as internal runtime-format """
from turtle import backward
from uuid import uuid1
from name_mapping import NameMapping
import json
import base64
from constants import TYPES_B64_DECODE, TYPES_SPATIAL, SPATIAL_DEFAULT_SRID, ENTITY_PREFIX, VIEW_PREFIX


PRIVACY_CATEGORY_COLUMN_DEFINITION = ('_PRIVACY_CATEGORY', {'type':'TINY'})
PRIVACY_CATEGORY_ANNOTATION = '@EnterpriseSearchIndex.privacyCategory'

class DefaultPK:
    @staticmethod
    def get_pk(table_name, subtable_level):
        #pylint: disable=unused-argument
        return uuid1().urn[9:]
    @staticmethod
    def get_definition(subtable_level):
        #pylint: disable=unused-argument
        return ('_ID', {'type':'VARCHAR', 'length': 36, 'isIdColumn': True})

class ModelException(Exception):
    pass

class DataException(Exception):
    pass


def get_sql_type(table_name_mapping, cson, cap_type, pk):
    ''' get SQL type from CAP type'''
    if cap_type['type'] in cson['definitions'] and 'type' in cson['definitions'][cap_type['type']]:
        return get_sql_type(table_name_mapping, cson, cson['definitions'][cap_type['type']], pk)

    sql_type = {}
    if 'length' in cap_type:
        sql_type['length'] = cap_type['length']
    match cap_type['type']:
        case 'cds.UUID':
            sql_type['type'] = 'NVARCHAR'
            sql_type['length'] = 36
        case 'cds.String':
            if '@esh.type.text' in cap_type and cap_type['@esh.type.text']:
                sql_type['type'] = 'SHORTTEXT'
            else:
                sql_type['type'] = 'NVARCHAR'
            if not 'length' in cap_type:
                sql_type['length'] = 5000
        case 'cds.LargeString':
            if '@esh.type.text' in cap_type and cap_type['@esh.type.text']:
                sql_type['type'] = 'TEXT'
            else:
                sql_type['type'] = 'NCLOB'
        case 'cds.Varchar':
            sql_type['type'] = 'VARCHAR'
            if not 'length' in cap_type:
                sql_type['length'] = 5000
        case 'cds.Integer64':
            sql_type['type'] = 'BIGINT'
        case 'cds.Timestamp':
            sql_type['type'] = 'TIMESTAMP'
        case 'cds.Boolean':
            sql_type['type'] = 'BOOLEAN'
        case 'cds.Date':
            sql_type['type'] = 'DATE'
        case 'cds.Integer':
            sql_type['type'] = 'INTEGER'
        case 'cds.Decimal':
            sql_type['type'] = 'DECIMAL'
            if 'precision' in cap_type:
                sql_type['precision'] = cap_type['precision']
            if 'scale' in cap_type:
                sql_type['scale'] = cap_type['scale']
        case 'cds.Double':
            sql_type['type'] = 'DOUBLE'
        case 'cds.Time':
            sql_type['type'] = 'TIME'
        case 'cds.DateTime':
            sql_type['type'] = 'SECONDDATE'
        case 'cds.Timestamp':
            sql_type['type'] = 'TIMESTAMP'
        case 'cds.Binary':
            sql_type['type'] = 'VARBINARY'
            if 'length' in cap_type:
                sql_type['length'] = cap_type['length']
            #sql_type['isBinary'] = True
        case 'cds.LargeBinary':
            if '@esh.type.text' in cap_type and cap_type['@esh.type.text']:
                sql_type['type'] = 'BINTEXT'
            else:
                sql_type['type'] = 'BLOB'
            #sql_type['isBinary'] = True
        case 'cds.hana.BINARY':
            sql_type['type'] = 'BINARY'
            #sql_type['isBinary'] = True
        case 'cds.hana.VARCHAR':
            sql_type['type'] = 'VARCHAR'
            if not 'length' in cap_type:
                sql_type['length'] = 5000
        case 'cds.hana.SMALLINT':
            sql_type['type'] = 'SMALLINT'
        case 'cds.hana.TINYINT':
            sql_type['type'] = 'TINYINT'
        case 'cds.hana.SMALLDECIMAL':
            sql_type['type'] = 'SMALLDECIMAL'
        case 'cds.hana.REAL':
            sql_type['type'] = 'REAL'
        case 'cds.hana.CLOB':
            sql_type['type'] = 'CLOB'
        case 'cds.hana.CHAR':
            sql_type['type'] = 'CHAR'
        case 'cds.hana.NCHAR':
            sql_type['type'] = 'NCHAR'
        case 'cds.hana.ST_POINT':
            sql_type['type'] = 'ST_POINT'
            if 'srid' in cap_type:
                sql_type['srid'] = cap_type['srid']
            else:
                sql_type['srid'] = SPATIAL_DEFAULT_SRID
        case 'cds.hana.ST_GEOMETRY':
            sql_type['type'] = 'ST_GEOMETRY'
            if 'srid' in cap_type:
                sql_type['srid'] = cap_type['srid']
        case 'cds.Association':
            target_key_column = \
                cson['definitions'][cap_type['target']]['elements'][cson['definitions'][cap_type['target']]['pk']]
            sql_type = get_sql_type(table_name_mapping, cson, target_key_column, pk)
            rel = {}
            rel_to, _ = table_name_mapping.register([cap_type['target']], ENTITY_PREFIX)
            rel['table_name'] = rel_to
            rel['type'] = 'association'
            if 'cardinality' in cap_type:
                rel['cardinality'] = cap_type['cardinality']
            sql_type['rel'] = rel
        case _:
            t = cap_type['type']
            print(f'Unexpected type: {t}')
            raise ModelException(f'Unexpected cds type {t}')

    # Copy annotations
    annotations = {k:v for k,v in cap_type.items() if k.startswith('@')}
    if annotations:
        sql_type['annotations'] = annotations

    return sql_type


def find_definition(cson, type_definition):
    found = False
    while not found:
        if 'type' in type_definition and type_definition['type'] in cson['definitions']\
             and (('type' in cson['definitions'][type_definition['type']] \
                 and cson['definitions'][type_definition['type']]['type'] in cson['definitions']) \
                     or 'elements' in  cson['definitions'][type_definition['type']]):
            type_definition = cson['definitions'][type_definition['type']]
        else:
            found = True
    return type_definition

def get_key_columns(subtable_level, pk):
    d = pk.get_definition(subtable_level)
    if subtable_level == 0:
        res = (d[0], None, {d[0]: d[1]})
    elif subtable_level == 1:
        pk_name = d[0] + str(subtable_level)
        pk_parent_name = d[0]
        res = (pk_name, pk_parent_name, {pk_parent_name: d[1], pk_name: d[1]})
    else:
        pk_name = d[0] + str(subtable_level)
        pk_parent_name = d[0] + str(subtable_level - 1)
        res = (pk_name, pk_parent_name, {pk_parent_name: d[1], pk_name: d[1]})
    return res

def add_key_columns_to_table(table, subtable_level, pk):
    d = pk.get_definition(subtable_level)
    if subtable_level == 0:
        raise NotImplementedError
    elif subtable_level == 1:
        pk_name = d[0] + str(subtable_level)
        pk_parent_name = d[0]
        key_properties = {pk_parent_name: d[1], pk_name: d[1]}
    else:
        pk_name = d[0] + str(subtable_level)
        pk_parent_name = d[0] + str(subtable_level - 1)
        key_properties = {pk_parent_name: d[1], pk_name: d[1]}
    table['pk'] = pk_name
    table['pkParent'] = pk_parent_name
    table['columns'] = key_properties

def cson_entity_to_tables(table_name_mapping, cson, tables, path, type_name, type_definition,\
    subtable_level = 0, is_table = True, has_pc = False, pk = DefaultPK, parent_table_name = None,
    sur_table = None, sur_prop_name_mapping = None, sur_prop_path = [], entity = {}):
    ''' Transforms cson entity definition to model definition.
    The tables links the external object-oriented-view with internal HANA-database-view.'''
    external_path = path + [type_name]
    if sur_table:
        table = sur_table
        column_name_mapping = sur_prop_name_mapping
    else:
        table = {'external_path':external_path, 'level': subtable_level}
        column_name_mapping = NameMapping()
        if parent_table_name:
            table['parent'] = parent_table_name
        if subtable_level == 0:
            annotations = {k:v for k,v in type_definition.items() if k.startswith('@')}
            if annotations:
                table['annotations'] = annotations
        if is_table:
            if subtable_level == 0:
                pk_column_name, _ = column_name_mapping.register([type_definition['pk']])
                entity['elements'][type_definition['pk']] = {'column_name': pk_column_name}
                table['pk'] = pk_column_name
                table_name, table_map = table_name_mapping.register(external_path, ENTITY_PREFIX\
                    , definition = {'pk': pk_column_name})
                entity['table_name'] = table_name
                table['columns'] = {}
            else:
                table_name, table_map = table_name_mapping.register(external_path)
                entity['table_name'] = table_name
                add_key_columns_to_table(table, subtable_level, pk)
            table['table_name'] = table_name
            parent_table_name = table_name
        #if has_pc:
        #    table['columns'][PRIVACY_CATEGORY_COLUMN_DEFINITION[0]] = PRIVACY_CATEGORY_COLUMN_DEFINITION[1]
    #else:
    #    table = {'columns': {}}
    subtables = []
    type_definition = find_definition(cson, type_definition) # ToDo: check, if needed
    if type_definition['kind'] == 'entity' or (path and 'elements' in type_definition):
        for element_name_ext, element in type_definition['elements'].items():
            is_virtual = '@sap.esh.isVirtual' in element and element['@sap.esh.isVirtual']
            is_association = 'type' in element and element['type'] == 'cds.Association'
            entity['elements'][element_name_ext] = {}
            if is_virtual:
                if not is_association:
                    raise ModelException(f'{element_name_ext}: '
                    'Annotation @sap.esh.isVirtual is only allowed on associations')
                if subtable_level != 0:
                    raise ModelException(f'{element_name_ext}: '
                    'Annotation @sap.esh.isVirtual is only allowed on root level')
                referred_element = element['target']
                backward_rel = [k for k, v in cson['definitions'][referred_element]['elements'].items()\
                     if 'type' in v and v['type'] == 'cds.Association' and v['target'] == type_name]
                if len(backward_rel) != 1:
                    if not (isinstance(element['@sap.esh.isVirtual'], str) and element['@sap.esh.isVirtual'] in backward_rel):
                        raise ModelException(f'{element_name_ext}: Annotation @sap.esh.isVirtual must specify '
                        f'which backward association should be used from referred entity {referred_element}',)
                element['isVirtual'] = True
            if is_association:
                element['target_table_name'], _ = table_name_mapping.register([element['target']], ENTITY_PREFIX)
                element['target_pk'] = cson['definitions'][element['target']]['pk']
                element_name, _ = column_name_mapping.register(sur_prop_path + [element_name_ext], definition=element)
                entity['elements'][element_name_ext]['definition'] = element
            else:
                element_name, _ = column_name_mapping.register(sur_prop_path + [element_name_ext])
                
            element_needs_pc = PRIVACY_CATEGORY_ANNOTATION in element
            if 'items' in element or element_needs_pc: # collection (many keyword)
                if 'items' in element and 'elements' in element['items']: # nested definition
                    sub_type = element['items']
                    sub_type['kind'] = 'type'
                elif 'items' in element and element['items']['type'] in cson['definitions']:
                    sub_type = cson['definitions'][element['items']['type']]
                else: # built-in type
                    if 'items' in element:
                        sub_type = element['items']
                        sub_type['kind'] = 'type'
                    else:
                        sub_type = element
                        sub_type['kind'] = 'type'
                entity['elements'][element_name_ext]['items'] = {'elements': {}}
                subtable = cson_entity_to_tables(table_name_mapping, cson, tables, path +\
                    [type_name], element_name_ext, sub_type, subtable_level +  1, True\
                    , element_needs_pc, parent_table_name = parent_table_name
                    , entity= entity['elements'][element_name_ext]['items'])
                subtables.append(subtable)
                table['columns'][element_name] = {'rel': {'table_name':subtable['table_name'],\
                    'type':'containment'}, 'external_path': sur_prop_path + [element_name_ext], 'isVirtual': True}
            elif 'type' in element:
                if element['type'] in cson['definitions']:
                    if 'elements' in cson['definitions'][element['type']]:
                        entity['elements'][element_name_ext]['elements'] = {}
                        _ = cson_entity_to_tables(table_name_mapping, cson, tables, path + [type_name],\
                            element_name_ext, element, subtable_level, False, parent_table_name = parent_table_name, 
                            sur_table=table, sur_prop_name_mapping=column_name_mapping,
                            sur_prop_path=sur_prop_path + [element_name_ext],
                            entity=entity['elements'][element_name_ext])
                    else:
                        table['columns'][element_name] =\
                            get_sql_type(table_name_mapping, cson, cson['definitions'][element['type']], pk)
                        table['columns'][element_name]['external_path'] = sur_prop_path + [element_name_ext]
                        entity['elements'][element_name_ext]['column_name'] = element_name
                else:
                    table['columns'][element_name] = get_sql_type(table_name_mapping, cson, element, pk)
                    table['columns'][element_name]['external_path'] = sur_prop_path + [element_name_ext]
                    entity['elements'][element_name_ext]['column_name'] = element_name
            elif 'elements' in element: # nested definition
                element['kind'] = 'type'
                entity['elements'][element_name_ext]['elements'] = {}
                _ = cson_entity_to_tables(table_name_mapping, cson, tables, path + [type_name],\
                    element_name_ext, element, subtable_level, False, parent_table_name = parent_table_name,
                    sur_table=table, 
                    sur_prop_name_mapping=column_name_mapping,
                    sur_prop_path=sur_prop_path + [element_name_ext],
                    entity=entity['elements'][element_name_ext])
            else:
                raise NotImplementedError
    elif path and type_definition['kind'] == 'type': # single column for one table
        entity['table_name'] = table_name
        entity['column_name'] = '_VALUE'
        if not type_definition['type'] in cson['definitions']:
            table['columns']['_VALUE'] = get_sql_type(table_name_mapping, cson, type_definition, pk)
        #elif '@EnterpriseSearchIndex.type' in cson['definitions'][type_definition['type']] and\
        #    cson['definitions'][type_definition['type']]['@EnterpriseSearchIndex.type'] == 'CodeList':
            # this is for codelist TODO, change this harcoded value
        #    table['columns']["_VALUE"] = {'type': "NVARCHAR", 'length': 50}
        else:
            # print("----- {}={}".format(path, type_definition['type']))
            # print(cson['definitions'][type_definition['type']])
            #found = False
            #while not found:
            #    if 'type' in type_definition and type_definition['type'] in cson['definitions'] and 'type' in\
            #        cson['definitions'][type_definition['type']] and \
            #            cson['definitions'][type_definition['type']]['type'] in cson['definitions']:
            #        type_definition = cson['definitions'][type_definition['type']]
            #    else:
            #        found = True
            # HERE type_definition = find_definition(cson, type_definition)
            # if 'elements' in cson['definitions'][type_definition['type']]:
            if 'elements' in type_definition:
                for key, value in type_definition['elements'].items():
                    # print("KEY: {}, value: {}, find_definition".format(key, value),find_definition(value) )
                    table['columns'][key] = get_sql_type(table_name_mapping, cson, find_definition(cson, value), pk)
            else:
                table['columns']['_VALUE'] = get_sql_type(table_name_mapping, cson, type_definition, pk)
            #table['columns']['ONE'] = 2
    else:
        raise NotImplementedError

    if subtables:
        table['contains'] = [w['table_name'] for w in subtables]
    if is_table:
        if 'contains' in column_name_mapping.ext_tree:
            table_map['columns'] = column_name_mapping.ext_tree['contains']
        else:
            table_map['columns'] = {}
        tables[table_name] = table
    return table


def is_many_rel(column_rel):
    return 'cardinality' in column_rel\
        and 'max' in column_rel['cardinality'] and column_rel['cardinality']['max'] == '*'

def cson_to_mapping(cson, pk = DefaultPK):
    tables = {}
    entities = {}
    table_name_mapping = NameMapping()
    for cson_def_name, cson_def in cson['definitions'].items():
        if cson_def['kind'] == 'entity':
            keys = [k for k, v in cson_def['elements'].items() if 'key' in v and v['key']]
            if len(keys) != 1:
                raise ModelException(f'{cson_def_name}: An entity must have exactly one key property')
            cson_def['pk'] = keys[0]
    for cson_def_name, cson_def in cson['definitions'].items():
        if cson_def['kind'] == 'entity':
            entity = {'elements':{}}
            cson_entity_to_tables(table_name_mapping, cson, tables, [], cson_def_name, cson_def, pk = pk, entity = entity)
            entities[cson_def_name] = entity


    for table_name, table in tables.items():
        for column_name, column in table['columns'].items():
            is_virtual = 'annotations' in column and '@sap.esh.isVirtual' in column['annotations'] and \
                column['annotations']['@sap.esh.isVirtual']
            is_association = 'rel' in column and column['rel']['type'] == 'association'
            if is_virtual:
                if not is_association:
                    raise ModelException(f'{column_name}: Annotation @sap.esh.isVirtual is only allowed on associations')
                if table['level'] != 0:
                    raise ModelException(f'{column_name}: Annotation @sap.esh.isVirtual is only allowed on root level')
                referred_table = tables[column['rel']['table_name']]
                backward_rel = [(k, r, is_many_rel(r['rel'])) for k, r in referred_table['columns'].items() \
                    if 'rel' in r and r['rel']['table_name'] == table_name]
                if len(backward_rel) == 1:
                    column['rel']['column_name'] = backward_rel[0][0]
                else:
                    external_path = None
                    if isinstance(column['annotations']['@sap.esh.isVirtual'], list):
                        external_path = column['annotations']['@sap.esh.isVirtual']
                    elif isinstance(column['annotations']['@sap.esh.isVirtual'], str):
                        external_path = [column['annotations']['@sap.esh.isVirtual']]
                    rel_column_name = []
                    if external_path:
                        rel_column_name = [k for k,v,_ in backward_rel if v['external_path'] == external_path]
                    if len(rel_column_name) == 1:
                        column['rel']['column_name'] = rel_column_name[0]
                    else:
                        msg = ( f'{column_name}: Annotation @sap.esh.isVirtual must specify '
                        'which backward association should be used from referred entity ')
                        msg += referred_table['externalPath'][0]
                        raise ModelException(msg)
                column['isVirtual'] = True

        table['sql'] = {}
        nl = table['level']
        select_columns = []
        for k, v in table['columns'].items():
            if ('isVirtual' in v and v['isVirtual']):
                continue
            prefix = f'L{nl}.' if nl > 1 else ''
            suffix = '.ST_AsGeoJSON()' if v['type'] in TYPES_SPATIAL else ''
            select_columns.append(f'{prefix}"{k}"{suffix}')
        if nl <= 1:
            if nl == 0:
                key_column = table['pk']
            else:
                key_column = table['pkParent']
            sql_table_joins = f'"{{schema_name}}"."{table_name}"'
            sql_condition = f'"{key_column}" in ({{id_list}})'
            table['sql']['delete'] = f'DELETE from {sql_table_joins} where {sql_condition}'
        else:
            joins = []
            del_subselect = []
            parents = get_parents(tables, table, table['level'] - 1)
            for i, parent in enumerate(parents):
                joins.append(f'inner join "{{schema_name}}"."{parent}" L{i+1} on L{i+2}._ID{i+1} = L{i+1}._ID{i+1}')
                if i == len(parents) - 1:
                    del_subselect.append(f'select _ID{i+1} from "{{schema_name}}"."{parent}" L{i+1}')
                else:
                    del_subselect.append(f'inner join "{{schema_name}}"."{parent}" L{i+1} on L{i+2}._ID{i+1} = L{i+1}._ID{i+1}')
            joins.reverse()
            del_subselect.reverse()
            del_subselect.append('where L1."_ID" in ({id_list})')
            del_subselect_str = ' '.join(del_subselect)
            sql_table_joins = f'"{{schema_name}}"."{table_name}" L{nl} {" ".join(joins)}'
            sql_condition = f'L1."_ID" in ({{id_list}})'
            table['sql']['delete'] = f'DELETE from "{{schema_name}}"."{table_name}" where _ID{len(parents)} in ({del_subselect_str})'
        table['sql']['select'] = f'SELECT {", ".join(select_columns)} from {sql_table_joins} where {sql_condition}'
    return {'tables': tables, 'entities': entities}

def get_parents(tables, table, steps):
    if not 'parent' in table:
        return []
    parent = table['parent']
    if steps == 1:
        return [parent]
    else:
        return get_parents(tables, tables[parent], steps - 1) + [parent]

def value_ext_to_int(typ, value):
    if typ in TYPES_B64_DECODE:
        return base64.decodebytes(value.encode('utf-8'))
    elif typ in TYPES_SPATIAL:
        return json.dumps(value)
    return value


def array_to_dml(mapping, inserts, objects, subtable_level, parent_object_id, pk, entity):
    full_table_name = entity['table_name']
    if not full_table_name in inserts:
        _, _, key_columns = get_key_columns(subtable_level, pk)
        key_col_names = {k:idx for idx, k in enumerate(key_columns.keys())}
        inserts[full_table_name] = {'columns': key_col_names, 'rows':[]}
        inserts[full_table_name]['columns']['_VALUE'] = 2
    for obj in objects:
        row = []
        row.append(parent_object_id)
        object_id = pk.get_pk(full_table_name, subtable_level)
        row.append(object_id)
        row.append(value_ext_to_int(\
            mapping['tables'][full_table_name]['columns']['_VALUE']['type'], obj))
        inserts[full_table_name]['rows'].append(row)



def object_to_dml(mapping, inserts, objects, idmapping, subtable_level = 0, col_prefix = [],\
    parent_object_id = None, propagated_row = None, propagated_object_id = None, pk = DefaultPK
    , entity = {}, parent_table_name = ''):
    if 'table_name' in entity:
        full_table_name = entity['table_name']
    else:
        full_table_name = parent_table_name
    for obj in objects:
        if subtable_level == 0 and 'id' in obj:
            raise DataException('id is a reserved property name')
        if propagated_row is None:
            row = []
            if parent_object_id:
                row.append(parent_object_id)
            #object_id = pk.get_pk(full_table_name, subtable_level)
            if subtable_level == 0:
                object_id = None
                if 'source' in obj:
                    if len(obj['source']) != 1:
                        raise NotImplementedError
                    for source in obj['source']:
                        hashable_key = json.dumps(source)
                        if hashable_key in idmapping:
                            object_id = idmapping[hashable_key]['id']
                            idmapping[hashable_key]['resolved'] = True
                        else:
                            object_id = pk.get_pk(full_table_name, subtable_level)
                            idmapping[hashable_key] = {'id':object_id, 'resolved':True}
                if mapping['tables'][full_table_name]['pk'] == 'ID':
                    if not object_id:
                        object_id = pk.get_pk(full_table_name, subtable_level)
                    obj['id'] = object_id
            else:
                object_id = pk.get_pk(full_table_name, subtable_level)
                row.append(object_id)
                if not full_table_name in inserts:
                    _, _, key_columns = get_key_columns(subtable_level, pk)
                    key_col_names = {k:idx for idx, k in enumerate(key_columns.keys())}
                    inserts[full_table_name] = {'columns': key_col_names, 'rows':[]}
            if not full_table_name in inserts:
                inserts[full_table_name] = {'columns': {}, 'rows':[]}
            else:
                row.extend([None]*(len(inserts[full_table_name]['columns']) - len(row)))
        else:
            row = propagated_row
            object_id = propagated_object_id

        for k, v in obj.items():
            value = None
            if k in entity['elements']:
                prop = entity['elements'][k]
                if 'definition' in prop and 'type' in prop['definition']\
                    and prop['definition']['type'] == 'cds.Association':
                    if 'isVirtual' in prop['definition'] and prop['definition']['isVirtual']:
                        raise DataException(f'Data must not be provided for virtual property {k}')
                    if prop['definition']['target_pk'] in v:
                        value = v[prop['definition']['target_pk']]
                    elif 'source' in v:
                        if isinstance(v['source'], list):
                            hashable_keys = set([json.dumps(w) for w in v['source']])
                            if len(hashable_keys) == 0:
                                raise DataException(f'Association property {k} has no source')
                            elif len(hashable_keys) > 1:
                                raise DataException(f'Association property {k} has conflicting sources')
                            hashable_key = list(hashable_keys)[0]
                            if hashable_key in idmapping:
                                value = idmapping[hashable_key]['id']
                            else:
                                target_table_name = prop['definition']['target_table_name']
                                value = pk.get_pk(target_table_name, 0)
                                idmapping[hashable_key] = {'id':value, 'resolved':False}
                        else:
                            raise DataException(f'Association property {k} is not a list')
                    else:
                        raise DataException(f'Association property {k} has no source property')
            else:
                raise DataException(f'Unknown property {k}')
            
            
            if value is None and isinstance(v, list):
                if not 'items' in entity['elements'][k]:
                    raise DataException(f'{k} is not an array property')
                if entity['elements'][k]['items']['elements']:
                    object_to_dml(mapping, inserts, v, idmapping, subtable_level + 1,\
                        parent_object_id = object_id, pk = pk, 
                        entity=entity['elements'][k]['items'], parent_table_name=full_table_name)
                else:
                    array_to_dml(mapping, inserts, v, subtable_level + 1, object_id, pk
                    , entity['elements'][k]['items'])
            elif value is None and isinstance(v, dict) and (not 'column_name' in entity['elements'][k] or not \
                mapping['tables'][full_table_name]['columns'][entity['elements'][k]['column_name']]['type'] in TYPES_SPATIAL):
                object_to_dml(mapping, inserts, [v], idmapping, subtable_level, col_prefix + [k],\
                    propagated_row = row, propagated_object_id=object_id, pk = pk, 
                    entity=entity['elements'][k], parent_table_name=full_table_name)
            else:
                column_name = entity['elements'][k]['column_name']
                if not value:
                    value = value_ext_to_int(\
                        mapping['tables'][full_table_name]['columns'][column_name]['type'], v)
                if not column_name in inserts[full_table_name]['columns']:
                    inserts[full_table_name]['columns'][column_name] = len(inserts[full_table_name]['columns'])
                    row.append(value)
                else:
                    row[inserts[full_table_name]['columns'][column_name]] = value
        if row and not propagated_row and full_table_name in inserts:
            inserts[full_table_name]['rows'].append(row)


def objects_to_dml(mapping, objects, pk = DefaultPK):
    inserts = {}
    idmapping = {}
    for object_type, objects in objects.items():
        if not object_type in mapping['entities']:
            raise DataException(f'Unknown object type {object_type}')
        object_to_dml(mapping, inserts, objects, idmapping, pk = pk,
            entity=mapping['entities'][object_type])
    if idmapping:
        dangling = [json.loads(k) for k, v in idmapping.items() if not v['resolved']]
        if dangling:
            # ToDo: Handle references to objects which are not in one data package
            raise DataException('References to objects outside of one data package '
            f'is not yet supported. No object exists with source {json.dumps(dangling)}')
    for v in inserts.values():
        length = len(v['columns'])
        for row in v['rows']:
            if len(row) < length:
                row.extend([None]*(length - len(row)))

    return {'inserts': inserts}
