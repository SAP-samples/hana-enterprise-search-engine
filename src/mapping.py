"""Mapping between external objects and internal tables using 'nodes' as internal runtime-format """
from uuid import uuid1
from name_mapping import NameMapping
import json

ENTITY_PREFIX = 'ENTITY/'
VIEW_PREFIX = 'VIEW/'
PRIVACY_CATEGORY_COLUMN_DEFINITION = ('_PRIVACY_CATEGORY', {'type':'TINY'})
PRIVACY_CATEGORY_ANNOTATION = '@EnterpriseSearchIndex.privacyCategory'

class DefaultPK:
    @staticmethod
    def get_pk(node_name, subnode_level):
        #pylint: disable=unused-argument
        return uuid1().urn[9:]
    @staticmethod
    def get_definition(subnode_level):
        #pylint: disable=unused-argument
        return ('_ID', {'type':'VARCHAR', 'length': 36, 'isIdColumn': True})

class ModelException(Exception):
    pass

class DataException(Exception):
    pass


def get_sql_type(node_name_mapping, cson, cap_type, pk):
    ''' get SQL type from CAP type'''
    if cap_type['type'] in cson['definitions'] and 'type' in cson['definitions'][cap_type['type']]:
        return get_sql_type(node_name_mapping, cson, cson['definitions'][cap_type['type']], pk)

    sql_type = {}
    if 'length' in cap_type:
        sql_type['length'] = cap_type['length']
    match cap_type['type']:
        case 'cds.UUID':
            sql_type['type'] = 'NVARCHAR'
            sql_type['length'] = 36
        case 'cds.String':
            sql_type['type'] = 'NVARCHAR'
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
        case 'cds.Time':
            sql_type['type'] = 'TIME'
        case 'cds.DateTime':
            sql_type['type'] = 'DATETIME'
        case 'cds.Association':
            target_key_property = cson['definitions'][cap_type['target']]['elements'][cson['definitions'][cap_type['target']]['pk']]
            sql_type = get_sql_type(node_name_mapping, cson, target_key_property, pk)
            rel = {}
            rel_to, _ = node_name_mapping.register([cap_type['target']], ENTITY_PREFIX)
            rel['table_name'] = rel_to
            rel['type'] = 'association'
            if 'cardinality' in cap_type:
                rel['cardinality'] = cap_type['cardinality']
            sql_type['rel'] = rel
        case _:
            if cap_type['type'].startswith(cson['namespace']):
                rep_type = find_definition(cson, cap_type)
                print(rep_type)
                sql_type['type'] = get_sql_type(node_name_mapping, cson, cson['definitions'][rep_type['type']], pk)
            else:
                None #pylint: disable=pointless-statement
            print(f'Unexpected type: {cap_type["type"]}')
            raise ModelException('Unexpected cds type %s', cap_type["type"])

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

def get_key_columns(subnode_level, pk):
    d = pk.get_definition(subnode_level)
    if subnode_level == 0:
        res = (d[0], None, {d[0]: d[1]})
    elif subnode_level == 1:
        pk_name = d[0] + str(subnode_level)
        pk_parent_name = d[0]
        res = (pk_name, pk_parent_name, {pk_parent_name: d[1], pk_name: d[1]})
    else:
        pk_name = d[0] + str(subnode_level)
        pk_parent_name = d[0] + str(subnode_level - 1)
        res = (pk_name, pk_parent_name, {pk_parent_name: d[1], pk_name: d[1]})
    return res

def add_key_columns_to_node(node, subnode_level, pk):
    d = pk.get_definition(subnode_level)
    if subnode_level == 0:
        raise NotImplementedError
    elif subnode_level == 1:
        pk_name = d[0] + str(subnode_level)
        pk_parent_name = d[0]
        key_properties = {pk_parent_name: d[1], pk_name: d[1]}
    else:
        pk_name = d[0] + str(subnode_level)
        pk_parent_name = d[0] + str(subnode_level - 1)
        key_properties = {pk_parent_name: d[1], pk_name: d[1]}
    node['pk'] = pk_name
    node['pkParent'] = pk_parent_name
    node['properties'] = key_properties



