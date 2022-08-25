def extract_pathes(query):
    pathes = {tuple(['id']):''}
    scope = []
    if 'orderby' in query:
        for orderby in query['orderby']:
            if isinstance(orderby['key'], str):
                pathes[tuple([orderby['key']])] = ''
            elif isinstance(orderby['key'], list):
                pathes[tuple(orderby['key'])] = ''
            else:
                raise NotImplementedError
    if 'select' in query:
        for select in query['select']:
            if isinstance(select, str):
                pathes[tuple([select])] = ''
            elif isinstance(select, list):
                pathes[tuple(select)] = ''
            else:
                raise NotImplementedError
    extract_property_path(query, scope, pathes)
    return (scope, pathes)


def extract_property_path(obj, scope, pathes):
    if isinstance(obj, list):
        for o in obj:
            extract_property_path(o, scope, pathes)
    elif isinstance(obj, dict):
        if 'type' in obj:
            if obj['type'] == 'Path':
                pathes[tuple(obj['attribute'])] = ''
                return
            elif obj['type'] == 'Property':
                pathes[tuple([obj['property']])] = ''
                return
            elif obj['type'] == 'ScopeComparison':
                scope.extend(obj['values'])
                return
        for o in obj.values():
            extract_property_path(o, scope, pathes)

def map_query(query, scope, pathes):
    if 'orderby' in query:
        for orderby in query['orderby']:
            if isinstance(orderby['key'], str):
                orderby['key'] = pathes[tuple([orderby['key']])]
            elif isinstance(orderby['key'], list):
                orderby['key'] = pathes[tuple(orderby['key'])]
            else:
                raise NotImplementedError
    if 'select' in query:
        select_int = []
        for select in query['select']:
            if isinstance(select, str):
                select_int.append(pathes[tuple([select])])
            elif isinstance(select, list):
                select_int.append(pathes[tuple(select)])
            else:
                raise NotImplementedError
        query['select'] = select_int
    map_property(query, scope, pathes)

def map_property(obj, scope, pathes):
    if isinstance(obj, list):
        for o in obj:
            map_property(o, scope, pathes)
    elif isinstance(obj, dict):
        if 'type' in obj:
            if obj['type'] == 'Path':
                obj['type'] = 'Property'
                obj['property'] = pathes[tuple(obj['attribute'])]
                return
            elif obj['type'] == 'Property':
                obj['property'] = pathes[tuple([obj['property']])]
                return
            elif obj['type'] == 'ScopeComparison':
                obj['values'] = scope
                return
        for o in obj.values():
            map_property(o, scope, pathes)
