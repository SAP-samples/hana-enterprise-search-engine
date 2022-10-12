import esh_objects as esh


def extract_pathes(query: esh.EshObject):
    pathes = {tuple(['id']):''}
    scope = []
    if query.orderby:
        for orderby in query.orderby:
            if isinstance(orderby.key, str):
                pathes[tuple([orderby.key])] = ''
            elif isinstance(orderby.key, list):
                pathes[tuple(orderby.key)] = ''
            else:
                raise NotImplementedError
    if query.select:
        for select in query.select:
            if isinstance(select, str):
                pathes[tuple([select])] = ''
            elif isinstance(select, list):
                pathes[tuple(select)] = ''
            else:
                raise NotImplementedError
    if query.searchQueryFilter:
        extract_property_path(query.searchQueryFilter.items, scope, pathes)
    return (scope, pathes)


def extract_property_path(obj, scope, pathes):
    if isinstance(obj, list):
        for o in obj:
            extract_property_path(o, scope, pathes)
    else:
        match type(obj):
            case esh.Expression:
                extract_property_path(obj.items, scope, pathes)
            case esh.ScopeComparison:
                scope.extend(obj.values)
            case esh.Comparison:
                if isinstance(obj.property.property, str):
                    pathes[(obj.property.property,)] = ''
                else:
                    pathes[tuple(obj.property.property)] = ''

def map_query(query, scope, pathes):
    if query.orderby:
        for orderby in query.orderby:
            if isinstance(orderby.key, str):
                orderby.key = pathes[tuple([orderby.key])]
            elif isinstance(orderby.key, list):
                orderby.key = pathes[tuple(orderby.key)]
            else:
                raise NotImplementedError
    if query.select:
        select_int = []
        for select in query.select:
            if isinstance(select, str):
                select_int.append(pathes[tuple([select])])
            elif isinstance(select, list):
                select_int.append(pathes[tuple(select)])
            else:
                raise NotImplementedError
        query.select = select_int
    if query.searchQueryFilter:        
        map_property(query.searchQueryFilter.items, scope, pathes)

def map_property(obj, scope, pathes):
    if isinstance(obj, list):
        for o in obj:
            map_property(o, scope, pathes)
    else:
        match type(obj):
            case esh.Expression:
                extract_property_path(obj.items, scope, pathes)
            case esh.ScopeComparison:
                obj.values = scope
            case esh.Comparison:
                if isinstance(obj.property.property, str):
                    obj.property.property = pathes[(obj.property.property,)]
                else:
                    obj.property.property = pathes[tuple(obj.property.property)]



'''
        if obj.type:
            if obj.type == 'Path':
                obj.type = 'Property'
                obj.property = pathes[tuple(obj.attribute)]
                return
            elif obj.type == 'Property':
                obj.property = pathes[tuple([obj.property])]
                return
            elif obj.type == 'ScopeComparison':
                obj.values = scope
                return
        for o in obj.values():
            map_property(o, scope, pathes)

'''