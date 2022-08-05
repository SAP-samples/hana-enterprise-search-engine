import esh_objects
import json
class Constants(object):
    entities = 'entities'
    views = 'views'
    view_name = 'view_name'
    odata_name = 'odata_name'

def map_search_query_filter_comparison(incoming_request_index, model_views, item, main_scope, result_items):
    if 'type' not in item or item['type'] != 'Comparison':
        raise Exception(f"Unexpected item: {item}. It should be Comparison")
    if 'type' in item['property']:
        if item['property']['type'] == esh_objects.Property.__name__:
            property_name = item['property']['property'] if not type(item['property']['property']) is list else ".".join(item['property']['property'])
            found_property = False
            try:
                for column_name, column_definition in model_views[main_scope]['columns'].items():
                    if property_name == ".".join(column_definition['path']):
                        found_property = True
                        item['property']['property'] = column_name
                        if 'comparison_paths' not in result_items:
                            result_items['comparison_paths'] = []
                        # TODO check if it is better via property_name: result_items['comparison_paths'].append(property_name)
                        result_items['comparison_paths'].append(column_definition['path'])
                        break
            except:
                raise Exception(f"Incoming requests [{incoming_request_index}]: Unknown property: {property_name} for scope: {main_scope}")
            if not found_property:
                raise Exception(f"Incoming requests [{incoming_request_index}]: Unknown property: {property_name} for scope: {main_scope}")
        elif item['property']['type'] == esh_objects.Expression.__name__:
            map_search_query_filter_expression(incoming_request_index, model_views, item['property'], main_scope, result_items)
            # raise Exception(f"Incoming requests [{incoming_request_index}]: searchQueryFilter not implemented Comparison -> Property: {item['property']['type']}")
    else:
        property_name = item['property'] 
        found_property = False
        try:
            for column_name, column_definition in model_views[main_scope]['columns'].items():
                if property_name == ".".join(column_definition['path']):
                    found_property = True
                    item['property'] = column_name
                    break
        except:
            raise Exception(f"Incoming requests [{i}]: Unknown property: {property_name} for scope: {main_scope}")
        if not found_property:
            raise Exception(f"Incoming requests [{i}]: Unknown property: {property_name} for scope: {main_scope}")

def map_search_query_filter_expression(incoming_request_index, model_views, item, main_scope, result_items):
    if 'type' not in item or item['type'] != 'Expression':
        raise Exception(f"Unexpected item: {item}. It should be Expression")
    for expression_item in item['items']:
        if 'type' in expression_item:
            if expression_item['type'] == 'Comparison':
                map_search_query_filter_comparison(incoming_request_index, model_views, expression_item, main_scope, result_items)
            elif expression_item['type'] == 'Expression':
                for expression_item_element in expression_item['items']:
                    map_search_query_filter_comparison(incoming_request_index, model_views, expression_item_element, main_scope, result_items)
            else:
                result_items['exist_free_style'] = True
        else:
            result_items['exist_free_style'] = True

def map_search_query_filter(model_views, search_query_filter, result_items):
    if search_query_filter['type'] != esh_objects.Expression.__name__:
        raise Exception(f"Incoming requests [{i}]: searchQueryFilter has to be type Expression, but got: {search_query_filter['type']}")
    for j in range(0, len(search_query_filter['items'])):
        item = search_query_filter['items'][j]
        if type(item) is dict:
            if item['type'] == esh_objects.ScopeComparison.__name__:
                if j != 0:
                    raise Exception(f"Incoming requests [{i}]: searchQueryFilter should have ScopeComparison on the first position, but got on position: {j}")
                for i in range(0, len(item['values'])):
                    scope = item['values'][i]
                    if scope not in model_views:
                        raise Exception(f"Incoming requests [{i}]: searchQueryFilter contains unknown scope: {scope}")
                    item['values'][i] = model_views[scope]['odata_name']
                    main_scope = scope # TODO currently only one main scope allowed, e.g. SCOPE:example.Person
                    result_items['scope'] = main_scope            
            elif item['type'] == esh_objects.Comparison.__name__:
                map_search_query_filter_comparison(i, model_views, item, main_scope, result_items)
            elif item['type'] == esh_objects.Expression.__name__:
                map_search_query_filter_expression(i, model_views, item, main_scope, result_items)
                # raise Exception(f"Incoming requests [{i}]: searchQueryFilter not implemented mapping type: {item['type']}")
        else:
            result_items['exist_free_style'] = True


def map_request(mapping: dict, incoming_requests: list):
    result_items = {}
    for i in range(0, len(incoming_requests)):
        incoming_request = incoming_requests[i]
        incoming_request['select'] = ['ID']
        for key in incoming_request.keys():
            if key == esh_objects.Constants.searchQueryFilter:
                if not incoming_request[esh_objects.Constants.searchQueryFilter]:
                    raise Exception(f"Incoming requests [{i}]: searchQueryFilter cannot be empty")
                # HHH search_query_filter = esh_objects.deserialize_objects(incoming_request[esh_objects.Constants.searchQueryFilter])
                search_query_filter = incoming_request[esh_objects.Constants.searchQueryFilter]
                map_search_query_filter(mapping['views'], search_query_filter, result_items)
    returning_object = {
            'incoming_requests': incoming_requests
    }
    if 'scope' in result_items:
        returning_object['scope'] = result_items['scope']
    if 'comparison_paths' in result_items:
        returning_object['comparison_paths'] = result_items['comparison_paths']
    if 'exist_free_style' in result_items:
        returning_object['exist_free_style'] = result_items['exist_free_style']
    return returning_object
