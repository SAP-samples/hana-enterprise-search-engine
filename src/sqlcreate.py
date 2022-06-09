"""Creates SQL commands from node"""
from copy import deepcopy
import mapping


ESH_CONFIG_TEMPLATE = {
    'uri': '~/$metadata/EntitySets',
    'method': 'PUT',
    'content': {
        'Fullname': '',
        'EntityType': {
            '@EnterpriseSearch.enabled': True,
            '@Search.searchable': True,
            '@EnterpriseSearchHana.identifier': 'VORGANG_MODEL',
            '@EnterpriseSearchHana.passThroughAllAnnotations': True,
            'Properties': [
                {
                    'Name': '_ID',
                    '@EnterpriseSearch.key': True,
                    '@Search.defaultSearchElement': True,
                    '@UI.hidden': True
                }]}}}

'''
ToDo: Table creation
'''

def sequence(i = 0, prefix = '', fill = 3):
    while True:
        if prefix:
            yield f'{prefix}{str(i).zfill(fill)}'
        else:
            yield i
        i += 1

class ColumnView:
    """Column view definition"""
    def __init__(self, view_name: str, anchor_table_name: str) -> None:
        self.view_name = view_name
        self.anchor_table_name = anchor_table_name
        self.join_index = {}
        self.view_attribute = []
        self.join_conditions = []
        self.join_path = {}
        self.table(anchor_table_name)
        self.join_path_id_gen = sequence(1, 'JP', 3)
        self.join_condition_id_gen = sequence(1, 'JC', 3)
    def table(self, table_name):
        if not table_name in self.join_index:
            self.join_index[table_name] = 0
        else:
            self.join_index[table_name] += 1
        return (table_name, self.join_index[table_name])

    def add_join_condition(self, join_path_id, join_index_from, column_name_from, join_index_to, column_name_to):
        join_condition_id = next(self.join_condition_id_gen)
        self.join_conditions.append((join_condition_id, self.get_join_index_name(join_index_from),\
            column_name_from, self.get_join_index_name(join_index_to), column_name_to))
        if join_path_id in self.join_path:
            self.join_path[join_path_id].add(join_condition_id)
        else:
            self.join_path[join_path_id] = set([join_condition_id])

    @staticmethod
    def get_join_index_name(join_index):
        table_name, index = join_index
        if index == 0:
            return table_name
        else:
            return f'{table_name}.temp{str(index).zfill(2)}'

    def get_sql_statement(self):
        v  = f'create or replace column view "{self.view_name}" with parameters (indexType=6,\n'
        for join_index in self.join_index:
            v += f'joinIndex="{join_index}",joinIndexType=0,joinIndexEstimation=0,\n'
        for jc in self.join_conditions:
            v += f'joinCondition=(\'{jc[0]}\',"{jc[1]}","{jc[2]}","{jc[3]}","{jc[4]}",\'\',81,0),\n'
        for jp_name, jp_conditions in self.join_path.items():
            v += f"joinPath=('{jp_name}','{','.join(jp_conditions)}'),\n"
        for view_prop_name, table_name, table_prop_name, join_path_id in self.view_attribute:
            v += f"viewAttribute=('{view_prop_name}',\"{table_name}\",\"{table_prop_name}\",'{join_path_id}'"\
                +",'default','attribute'),\n"
        v += f"view=('default',\"{self.anchor_table_name}\"),\n"
        v += "defaultView='default',\n"
        v += 'OPTIMIZEMETAMODEL=0)'
        return v