def cson_entity_to_subnodes(element_name_ext, element, node, property_name_mapping,
    node_name_mapping, cson, nodes, path, type_name, subnode_level):
    subnode = cson_entity_to_nodes(node_name_mapping, cson, nodes, path + [type_name],\
        element_name_ext, element, subnode_level +  1, False)
    for column in subnode['properties'].values():
        if 'external_path' in column:
            property_name_int, _ =\
                property_name_mapping.register([element_name_ext] + column['external_path'])
        else:
            property_name_int, _ = property_name_mapping.register([element_name_ext])
        node['properties'][property_name_int] = column
        node['properties'][property_name_int]['external_path'] =\
            [element_name_ext] + column['external_path']


def cson_entity_to_nodes(node_name_mapping, cson, nodes, path, type_name, type_definition,\
    subnode_level = 0, is_table = True, has_pc = False, pk = DefaultPK):
    ''' Transforms cson entity definition to model definition.
    The nodes links the external object-oriented-view with internal HANA-database-view.'''
    external_path = path + [type_name]
    node = {'external_path':external_path, 'level': subnode_level}
    property_name_mapping = NameMapping()
    if subnode_level == 0:
        annotations = {k:v for k,v in type_definition.items() if k.startswith('@')}
        if annotations:
            node['annotations'] = annotations
    if is_table:
        if subnode_level == 0:
            pk_property_name, _ = property_name_mapping.register([type_definition['pk']])
            node['pk'] = pk_property_name
            table_name, node_map = node_name_mapping.register(external_path, ENTITY_PREFIX\
                , definition = {'pk': pk_property_name})
            node['properties'] = {}
        else:
            table_name, node_map = node_name_mapping.register(external_path)
            add_key_columns_to_node(node, subnode_level, pk)
            '''
            pk_name, key_columns = get_key_columns(subnode_level, pk)
            node['pk'] = pk_name
            node['pkParent'] = pk_parent_name
            node['properties'] = key_columns
            '''
        node['table_name'] = table_name
        #if has_pc:
        #    node['properties'][PRIVACY_CATEGORY_COLUMN_DEFINITION[0]] = PRIVACY_CATEGORY_COLUMN_DEFINITION[1]
    else:
        node = {'properties': {}}
    subnodes = []
    type_definition = find_definition(cson, type_definition) # ToDo: check, if needed
    if type_definition['kind'] == 'entity' or (path and 'elements' in type_definition):
        for element_name_ext, element in type_definition['elements'].items():
            is_virtual = '@sap.esh.isVirtual' in element and element['@sap.esh.isVirtual']
            is_association = 'type' in element and element['type'] == 'cds.Association'
            if is_virtual:
                if not is_association:
                    raise ModelException(f'{element_name_ext}: '
                    'Annotation @sap.esh.isVirtual is only allowed on associations')
                if subnode_level != 0:
                    raise ModelException(f'{element_name_ext}: '
                    'Annotation @sap.esh.isVirtual is only allowed on root level')
                referred_element = element['target']
                backward_rel = [k for k, v in cson['definitions'][referred_element]['elements'].items()\
                     if 'type' in v and v['type'] == 'cds.Association' and v['target'] == type_name]
                if len(backward_rel) != 1:
                    raise ModelException(f'{element_name_ext}: Annotation @sap.esh.isVirtual is only allowed if '
                    f'exactly one backward association exists from referred entity {referred_element}',)
                element['isVirtual'] = True

            if is_association:
                element['target_table_name'], _ = node_name_mapping.register([element['target']], ENTITY_PREFIX)
                element['target_pk'] = cson['definitions'][element['target']]['pk']
                element_name, _ = property_name_mapping.register([element_name_ext], definition=element)
            else:
                element_name, _ = property_name_mapping.register([element_name_ext])
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
                subnode = cson_entity_to_nodes(node_name_mapping, cson, nodes, path +\
                    [type_name], element_name_ext, sub_type, subnode_level +  1, True, element_needs_pc)
                subnodes.append(subnode)
                node['properties'][element_name] = {'rel': {'table_name':subnode['table_name'],\
                    'type':'containment'}, 'external_path': [element_name_ext], 'isVirtual': True}
            elif 'type' in element:
                if element['type'] in cson['definitions']:
                    if 'elements' in cson['definitions'][element['type']]:
                        cson_entity_to_subnodes(element_name_ext, element, node, property_name_mapping,
                            node_name_mapping, cson, nodes, path, type_name, subnode_level)
                    else:
                        node['properties'][element_name] =\
                            get_sql_type(node_name_mapping, cson, cson['definitions'][element['type']], pk)
                        node['properties'][element_name]['external_path'] = [element_name_ext]
                else:
                    node['properties'][element_name] = get_sql_type(node_name_mapping, cson, element, pk)
                    node['properties'][element_name]['external_path'] = [element_name_ext]
            elif 'elements' in element: # nested definition
                element['kind'] = 'type'
                cson_entity_to_subnodes(element_name_ext, element, node, property_name_mapping,
                    node_name_mapping, cson, nodes, path, type_name, subnode_level)
            else:
                raise NotImplementedError

    elif path and type_definition['kind'] == 'type': # single property for one node
        if not type_definition['type'] in cson['definitions']:
            node['properties']['_VALUE'] = get_sql_type(node_name_mapping, cson, type_definition, pk)
        #elif '@EnterpriseSearchIndex.type' in cson['definitions'][type_definition['type']] and\
        #    cson['definitions'][type_definition['type']]['@EnterpriseSearchIndex.type'] == 'CodeList':
            # this is for codelist TODO, change this harcoded value
        #    node['properties']["_VALUE"] = {'type': "NVARCHAR", 'length': 50}
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
                    node['properties'][key] = get_sql_type(node_name_mapping, cson, find_definition(cson, value), pk)
            else:
                node['properties']['_VALUE'] = get_sql_type(node_name_mapping, cson, type_definition, pk)
            #node['properties']['ONE'] = 2
    else:
        raise NotImplementedError

    if subnodes:
        node['contains'] = [w['table_name'] for w in subnodes]
    if is_table:
        if 'contains' in property_name_mapping.ext_tree:
            node_map['properties'] = property_name_mapping.ext_tree['contains']
        else:
            node_map['properties'] = {}
        nodes[table_name] = node

    return node

