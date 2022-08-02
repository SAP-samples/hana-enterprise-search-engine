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

def tables_dd(tables):
    return [f'create table "{t[Constants.table_name]}" ( {", ".join(get_columns(t))} )'\
        for t in tables.values()]

def mapping_to_ddl(mapping, schema_name):
    tables = tables_dd(mapping['tables'])
    #sdd = search_dd(schema_name, mapping, [v for v in mapping['views'].values()])
    #return {'tables': tables, 'views': sdd['views'], 'eshConfig':sdd['eshConfig']}
    views = []
    esh_configs = []
    for anchor_entity in mapping['entities'].values():
        cv = ColumnView(mapping, anchor_entity, schema_name)
        cv.by_default()
        view, esh_config = cv.data_definition()
        views.append(view)
        esh_configs.append(esh_config)
    return {'tables': tables, 'views': views, 'eshConfig':esh_configs}
