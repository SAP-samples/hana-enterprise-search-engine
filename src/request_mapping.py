import esh_objects

class Constants(object):
    entities = 'entities'
    views = 'views'
    view_name = 'view_name'
    odata_name = 'odata_name'

def map_request(mapping: dict, incoming_requests: list):
    mapped_requests = []
    for i in range(0, len(incoming_requests)):
        incoming_request = incoming_requests[i]
        mapped_request = esh_objects.IESSearchOptions({})
        main_scope = None
        for key in incoming_request.keys():
            if key == esh_objects.Constants.searchQueryFilter:
                if not incoming_request[esh_objects.Constants.searchQueryFilter]:
                    raise Exception(f"Incoming requests [{i}]: searchQueryFilter cannot be empty")
                search_query_filter = esh_objects.deserialize_objects(incoming_request[esh_objects.Constants.searchQueryFilter])
                if type(search_query_filter) != esh_objects.Expression:
                    raise Exception(f"Incoming requests [{i}]: searchQueryFilter has to be type Expression, but got: {search_query_filter.type}")
                root_search_query_filter_expression = esh_objects.Expression({
                    esh_objects.Constants.items: []
                })
                for j in range(0, len(search_query_filter.items)):
                    item = search_query_filter.items[j]
                    mapped_scope_comparison = esh_objects.ScopeComparison({
                        esh_objects.Constants.values: []
                    })
                    if type(item) == esh_objects.ScopeComparison:
                        if j != 0:
                            raise Exception(f"Incoming requests [{i}]: searchQueryFilter should have ScopeComparison on the first position, but got on position: {j}")
                        for scope in item.values:
                            if scope not in mapping[Constants.entities]:
                                raise Exception(f"Incoming requests [{i}]: searchQueryFilter contains unknown scope: {scope}")
                            # TODO change Constants.scope_connector_name="table_name"
                            mapped_scope_comparison.values.append(mapping[Constants.views][scope][Constants.odata_name])
                            main_scope = scope # TODO currently only one main scope allowed, e.g. SCOPE:example.Person
                        root_search_query_filter_expression.items.append(mapped_scope_comparison)
                mapped_request.searchQueryFilter = root_search_query_filter_expression
            elif key == "$top":
                mapped_request.top = incoming_request['$top']
            elif key == "$count":
                mapped_request.count = incoming_request['$count']
            else:
                raise Exception(f"Incoming requests [{i}]: unexpected property: {key}")
        mapped_requests.append(mapped_request)
    return mapped_requests