def is_many_rel(property_rel):
    return 'cardinality' in property_rel\
        and 'max' in property_rel['cardinality'] and property_rel['cardinality']['max'] == '*'

def cson_to_nodes(cson, pk = DefaultPK):
    nodes = {}
    node_name_mapping = NameMapping()
    for name, definition in cson['definitions'].items():
        if definition['kind'] == 'entity':
            keys = [k for k, v in definition['elements'].items() if 'key' in v and v['key']]
            if len(keys) != 1:
                raise ModelException(f'{name}: An entity must have exactly one key property')
            definition['pk'] = keys[0]
    for name, definition in cson['definitions'].items():
        if definition['kind'] == 'entity':
            cson_entity_to_nodes(node_name_mapping, cson, nodes, [], name, definition, pk = pk)


    for node_name, node in nodes.items():
        for prop_name, prop in node['properties'].items():
            is_virtual = 'annotations' in prop and '@sap.esh.isVirtual' in prop['annotations'] and \
                prop['annotations']['@sap.esh.isVirtual']
            is_association = 'rel' in prop and prop['rel']['type'] == 'association'
            if is_virtual:
                if not is_association:
                    raise ModelException(f'{prop_name}: Annotation @sap.esh.isVirtual is only allowed on associations')
                if node['level'] != 0:
                    raise ModelException(f'{prop_name}: Annotation @sap.esh.isVirtual is only allowed on root level')
                referred_node = nodes[prop['rel']['table_name']]
                backward_rel = [(r, is_many_rel(r['rel'])) for r in referred_node['properties'].values() \
                    if 'rel' in r and r['rel']['table_name'] == node_name]
                if len(backward_rel) != 1:
                    msg = ( f'{prop_name}: Annotation @sap.esh.isVirtual is only '
                    'allowed if exactly one backward association exists from referred entity ')
                    msg += referred_node['externalPath'][0]
                    raise ModelException(msg)
                prop['isVirtual'] = True

    return {'nodes': nodes, 'index': node_name_mapping.ext_tree['contains']}

