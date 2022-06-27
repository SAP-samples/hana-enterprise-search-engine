"""Mapping between external objects and internal tables using 'nodes' as internal runtime-format """
from copy import deepcopy
from uuid import uuid1
from name_mapping import NameMapping

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
        return ('_ID', {'type':'VARCHAR', 'length': 36})

def get_sql_type(node_name_mapping, cson, cap_type, pk):
    ''' get SQL type from CAP type'''
    # print("<<<<<<<<<<<< {}".format(cap_type))
    if cap_type['type'] in cson['definitions'] and 'type' in cson['definitions'][cap_type['type']]:
        return get_sql_type(node_name_mapping, cson, cson['definitions'][cap_type['type']], pk)

    sql_type = {}
    if 'length' in cap_type:
        sql_type['length'] = cap_type['length']
    match cap_type['type']:
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
            sql_type['precision'] = cap_type['precision']
            sql_type['scale'] = cap_type['scale']
        case 'cds.Association':
            for k, v in pk.get_definition(0)[1].items():
                sql_type[k] = v
            rel = {}
            rel_to, _ = node_name_mapping.register([cap_type['target']], ENTITY_PREFIX)
            rel['table_name'] = rel_to
            rel['type'] = 'association'
            if 'cardinality' in cap_type:
                rel['cardinality'] = cap_type['cardinality']
            sql_type['rel'] = rel
        case _:
            if cap_type['type'].startswith(cson['namespace']):
                # print("******* {}".format(cap_type['type']))
                #print(get_sql_type(cson['definitions'][cap_type['type']]))
                rep_type = find_definition(cson, cap_type)
                print(rep_type)
                sql_type['type'] = get_sql_type(node_name_mapping, cson, cson['definitions'][rep_type['type']], pk)
            else:
                None #pylint: disable=pointless-statement
            print(f'Unexpected type: {cap_type["type"]}')
            raise NotImplementedError

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
        res = (d[0], {d[0]: d[1]})
    elif subnode_level == 1:
        pk_name = d[0] + str(subnode_level)
        res = (pk_name, {d[0]: d[1], pk_name: d[1]})
    else:
        pk_name = d[0] + str(subnode_level)
        res = (pk_name, {d[0] + str(subnode_level - 1): d[1], d[0] + str(subnode_level): d[1]})
    return res


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
    if subnode_level == 0:
        annotations = {k:v for k,v in type_definition.items() if k.startswith('@')}
        if annotations:
            node['annotations'] = annotations
    if is_table:
        if subnode_level == 0:
            table_name, node_map = node_name_mapping.register(external_path, ENTITY_PREFIX)
        else:
            table_name, node_map = node_name_mapping.register(external_path)
        node['table_name'] = table_name
        pk_name, key_columns = get_key_columns(subnode_level, pk)
        node['pk'] = pk_name
        node['properties'] = key_columns
        if has_pc:
            node['properties'][PRIVACY_CATEGORY_COLUMN_DEFINITION[0]] = PRIVACY_CATEGORY_COLUMN_DEFINITION[1]
    else:
        node = {'properties': {}}
    subnodes = []
    type_definition = find_definition(cson, type_definition)
    property_name_mapping = NameMapping()
    if type_definition['kind'] == 'entity' or (path and 'elements' in type_definition):
        for element_name_ext, element in type_definition['elements'].items():
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
                    'type':'containment'}, 'external_path': [element_name_ext]}
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
        node_map['properties'] = property_name_mapping.ext_tree['contains']
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
            cson_entity_to_nodes(node_name_mapping, cson, nodes, [], name, definition, pk = pk)

    # analyze associations
    for node_name, node in nodes.items():
        for _, prop in node['properties'].items():
            if 'rel' in prop and prop['rel']['type'] == 'association' and is_many_rel(prop['rel']):
                referred_node = nodes[prop['rel']['table_name']]
                backward_rel = [(r, is_many_rel(r['rel'])) for r in referred_node['properties'].values() \
                    if 'rel' in r and r['rel']['table_name'] == node_name]
                if [1 for r, is_many in backward_rel if not is_many]:
                    prop['rel']['hidden'] = True
                elif [1 for r, is_many in backward_rel if is_many]:
                    raise NotImplementedError
    return {'nodes': nodes, 'index': node_name_mapping.ext_tree['contains']}

def get_column_name(nodes_index, exp_path):
    if len(exp_path) > 1:
        next_nodes_index = nodes_index[exp_path[0]]['contains']
        return get_column_name(next_nodes_index, exp_path[1:])
    return nodes_index[exp_path[0]]['int']


def object_to_dml(nodes, inserts, nodes_index, objects, subnode_level = 0, col_prefix = [],\
    parent_object_id = None, propagated_row = None, propagated_object_id = None, pk = DefaultPK):
    for obj in objects:
        full_table_name = nodes_index['int']
        if propagated_row:
            row = propagated_row
            object_id = propagated_object_id
        else:
            row = []
            if parent_object_id:
                row.append(parent_object_id)
            object_id = pk.get_pk(full_table_name, subnode_level)
            row.append(object_id)
            if not full_table_name in inserts:
                _, key_columns = get_key_columns(subnode_level, pk)
                key_col_names = {k:idx for idx, k in enumerate(key_columns.keys())}
                inserts[full_table_name] = {'columns': key_col_names, 'rows':[]}
            row.extend([None]*(len(inserts[full_table_name]['columns']) - len(row)))
        for k, v in obj.items():
            column_name = get_column_name(nodes_index['properties'], col_prefix + [k])
            if isinstance(v, list):
                object_to_dml(nodes, inserts, nodes_index['contains'][k], v, subnode_level + 1,\
                    parent_object_id = object_id, pk = pk)
            elif isinstance(v, dict):
                object_to_dml(nodes, inserts, nodes_index, [v], subnode_level, col_prefix + [k],\
                    propagated_row = row, propagated_object_id=object_id, pk = pk)
            else:
                if not column_name in inserts[full_table_name]['columns']:
                    inserts[full_table_name]['columns'][column_name] = len(inserts[full_table_name]['columns'])
                    row.append(v)
                else:
                    row[inserts[full_table_name]['columns'][column_name]] = v
        if not propagated_row:
            inserts[full_table_name]['rows'].append(row)

def objects_to_dml(nodes, objects, pk = DefaultPK):
    inserts = {}
    for object_type, objects in objects.items():
        object_to_dml(nodes, inserts, nodes['index'][object_type], objects, pk = pk)
    return {'inserts': inserts}
