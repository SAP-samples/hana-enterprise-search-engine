'''
External to internal mapping of query
'''
import esh_client as esh

def _extract_property_object(prop, pathes):
    if isinstance(prop, str):
        pathes[(prop,)] = ''
    else:
        pathes[tuple(prop)] = ''

def _extract_property_path(obj, pathes):
    if isinstance(obj, list):
        for o in obj:
            _extract_property_path(o, pathes)
    else:
        match type(obj):
            case esh.Property:
                _extract_property_object(obj.property, pathes)
            case esh.OrderBy:
                _extract_property_object(obj.key.property, pathes)
            case esh.Expression:
                _extract_property_path(obj.items, pathes)
            case esh.UnaryExpression:
                _extract_property_path(obj.item, pathes)
            case esh.Comparison:
                _extract_property_object(obj.property.property, pathes)

def extract_pathes(query: esh.EshObject):
    pathes = {tuple(['id']):''}
    if query.orderby:
        _extract_property_path(query.orderby, pathes)
    if query.select:
        _extract_property_path(query.select, pathes)
    if query.searchQueryFilter:
        _extract_property_path(query.searchQueryFilter.items, pathes)
    return pathes


def _map_property_object(prop, pathes):
    if isinstance(prop.property, str):
        prop.property = pathes[(prop.property,)]
    else:
        prop.property = pathes[tuple(prop.property)]



def _map_property(obj, pathes):
    if isinstance(obj, list):
        for o in obj:
            _map_property(o, pathes)
    else:
        match type(obj):
            case esh.Property:
                _map_property_object(obj, pathes)
            case esh.OrderBy:
                _map_property_object(obj.key, pathes)
            case esh.Expression:
                _map_property(obj.items, pathes)
            case esh.UnaryExpression:
                _map_property(obj.item, pathes)
            case esh.Comparison:
                _map_property_object(obj.property, pathes)

def map_query(query, pathes):
    if query.orderby:
        _map_property(query.orderby, pathes)
    if query.select:
        _map_property(query.select, pathes)
    if query.searchQueryFilter:
        _map_property(query.searchQueryFilter.items, pathes)
