"""Column View"""
from copy import deepcopy
from name_mapping import NameMapping
from constants import ENTITY_PREFIX, VIEW_PREFIX

_ESH_CONFIG_TEMPLATE = {
    'uri': '~/$metadata/EntitySets',
    'method': 'PUT',
    'content': {
        'Fullname': '',
        'EntityType': {
            '@EnterpriseSearch.enabled': True,
            '@Search.searchable': True,
            '@EnterpriseSearchHana.identifier': None,
            '@EnterpriseSearchHana.passThroughAllAnnotations': True,
            'Properties': []}}}

def sequence(i = 0, prefix = '', fill = 3):
    while True:
        if prefix:
            yield f'{prefix}{str(i).zfill(fill)}'
        else:
            yield i
        i += 1

def sequence_int(i = 10, step = 10):
    while True:
        yield i
        i += step

class ColumnView:
    """Column view definition"""
    def __init__(self, mapping, anchor_entity_name, schema_name, default_annotations) -> None:
        self.mapping = mapping
        self.anchor_entity = mapping['entities'][anchor_entity_name]
        self.schema_name = schema_name
        self.default_annotations = default_annotations
        self.esh_config = deepcopy(_ESH_CONFIG_TEMPLATE)
        self.column_name_mapping = NameMapping()
        self.join_index = {}
        self.view_attribute = []
        self.join_conditions = []
        self.join_path = {}
        self.join_path_id_gen = sequence(1, 'JP', 3)
        self.join_condition_id_gen = sequence(1, 'JC', 3)
        self.ui_position_gen = sequence_int()

    def by_selector(self, view_name, odata_name, selector):
        self.view_name = view_name
        self.odata_name = odata_name
        self.selector = selector


    @staticmethod
    def _get_join_index_name(join_index):
        table_name, index = join_index
        if index == 0:
            return table_name
        else:
            return f'{table_name}.temp{str(index).zfill(2)}'

    @staticmethod
    def _cleanup_labels(annotations:dict):
        # for UI5 enterprise search UI to work
        if '@EndUserText.Label' in annotations and not '@SAP.Common.Label' in annotations:
            annotations['@SAP.Common.Label'] = annotations['@EndUserText.Label']
            del annotations['@EndUserText.Label']

    def _table(self, table_name):
        if not table_name in self.join_index:
            self.join_index[table_name] = 0
        else:
            self.join_index[table_name] += 1
        return (table_name, self.join_index[table_name])

    def _add_join_condition(self, join_path_id, join_index_from, column_name_from, join_index_to, column_name_to):
        join_condition_id = next(self.join_condition_id_gen)
        self.join_conditions.append((join_condition_id, self._get_join_index_name(join_index_from),\
            column_name_from, self._get_join_index_name(join_index_to), column_name_to))
        if join_path_id in self.join_path:
            self.join_path[join_path_id].add(join_condition_id)
        else:
            self.join_path[join_path_id] = set([join_condition_id])

    def _get_sql_statement(self):
        v  = f'create or replace column view "{self.schema_name}"."{self.view_name}" with parameters (indexType=6,\n'
        for join_index in self.join_index:
            v += f'joinIndex="{self.schema_name}"."{join_index}",joinIndexType=0,joinIndexEstimation=0,\n'
        for jc in self.join_conditions:
            v += f'joinCondition=(\'{jc[0]}\',"{self.schema_name}"."{jc[1]}","{jc[2]}","{self.schema_name}"."{jc[3]}","{jc[4]}",\'\',81,0),\n'
        for jp_name, jp_conditions in self.join_path.items():
            v += f"joinPath=('{jp_name}','{','.join(sorted(list(jp_conditions)))}'),\n"
        for view_prop_name, table_name, table_prop_name, join_path_id, _ in self.view_attribute:
            v += f"viewAttribute=('{view_prop_name}',\"{self.schema_name}\".\"{table_name}\",\"{table_prop_name}\",'{join_path_id}'"\
                +",'default','attribute'),\n"
        v += f"view=('default',\"{self.schema_name}\".\"{self.anchor_entity['table_name']}\"),\n"
        v += "defaultView='default',\n"
        v += 'OPTIMIZEMETAMODEL=0,\n'
        v += "'LEGACY_MODE' = 'TRUE')"
        return v

    def _add_view_column(self, join_index, join_path_id,\
        name_path, table_column_name, annotations, selector_pos):
        table_name = join_index[0]
        view_column_name, _ = self.column_name_mapping.register(name_path)
        selector_pos['as'] = view_column_name
        self.view_attribute.append((view_column_name, \
            self._get_join_index_name(join_index), table_column_name, join_path_id, name_path))
        # ESH config
        col_conf = {'Name': view_column_name}
        if annotations:
            self._cleanup_labels(annotations)
            col_conf |= annotations
        is_enteprise_search_key = \
            not join_path_id and table_column_name == self.mapping['tables'][table_name]['pk']
        if is_enteprise_search_key:
            col_conf['@EnterpriseSearch.key'] = True
            col_conf['@UI.hidden'] = True
        elif self.default_annotations:
            if self.mapping['tables'][table_name]['columns'][table_column_name]['type'] not in ['ST_POINT', 'ST_GEOMETRY']:
                col_conf['@Search.defaultSearchElement'] = True
            if not join_path_id:
                col_conf['@UI.identification'] = [{'position': next(self.ui_position_gen)}]
        self.esh_config['content']['EntityType']['Properties'].append(col_conf)

    def _add_join(self, join_path_id, source_join_index, target_entity_pos\
        , source_column = '', target_column = ''):
        if join_path_id:
            jp_id = join_path_id
        else:
            jp_id = next(self.join_path_id_gen)
        target_table_name = target_entity_pos['table_name']
        target_join_index = self._table(target_table_name)
        if source_column:
            source_key = source_column
            target_key = target_column
        else:
            source_key = self.mapping['tables'][source_join_index[0]]['pk']
            target_key = self.mapping['tables'][target_table_name]['pkParent']
        self._add_join_condition(jp_id, source_join_index, source_key\
            , target_join_index, target_key)
        return target_join_index, jp_id

    def _add_column(self, entity_pos, join_index, join_path_id, name_path, selector_pos):
        if 'items' in entity_pos:
            ep = entity_pos['items']
            join_index, join_path_id = self._add_join(join_path_id, join_index, ep)
        else:
            ep = entity_pos
        annotations = ep['annotations'] if 'annotations' in ep else {}
        self._add_view_column(join_index, join_path_id,\
            name_path, ep['column_name'], annotations, selector_pos)


    def _traverse(self, selector_pos, entity_pos, name_path, join_index, join_path_id = ''):
        if 'elements' in selector_pos:
            for selected_property_name, selected_property in selector_pos['elements'].items():
                # ToDo: Error handling
                entity_property = entity_pos['elements'][selected_property_name]
                if 'elements' in selected_property:
                    if 'elements' in entity_property:
                        self._traverse(selected_property, entity_property\
                            , name_path + [selected_property_name], join_index, join_path_id)
                    elif 'items' in entity_property and 'elements' in entity_property['items']:
                        target_join_index, jp_id = \
                            self._add_join(join_path_id, join_index, entity_property['items'])
                        self._traverse(selected_property, entity_property['items']\
                            , name_path + [selected_property_name], target_join_index, jp_id)
                    elif 'definition' in entity_property and 'type' in entity_property['definition']\
                        and entity_property['definition']['type'] == 'cds.Association':
                        target_entity = self.mapping['entities'][entity_property['definition']['target']]
                        if '@sap.esh.isVirtual' in entity_property['definition']\
                            and entity_property['definition']['@sap.esh.isVirtual']:
                            source_table = self.mapping['tables'][join_index[0]]
                            source_column = source_table['pk']
                            target_column = source_table['columns'][entity_property['column_name']]['rel']['column_name']
                        else:
                            source_column = entity_property['column_name']
                            target_column = self.mapping['tables'][target_entity['table_name']]['pk']
                        target_join_index, jp_id = \
                            self._add_join(join_path_id, join_index, target_entity, source_column, target_column)
                        self._traverse(selected_property, target_entity\
                            , name_path + [selected_property_name], target_join_index, jp_id)
                    else:
                        raise NotImplementedError
                else:
                    self._add_column(entity_property, join_index, join_path_id\
                        , name_path + [selected_property_name], selected_property)
        else:
            self._add_column(entity_pos, join_index, join_path_id, name_path, selector_pos)

    def _make_default_selector(self, element, path, table_name):
        if 'table_name' in element:
            table_name = element['table_name']
        if 'elements' in element and element['elements']:
            view_element = {}
            for k, v in element['elements'].items():
                if not ('definition' in v and 'isVirtual' in v['definition']):
                    view_element[k] = self._make_default_selector(v, path + [k], table_name)
            return {'elements': view_element}
        if 'items' in element:
            return self._make_default_selector(element['items'], path, table_name)
        return {}

    def _selector_from_path(self, path, selector_pos):
        if path[0] not in selector_pos['elements']:
            selector_pos['elements'][path[0]] = {}
        if len(path) > 1:
            if 'elements' not in selector_pos['elements'][path[0]]:
                selector_pos['elements'][path[0]]['elements'] = {}
            self._selector_from_path(path[1:], selector_pos['elements'][path[0]])

    def by_path_list(self, path_list, view_name, odata_name):
        self.view_name = view_name
        self.odata_name = odata_name
        self.selector = {'elements':{}}
        for path in path_list:
            self._selector_from_path(path, self.selector)

    def by_default(self):
        self.view_columns = {}
        self.selector = self._make_default_selector(self.anchor_entity, [], None)
        self.odata_name = self.anchor_entity['table_name'][len(ENTITY_PREFIX):]
        self.view_name = VIEW_PREFIX + self.odata_name

    def by_default_and_path_list(self, path_list, view_name, odata_name):
        self.view_name = view_name
        self.odata_name = odata_name
        self.selector = self._make_default_selector(self.anchor_entity, [], None)
        for path in path_list:
            self._selector_from_path(path, self.selector)

    def data_definition(self):
        anchor_table_name = self.anchor_entity['table_name']
        if 'annotations' in self.anchor_entity:
            annotations = self.anchor_entity['annotations']
            self._cleanup_labels(annotations)
            self.esh_config['content']['EntityType'] |= annotations
        self.esh_config['content']['Fullname'] = f'{self.schema_name}/{self.view_name}'
        self.esh_config['content']['EntityType']['@EnterpriseSearchHana.identifier'] = self.odata_name
        self._traverse(self.selector, self.anchor_entity, [], self._table(anchor_table_name))

        has_default_search_element = False
        for prop in self.esh_config['content']['EntityType']['Properties']:
            if '@Search.defaultSearchElement' in prop:
                has_default_search_element = True
                break
        if not has_default_search_element:
            for prop in self.esh_config['content']['EntityType']['Properties']:
                if '@EnterpriseSearch.key' in prop and prop['@EnterpriseSearch.key']:
                    prop['@Search.defaultSearchElement'] = True

        return self._get_sql_statement(), self.esh_config

    def column_name_by_path(self, path, selector = None):
        if not selector:
            selector = self.selector
        if len(path) > 1:
            return self.column_name_by_path(path[1:], selector['elements'][path[0]])
        return selector['elements'][path[0]]['as']

