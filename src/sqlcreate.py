'''Creates SQL commands from tables'''
from __future__ import annotations
from copy import deepcopy
from column_view import ColumnView

class Constants(object):
    table_name = 'table_name'
    columns = 'columns'
    type = 'type'
    length = 'length'
    precision = 'precision'
    scale = 'scale'
    srid = 'srid'

def get_columns(table):
    columns = []
    for prop_name, prop in table[Constants.columns].items():
        if 'isVirtual' in prop and prop['isVirtual']:
            continue
        if Constants.length in prop:
            column_type = f'{prop[Constants.type]}({prop[Constants.length]})'
        elif Constants.srid in prop:
            column_type = f'{prop[Constants.type]}({prop[Constants.srid]})'
        elif Constants.precision in prop and Constants.scale in prop:
            column_type = f'{prop[Constants.type]}({prop[Constants.precision]},{prop[Constants.scale]})'
        else:
            column_type = prop[Constants.type]
        if 'pk' in table and table['pk'] == prop_name:
            suffix = ' PRIMARY KEY'
        else:
            suffix = ''
        cl = f'"{prop_name}" {column_type}{suffix}'
        columns.append(cl)
    return columns

def get_indices(tables, schema_name, hana_version):
    indices = []
    for table in tables.values():
        if table['external_path'][-1] == 'source' and 'NAME' in table['columns'] and 'SID' in table['columns'] and 'TYPE' in table['columns']:
            sql = f'create unique index "{table[Constants.table_name]}_SOURCE" on "{schema_name}"."{table[Constants.table_name]}"("NAME", "TYPE", "SID")'
            indices.append(sql)
        #CREATE UNIQUE INDEX idx3 ON t(b, c);
        for i, (prop_name, prop) in enumerate(table[Constants.columns].items()):
            if 'annotations' in prop and '@sap.esh.isText' in prop['annotations'] and prop['annotations']['@sap.esh.isText']:
                if hana_version == 2:
                    indices.append(f'create fulltext index "{table[Constants.table_name]}_{i}" on "{schema_name}"."{table[Constants.table_name]}" ("{prop_name}") fast preprocess on fuzzy search index on search only off async')
                elif hana_version == 4:
                    indices.append(f'create fuzzy search index "{table[Constants.table_name]}_{i}" on "{schema_name}"."{table[Constants.table_name]}" ("{prop_name}") search mode text')
                else:
                    raise NotImplementedError
    return indices

def tables_dd(tables, schema_name):
    return [f'create table "{schema_name}"."{t[Constants.table_name]}" ( {", ".join(get_columns(t))} )'\
        for t in tables.values()]

def mapping_to_ddl(mapping, schema_name, hana_version  = 2):
    tables = tables_dd(mapping['tables'], schema_name)
    indices = get_indices(mapping['tables'], schema_name, hana_version)
    views = []
    esh_configs = []
    for anchor_entity_name, anchor_entity in mapping['entities'].items():
        if 'annotations' in anchor_entity and '@EnterpriseSearch.enabled' in anchor_entity['annotations']:
            if anchor_entity['annotations']['@EnterpriseSearch.enabled']:
                cv = ColumnView(mapping, anchor_entity_name, schema_name, False)
            else:
                continue
        else: 
            cv = ColumnView(mapping, anchor_entity_name, schema_name, True)
        cv.by_default()
        view, esh_config = cv.data_definition()
        views.append(view)
        esh_configs.append(esh_config)
    return {'tables': tables, 'views': views, 'eshConfig':esh_configs, 'indices':indices}