def nodes_to_ddl(nodes, schema_name):
    tables = []
    views = []
    esh_configs = []
    for node in nodes['nodes'].values():
        create_statement = f'create table "{node[Constants.table_name]}" ( {", ".join(get_columns(node))} )'
        tables.append(create_statement)
        if node['level'] == 0:
            esh_config_hana_identifier = node[Constants.table_name][len(mapping.ENTITY_PREFIX):]
            view_name = mapping.VIEW_PREFIX + esh_config_hana_identifier
            cv = ColumnView(view_name, node['table_name'])
            anchor_join_index = (node['table_name'], 0)
            esh_config = deepcopy(ESH_CONFIG_TEMPLATE)
            if 'annotations' in node:
                esh_config['content']['EntityType'] |= node['annotations']
            # for UI5 enterprise search UI to work
            if 'annotations' in node and '@EndUserText.Label' in node['annotations']\
                and not '@SAP.Common.Label' in node['annotations']:
                esh_config['content']['EntityType']['@SAP.Common.Label'] = node['annotations']['@EndUserText.Label']

            esh_config['content']['Fullname'] = f'{schema_name}/{view_name}'
            esh_config['content']['EntityType']['@EnterpriseSearchHana.identifier'] = esh_config_hana_identifier
            esh_config_properties = []
            #ui_position = 10
            #for prop_name, prop in node['properties'].items():
            #    if not 'rel' in prop:
            #        #cv.view_attribute.append((prop_name, node[Constants.table_name], prop_name, ''))
            #        if prop_name != '_ID':
            #            col_conf = {'Name': prop_name}
            #            if 'annotations' in prop:
            #                col_conf |= prop['annotations']
            #            # for UI5 enterprise search UI to work
            #            if 'annotations' in prop and '@EndUserText.Label' in prop['annotations']\
            #                and not '@SAP.Common.Label' in prop['annotations']:
            #                col_conf['@SAP.Common.Label'] = prop['annotations']['@EndUserText.Label']
            #            col_conf['@Search.defaultSearchElement'] = True
            #            col_conf['@UI.identification'] = [{'position': ui_position}]
            #            ui_position += 10
            #            esh_config_properties.append(col_conf)
            traverse_contains(cv, esh_config_properties, nodes, node, anchor_join_index)
            views.append(cv.get_sql_statement())
            esh_config['content']['EntityType']['Properties'].extend(esh_config_properties)
            esh_configs.append(esh_config)

    return {'tables': tables, 'views': views, 'eshConfig':esh_configs}

def traverse_contains(cv: ColumnView, esh_config_properties, nodes, parent_node, parent_join_index,\
    join_path_id = None, view_columns_prefix = None, ignore_in_view = None, is_root_node = True):
    ui_position = 10
    for prop_name, prop in parent_node['properties'].items():
        if ignore_in_view and ignore_in_view == prop_name:
            continue
        if 'rel' in prop:
            continue
        if view_columns_prefix:
            view_column_name = '.'.join([view_columns_prefix, prop_name])
        else:
            view_column_name = prop_name
        view_column_name = view_column_name.replace('.', '_')
        if 'rel' in prop:
            child_node_name = prop['rel']['table_name']
            child_node = nodes['nodes'][child_node_name]
            if join_path_id:
                jp_id = join_path_id
            else:
                jp_id = next(cv.join_path_id_gen)
            child_join_index = cv.table(child_node['table_name'])
            cv.add_join_condition(jp_id, parent_join_index, parent_node['pk'], child_join_index, parent_node['pk'])
            traverse_contains(cv, esh_config_properties, nodes, child_node, child_join_index, jp_id,\
                view_column_name, parent_node['pk'], is_root_node = False)
        else:
            cv.view_attribute.append((view_column_name, parent_node[Constants.table_name], prop_name, ''))
            # ESH config
            if prop_name != '_ID':
                col_conf = {'Name': view_column_name}
                if 'annotations' in prop:
                    col_conf |= prop['annotations']
                # for UI5 enterprise search UI to work
                if 'annotations' in prop and '@EndUserText.Label' in prop['annotations']\
                    and not '@SAP.Common.Label' in prop['annotations']:
                    col_conf['@SAP.Common.Label'] = prop['annotations']['@EndUserText.Label']
                if not prop_name.startswith('_ID'):
                    col_conf['@Search.defaultSearchElement'] = True
                if is_root_node:
                    col_conf['@UI.identification'] = [{'position': ui_position}]
                    ui_position += 10
                esh_config_properties.append(col_conf)
