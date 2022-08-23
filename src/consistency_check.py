"""Check consistency of CSON"""

from constants import CSON_TYPES

def check_property(errors:list, obj:dict, key:str, typ:type, loc:list, must_exist:bool = False):
    if key in obj:
        if isinstance(obj[key], typ):
            return True
        else:
            errors.append({'loc':loc + [key]\
                ,'msg':f'type {typ.__name__} expected'})
            return False
    elif must_exist:
        errors.append({'loc':loc + [key],'msg':'missing'})
    return False


def check_cson(cson:dict):
    errors = []
    check_property(errors, cson, 'namespace', str, [], False)
    check_property(errors, cson, '$version', str, [], False)
    if check_property(errors, cson, 'definitions', dict, [], True):
        if cson['definitions'] == {}:
            errors.append({'loc':['definitions'],'msg':'empty'})
        for k, cson_definition in cson['definitions'].items():
            if check_property(errors, cson['definitions'], k, dict, ['definitions'], True):
                check_cson_definition(errors, cson, cson_definition, ['definitions', k])
    return errors

def check_cson_definition(errors:list, cson:dict, cson_definition:dict, loc:list):
    if check_property(errors, cson_definition, 'includes', list, loc, False):
        for incl in cson_definition['includes']:
            if incl not in cson['definitions']:
                errors.append({'loc':loc + ['includes', incl]\
                    ,'msg':'unknown definition'})
    if check_property(errors, cson_definition, 'kind', str, loc, True):
        if not cson_definition['kind'] in ['type', 'entity', 'aspect']:
            errors.append({'loc':loc + ['kind', cson_definition['kind']]\
                ,'msg':'unknown kind'})
        if cson_definition['kind'] == 'entity':
            if check_property(errors, cson_definition, 'elements', dict, loc, True):
                keys = [k for k, v in cson_definition['elements'].items() if 'key' in v and v['key']]
                if len(keys) != 1:
                    errors.append({'loc':loc + ['elements'],\
                        'msg':'an entity must have exactly one key-element'})
        check_cson_element(errors, cson, cson_definition, loc)


def check_cson_element(errors, cson, element, loc):
    if element == {}:
        errors.append({'loc':loc, 'msg':'empty'})
    else:
        has_type = check_property(errors, element, 'type', str, loc, False)
        has_items = check_property(errors, element, 'items', dict, loc, False)
        has_elements = check_property(errors, element, 'elements', dict, loc, False)
        if sum([has_type, has_items, has_elements]) != 1:
            errors.append({'loc':loc, 'msg':'exactly one property "type", "items" or "elements" must exist'})
        if has_elements:
            for sub_element_name, sub_element in element['elements'].items():
                if check_property(errors, element['elements'], sub_element_name, dict, loc + ['elements'], True):
                    check_cson_element(errors, cson, sub_element, loc + ['elements'] + [sub_element_name])
        elif has_items:
            check_cson_element(errors, cson, element['items'], loc + ['items'])
        elif has_type:
            if element['type'] not in CSON_TYPES and element['type'] not in cson['definitions']:
                errors.append({'loc':loc + ['type', element['type']], 'msg':'undefined'})
            if element['type'] == loc[1]:
                errors.append({'loc':loc + ['type'], 'msg':'recursive type definition ' + element['type']})
            if element['type'] == 'cds.Association':
                if check_property(errors, element, 'target', str, loc + ['type'], True):
                    if element['target'] in cson['definitions']:
                        target = cson['definitions'][element['target']]
                        if check_property(errors, target, 'kind', str, loc + ['target', element['target']], True):
                            if target['kind'] != 'entity':
                                errors.append({'loc':loc + ['target', element['target']]\
                                    , 'msg':'target must be entity'})
                    else:
                        errors.append({'loc':loc + ['target', element['target']], 'msg':'undefined'})
