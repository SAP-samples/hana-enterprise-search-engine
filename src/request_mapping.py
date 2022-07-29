import esh_objects
import json
class Constants(object):
    entities = 'entities'
    views = 'views'
    view_name = 'view_name'
    odata_name = 'odata_name'

def map_request(mapping: dict, incoming_requests: list):
    for i in range(0, len(incoming_requests)):
        incoming_request = incoming_requests[i]
        main_scope = None
        for key in incoming_request.keys():
            if key == esh_objects.Constants.searchQueryFilter:
                if not incoming_request[esh_objects.Constants.searchQueryFilter]:
                    raise Exception(f"Incoming requests [{i}]: searchQueryFilter cannot be empty")
                # HHH search_query_filter = esh_objects.deserialize_objects(incoming_request[esh_objects.Constants.searchQueryFilter])
                search_query_filter = incoming_request[esh_objects.Constants.searchQueryFilter]
                if search_query_filter['type'] != esh_objects.Expression.__name__:
                    raise Exception(f"Incoming requests [{i}]: searchQueryFilter has to be type Expression, but got: {search_query_filter['type']}")
                for j in range(0, len(search_query_filter['items'])):
                    item = search_query_filter['items'][j]
                    if item['type'] == esh_objects.ScopeComparison.__name__:
                        if j != 0:
                            raise Exception(f"Incoming requests [{i}]: searchQueryFilter should have ScopeComparison on the first position, but got on position: {j}")
                        for i in range(0, len(item['values'])):
                            scope = item['values'][i]
                            if scope not in mapping[Constants.views]:
                                raise Exception(f"Incoming requests [{i}]: searchQueryFilter contains unknown scope: {scope}")
                            item['values'][i] = mapping[Constants.views][scope]['odata_name']
                            main_scope = scope # TODO currently only one main scope allowed, e.g. SCOPE:example.Person               
                    elif item['type'] == esh_objects.Comparison.__name__:
                        if 'type' in item['property']:
                            if item['property']['type'] == esh_objects.Property.__name__:
                                property_name = item['property']['property']
                                item['property']['property'] = mapping[Constants.views][main_scope]['elements'][property_name]['view_column_name']
                            else:
                                raise Exception(f"Incoming requests [{i}]: searchQueryFilter not implemented Comparison-> Property: {item['property']['type']}")
                        else:
                            property_name = item['property'] 
                            item['property'] = mapping[Constants.views][main_scope]['elements'][property_name]['view_column_name']
                    elif item['type'] == esh_objects.Expression.__name__:
                        raise Exception(f"Incoming requests [{i}]: searchQueryFilter not implemented mapping type: {item['type']}")
    return incoming_requests