def get_column_name(nodes_index, exp_path):
    if len(exp_path) > 1:
        if not 'contains' in nodes_index[exp_path[0]]:
            raise DataException(f'Unknown property {exp_path[1]}')
        next_nodes_index = nodes_index[exp_path[0]]['contains']
        return get_column_name(next_nodes_index, exp_path[1:])
    if not exp_path[0] in nodes_index:
        raise DataException(f'Unknown property {exp_path[0]}')
    return nodes_index[exp_path[0]]['int']


def object_to_dml(nodes, inserts, nodes_index, objects, idmapping, subnode_level = 0, col_prefix = [],\
    parent_object_id = None, propagated_row = None, propagated_object_id = None, pk = DefaultPK, properties = {}):
    for obj in objects:
        if subnode_level == 0 and 'id' in obj:
            raise DataException('Reserved property name ########## id')
        full_table_name = nodes_index['int']
        if propagated_row:
            row = propagated_row
            object_id = propagated_object_id
        else:
            row = []
            if parent_object_id:
                row.append(parent_object_id)
            object_id = pk.get_pk(full_table_name, subnode_level)
            if subnode_level == 0:
                if nodes_index['definition']['pk'] == 'ID':
                    obj['id'] = object_id
                if 'source' in obj:
                    for source in obj['source']:
                        hashable_key = json.dumps(source)
                        if hashable_key in idmapping:
                            idmapping[hashable_key]['resolved'] = True
                        else:
                            idmapping[hashable_key] = {'id':object_id, 'resolved':True}
            else:
                row.append(object_id)
                if not full_table_name in inserts:
                    _, _, key_columns = get_key_columns(subnode_level, pk)
                    key_col_names = {k:idx for idx, k in enumerate(key_columns.keys())}
                    inserts[full_table_name] = {'columns': key_col_names, 'rows':[]}
            if not full_table_name in inserts:
                inserts[full_table_name] = {'columns': {}, 'rows':[]}
            else:
                row.extend([None]*(len(inserts[full_table_name]['columns']) - len(row)))
        for k, v in obj.items():
            value = None
            if k in properties:
                prop = properties[k]
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
            if value == None and isinstance(v, list):
                object_to_dml(nodes, inserts, nodes_index['contains'][k], v, idmapping, subnode_level + 1,\
                    parent_object_id = object_id, pk = pk, properties=nodes_index['contains'][k]['properties'])
            elif value == None and isinstance(v, dict):
                object_to_dml(nodes, inserts, nodes_index, [v], idmapping, subnode_level, col_prefix + [k],\
                    propagated_row = row, propagated_object_id=object_id, pk = pk, properties = properties[k]['contains'])
            else:
                column_name = get_column_name(nodes_index['properties'], col_prefix + [k])
                if not value:
                    value = v
                if not column_name in inserts[full_table_name]['columns']:
                    inserts[full_table_name]['columns'][column_name] = len(inserts[full_table_name]['columns'])
                    row.append(value)
                else:
                    row[inserts[full_table_name]['columns'][column_name]] = value
        if not propagated_row:
            inserts[full_table_name]['rows'].append(row)


def objects_to_dml(nodes, objects, pk = DefaultPK):
    inserts = {}
    idmapping = {}
    for object_type, objects in objects.items():
        if not object_type in nodes['index']:
            raise DataException(f'Unknown object type {object_type}')
        ni = nodes['index'][object_type]
        object_to_dml(nodes, inserts, ni, objects, idmapping, pk = pk, properties= ni['properties'])
    if idmapping:
        dangling = [json.loads(k) for k, v in idmapping.items() if not v['resolved']]
        if dangling:
            # ToDo: Handle references to objects which are not in one data package
            raise DataException('References to objects outside of one data package '
            f'is not yet supported. No object exists with source {json.dumps(dangling)}')
    return {'inserts': inserts}
