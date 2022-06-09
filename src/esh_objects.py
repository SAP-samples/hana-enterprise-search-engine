"""Classes to define a query"""
import json

reservedCharacters = ['\\', '-', '(', ')', '~', '^', '?', '\'', ':', "'", '[', ']']
reservedWords = ['AND', 'OR', 'NOT']

#pylint: disable=invalid-name
#pylint: disable=missing-class-docstring
class Constants(object):
    """Constants used for query"""
    x = 'x'
    y = 'y'
    id = 'id'
    top = 'top'
    skip = 'skip'
    count = 'count'
    whyfound = 'whyfound'
    orderby = 'orderby'
    term = 'term'
    select = 'select'
    search_options = 'search_options'
    fuzzySearchOptions = 'fuzzySearchOptions'
    is_quoted = 'is_quoted'
    do_esh_escaping = 'do_esh_escaping'
    weight = 'weight'
    fuzzinessThreshold = 'fuzzinessThreshold'
    fuzzySearchOptions = 'fuzzySearchOptions'
    type = 'type'
    phrase = 'phrase'
    without_enclosing = 'without_enclosing'
    is_single_quoted = 'is_single_quoted'
    value = 'value'
    property = 'property'
    operator = 'operator'
    prefixOperator = 'prefixOperator'
    values = 'values'
    items = 'items'
    searchQueryFilter = 'searchQueryFilter'
    odataFilter = 'odataFilter'
    key = 'key'
    order = 'order'
    estimate = 'estimate'
    wherefound = 'wherefound'
    facetlimit = 'facetlimit'
    facets = 'facets'
    filteredgroupby = 'filteredgroupby'
    suggestTerm = 'suggestTerm'
    resourcePath = 'resourcePath'
    point = 'point'
    points = 'points'
    geometryCollection = 'geometryCollection'

def deserialize_objects(item):
    # print(item)
    if item[Constants.type] == StringValue.type:
        return StringValue(item)
    elif item[Constants.type] == Property.type:
        return Property(item)
    elif item[Constants.type] == Term.type:
        return Term(item)
    elif item[Constants.type] == Phrase.type:
        return Phrase(item)
    elif item[Constants.type] == NumberValue.type:
        return NumberValue(item)
    elif item[Constants.type] == BooleanValue.type:
        return BooleanValue(item)
    elif item[Constants.type] == Comparison.type:
        return Comparison(item)
    elif item[Constants.type] == ScopeComparison.type:
        return ScopeComparison(item)
    elif item[Constants.type] == Expression.type:
        return Expression(item)
    elif item[Constants.type] == PointValues.type:
        return PointValues(item)
    elif item[Constants.type] == MultiPointValues.type:
        return MultiPointValues(item)
    elif item[Constants.type] == LineStringValues.type:
        return LineStringValues(item)
    elif item[Constants.type] == CircularStringValues.type:
        return CircularStringValues(item)
    elif item[Constants.type] == MultiLineStringValues.type:
        return MultiLineStringValues(item)
    elif item[Constants.type] == PolygonValues.type:
        return PolygonValues(item)
    elif item[Constants.type] == MultiPolygonValues.type:
        return MultiPolygonValues(item)
    elif item[Constants.type] == GeometryCollectionValues.type:
        return GeometryCollectionValues(item)
    elif item[Constants.type] == CoveredByOperator.type:
        return CoveredByOperator(item)
    elif item[Constants.type] == IntersectsOperator.type:
        return IntersectsOperator(item)
    else:
        raise Exception('unknown item type: ' + item[Constants.type])

def escapeQuery(query: str) -> str:
    escapedQuery = query if query.strip() else ''
    if escapedQuery != '':
        for specialCharacter in reservedCharacters:
            if specialCharacter:
                if specialCharacter == "'":
                    escapedQuery = escapeSingleQuote(escapedQuery)
                else:
                    escapedQuery = escapedQuery.replace(specialCharacter, '\\' + specialCharacter)
        for specialWord in reservedWords:
            if escapedQuery == specialWord:
                escapedQuery = '\'' + specialWord + '\''
            if escapedQuery.startswith(specialWord + ' '):
                escapedQuery = '\'' + specialWord + '\' ' + escapedQuery[len(specialWord)+1:]
            if escapedQuery.endswith(' ' + specialWord):
                escapedQuery = escapedQuery[:-len(specialWord)] + '\'' + specialWord + '\''
            escapedQuery = escapedQuery.replace(f' {specialWord} ', f' \'{specialWord}\' ')

    if escapedQuery == '':
        escapedQuery = '*'
    return escapedQuery


def escapeSingleQuote(value: str) -> str:
    return value.replace("'", "''")

def escapeDoubleQuoteAndBackslash(value: str) -> str:
    return value.replace('\\', '\\\\').replace('"', '\\"')

def escapePhrase(value: str) -> str:
    return value.replace('\\','\\\\').replace('"','\\"').replace('*','\\*').replace('?','\\?').replace("'","''")

def addFuzzySearchOptions(item: str, searchOptions: dict) -> str:
    returnStatement = item
    if searchOptions:
        keys = searchOptions.keys()
        if Constants.fuzzinessThreshold in keys:
            returnStatement = returnStatement + '~' + str(searchOptions[Constants.fuzzinessThreshold])
        if Constants.fuzzySearchOptions in keys:
            if Constants.fuzzinessThreshold not in keys:
                returnStatement = returnStatement + '~0.8'
            returnStatement = returnStatement + '[' + searchOptions[Constants.fuzzySearchOptions] + ']'
        if Constants.weight in keys:
            returnStatement = returnStatement + '^' + str(searchOptions[Constants.weight])
    return returnStatement

class IToStatement:
    def to_statement(self):
        raise NotImplementedError

    def to_dict(self):
        return {'type': self.type, **self.__dict__}

class Property(IToStatement):
    type = 'Property'

    def __init__(self, item: dict):
        self.property = item[Constants.property]
        self.prefixOperator = item[Constants.prefixOperator] if Constants.prefixOperator in item.keys() else None

    def to_statement(self):
        if self.prefixOperator:
            return self.prefixOperator + ' ' + self.property
        else:
            return self.property

class Term(IToStatement):
    type = 'Term'
    def __init__(self, item):
        keys = item.keys()
        self.term = item[Constants.term]
        self.is_quoted = item[Constants.is_quoted] if Constants.is_quoted in keys else False
        self.do_esh_escaping = item[Constants.do_esh_escaping] if Constants.do_esh_escaping in keys else False
        self.search_options = item[Constants.search_options] if Constants.search_options in keys else None

    def to_statement(self):
        if self.do_esh_escaping:
            final_term = f'"{escapePhrase(self.term)}"'if self.is_quoted else escapeQuery(self.term)
        else:
            final_term = f'"{self.term}"' if self.is_quoted else self.term
        return addFuzzySearchOptions(final_term, self.search_options)

class Phrase(IToStatement):
    type = 'Phrase'

    def __init__(self, item: dict):
        keys = item.keys()
        self.phrase = item['phrase']
        self.search_options = item[Constants.search_options] if Constants.search_options in keys else None
        self.do_esh_escaping = item[Constants.do_esh_escaping] if Constants.do_esh_escaping in keys else True

    def to_statement(self):
        if self.do_esh_escaping:
            final_phrase = escapePhrase(self.phrase)
        else:
            final_phrase = self.phrase
        return addFuzzySearchOptions('\"' + final_phrase + '\"', self.search_options)


class StringValue(IToStatement):
    type = 'StringValue'
    def __init__(self, item: dict):
        keys = item.keys()
        self.value = item['value']
        self.is_quoted = item[Constants.is_quoted] if Constants.is_quoted in keys else False
        self.is_single_quoted = item[Constants.is_single_quoted] if Constants.is_single_quoted in keys else False
        self.without_enclosing = item[Constants.without_enclosing] if Constants.without_enclosing in keys else False

    def to_statement(self):
        #if self.without_enclosing:
        #    return String(Number.parseFloat(this.value));
        if self.is_quoted:
            return f'"{escapeDoubleQuoteAndBackslash(self.value)}"'
        if self.is_single_quoted:
            return f"'{escapeSingleQuote(self.value)}'"
        return self.value



class NumberValue(IToStatement):
    type = 'NumberValue'

    def __init__(self, item: dict):
        self.value = item[Constants.value]

    def to_statement(self):
        return f'{self.value}'

class BooleanValue(IToStatement):
    type = 'BooleanValue'

    def __init__(self, item: dict):
        self.value = item[Constants.value]

    def to_statement(self):
        return json.dumps(self.value)

class ScopeComparison(IToStatement):
    type = 'ScopeComparison'

    def __init__(self, item: dict):
        self.values = item[Constants.values]

    def to_statement(self):
        if len(self.values) == 1:
            return f'SCOPE:{self.values[0]}'
        else:
            scope_values = ' OR '.join(self.values)
            return f'SCOPE:({scope_values})'

class Expression:
    type = 'Expression'

    def __init__(self, item: dict ):
        self.items = list(map(deserialize_objects, item[Constants.items])) if 'items' in item else []
        self.operator = item[Constants.operator] if Constants.operator in item.keys() else ''

    def to_statement(self):
        if self.operator != '':
            connect_operator = f' {self.operator} '
        else:
            connect_operator = ' '
        # print(list(map(lambda x: x.to_statement(), self.items)))
        lst = list(map(lambda x: f'({x.to_statement()})' if isinstance(x, Expression) else x.to_statement(),\
            self.items))
        return connect_operator.join(lst)
        #return connect_operator.join(list(map(lambda x: x.to_statement(), self.items)))

    def to_dict(self):
        return {
            Constants.type: self.type,
            Constants.items: list(map(lambda x: x.to_dict(), self.items)),
            Constants.operator: self.operator
        }

class Comparison(IToStatement):
    type = 'Comparison'

    def __init__(self, item: dict):
        keys = item.keys()
        self.property = deserialize_objects(item[Constants.property])
        self.operator = item[Constants.operator]
        self.value = deserialize_objects(item[Constants.value]) if Constants.value in keys else None


    def to_statement(self):
        return f'{self.property.to_statement()}{self.operator}{self.value.to_statement()}'

    def to_dict(self):
        return {
            Constants.type: self.type,
            Constants.property: self.property.to_dict(),
            Constants.operator: self.operator,
            Constants.value: self.value.to_dict()
        }

class SpatialReferenceSystemsOperator(IToStatement):
    type = 'SpatialReferenceSystemsOperator'

    def __init__(self, item: dict):
        self.id = item[Constants.id] if Constants.id in item.keys() else None

    def to_statement(self):
        statement_value = ''
        if self.id:
            statement_value = '(' + str(self.id) + '):'
        return f':{statement_value}'


class SpatialReferenceSystemsOperatorBase(IToStatement):
    def __init__(self, functionName: str, id_ = None):
        self.functionName = functionName
        self.id = id_

    def to_statement(self) -> str:
        if self.id:
            return f':{self.functionName}({str(self.id)}):'
        else:
            return f':{self.functionName}:'

class WithinOperator(SpatialReferenceSystemsOperatorBase):
    type = 'WithinOperator'
    def __init__(self, item: dict):
        if Constants.id in item.keys():
            super().__init__('WITHIN', item[Constants.id])
        else:
            super().__init__('WITHIN')


class CoveredByOperator(SpatialReferenceSystemsOperatorBase):
    type = 'CoveredByOperator'
    def __init__(self, item: dict):
        if Constants.id in item.keys():
            super().__init__('COVERED_BY', item[Constants.id])
        else:
            super().__init__('COVERED_BY')

class IntersectsOperator(SpatialReferenceSystemsOperatorBase):
    type = 'IntersectsOperator'
    def __init__(self, item: dict):
        if Constants.id in item.keys():
            super().__init__('INTERSECTS', item[Constants.id])
        else:
            super().__init__('INTERSECTS')

def pointCoordinates(item: dict) -> str:
    return f'{item[Constants.x]} {item[Constants.y]}'

class PointValues(IToStatement):
    type = 'PointValues'

    def __init__(self, item: dict):
        self.point = item[Constants.point]
        self.search_options = item[Constants.search_options] if Constants.search_options in item.keys() else None

    def to_statement(self):
        return addFuzzySearchOptions(f'POINT({pointCoordinates(self.point)})', self.search_options)

class MultiPointValues(IToStatement):
    type = 'MultiPointValues'

    def __init__(self, item: dict):
        self.points = item[Constants.points]

    def to_statement(self) -> str:
        multipoint_value = (',').join(list(map(lambda point: '(' + pointCoordinates(point) + ')', self.points)))
        return f'MULTIPOINT({multipoint_value})'

def toLineStringArray(points: list) -> str:
    line_string_array_value = ', '.join(list(map(pointCoordinates, points)))
    return f'({line_string_array_value})'

def toPolygonStringArray(polygon: list) -> str:
    polygon_string_value = ', '.join(list(map(toLineStringArray, polygon)))
    return f'({polygon_string_value})'
class LineStringValuesBase(IToStatement):
    def __init__(self, valuesType: str, item: dict):
        self.valuesType = valuesType
        self.points = item[Constants.points]

    def to_statement(self):
        return f'{self.valuesType}{toLineStringArray(self.points)}'

class LineStringValues(LineStringValuesBase):
    type = 'LineStringValues'

    def __init__(self, item: dict):
        super().__init__('LINESTRING', item)

class CircularStringValues(LineStringValuesBase):
    type = 'CircularStringValues'

    def __init__(self, item: dict):
        super().__init__('CIRCULARSTRING', item)

class MultiLineStringValues(LineStringValuesBase):
    type = 'MultiLineStringValues'

    def __init__(self, item: dict):
        super().__init__('MULTILINESTRING', item)

class PolygonValuesBase(IToStatement):
    def __init__(self, valuesType: str, item: dict):
        self.valuesType = valuesType
        self.points = item[Constants.points]

    def to_statement(self):
        return f'{self.valuesType}{toPolygonStringArray(self.points)}'

class PolygonValues(PolygonValuesBase):
    type = 'PolygonValues'

    def __init__(self, item: dict):
        super().__init__('POLYGON', item)

class MultiPolygonValues(PolygonValuesBase):
    type = 'MultiPolygonValues'

    def __init__(self, item: dict):
        super().__init__('MULTIPOLYGON', item)

class GeometryCollectionValues(IToStatement):
    type = 'GeometryCollectionValues'

    def __init__(self, item: list):
        self.geometryCollection = \
            list(map(deserialize_objects, item[Constants.geometryCollection]))

    def to_statement(self) -> str:
        geometry_collection_values = ', '.join(list(map(lambda geometry: geometry.to_statement(),\
            self.geometryCollection)))
        return f'GEOMETRYCOLLECTION({geometry_collection_values})'

class IESSearchOptions(IToStatement):
    def __init__(self, item: dict):
        keys = item.keys()
        self.top = item[Constants.top] if Constants.top in keys else 10
        self.skip = item[Constants.skip] if Constants.skip in keys else None
        self.count = item[Constants.count] if Constants.count in keys else None
        self.searchQueryFilter = \
            deserialize_objects(item[Constants.searchQueryFilter]) if Constants.searchQueryFilter in keys else None
        self.odataFilter = \
            deserialize_objects(item[Constants.odataFilter]) if Constants.odataFilter in keys else None
        self.whyfound = item[Constants.whyfound] if Constants.whyfound in keys else None
        self.select = item[Constants.select] if Constants.select in keys else None
        self.orderby = item[Constants.orderby] if Constants.orderby in keys else None
        self.estimate = item[Constants.estimate] if Constants.estimate in keys else None
        self.wherefound = item[Constants.wherefound] if Constants.wherefound in keys else None
        self.facetlimit = item[Constants.facetlimit] if Constants.facetlimit in keys else None
        self.facets = item[Constants.facets] if Constants.facets in keys else None
        self.filteredgroupby = item[Constants.filteredgroupby] if Constants.filteredgroupby in keys else None
        self.suggestTerm = item[Constants.suggestTerm] if Constants.suggestTerm in keys else None
        self.resourcePath = item[Constants.resourcePath] if Constants.resourcePath in keys else None

    def __setattr__(self, name, value):
        if name in [Constants.count, Constants.whyfound, Constants.wherefound, Constants.estimate,\
            Constants.filteredgroupby] and value is not None and not isinstance(value, bool):
            raise TypeError(name + ' must be a boolean')
        elif name in [Constants.top, Constants.skip, Constants.facetlimit] and value is not None\
            and not isinstance(value, int):
            raise TypeError(name + ' must be an int')
        elif name in [Constants.searchQueryFilter, Constants.odataFilter] and value is not None\
            and not isinstance(value, Expression):
            raise TypeError(name + ' must be an Expression')
        elif name in [Constants.select, Constants.orderby, Constants.facets] and value is not None\
            and not isinstance(value, list):
            raise TypeError(name + ' must be a list')
        super().__setattr__(name, value)

    def to_statement(self):
        esh = '/$all' if self.resourcePath is None else self.resourcePath
        searchQueryFilter = self.searchQueryFilter.to_statement() if self.searchQueryFilter else ''
        odataFilter = self.odataFilter.to_statement() if self.odataFilter else ''
        if self.suggestTerm is not None:
            escaped_suggested_term = self.suggestTerm.replace("'","''")
            esh += f"/GetSuggestion(term='{escaped_suggested_term}')"
        if esh.startswith('/$all'):
            esh += '?'
            if self.top is not None:
                esh += f'${Constants.top}={self.top}'
            if self.skip is not None:
                esh += f'&${Constants.skip}={self.skip}'
            if self.count is not None:
                esh += f'&${Constants.count}={json.dumps(self.count)}'
            if searchQueryFilter != '' or odataFilter != '':
                if odataFilter != '':
                    esh += f"&$apply=filter(Search.search(query='{searchQueryFilter}')) and {odataFilter}"
                else:
                    esh += f"&$apply=filter(Search.search(query='{searchQueryFilter}'))"
            if self.whyfound is not None:
                esh += f'&{Constants.whyfound}={json.dumps(self.whyfound)}'
            if self.select is not None:
                select_value = ','.join(self.select)
                esh += f'&${Constants.select}={select_value}'
            if self.orderby is not None:
                order_by_value = ','.join(list(map(lambda x: f'{x[Constants.key]} {x[Constants.order]}' \
                    if Constants.order in x.keys() else x[Constants.key], self.orderby)))
                esh += f'&${Constants.orderby}={order_by_value}'
            if self.estimate is not None:
                esh += f'&{Constants.estimate}={json.dumps(self.estimate)}'
            if self.wherefound is not None:
                esh += f'&{Constants.wherefound}={json.dumps(self.wherefound)}'
            if self.facetlimit is not None:
                esh += f'&{Constants.facetlimit}={json.dumps(self.facetlimit)}'
            if self.facets is not None:
                facets_value = ','.join(self.facets)
                esh += f'&{Constants.facets}={facets_value}'
            if self.filteredgroupby is not None:
                esh += f'&{Constants.filteredgroupby}={json.dumps(self.filteredgroupby)}'
        return esh

    def to_dict(self):
        return_object = {}
        if self.top: return_object[Constants.top] = self.top
        if self.skip: return_object[Constants.skip] = self.skip
        if self.count: return_object[Constants.count] = self.count
        if self.searchQueryFilter: return_object[Constants.searchQueryFilter] = self.searchQueryFilter.to_dict()
        if self.whyfound: return_object[Constants.whyfound] = self.whyfound
        if self.select: return_object[Constants.select] = self.select
        if self.orderby: return_object[Constants.orderby] = self.orderby
        if self.estimate: return_object[Constants.estimate] = self.estimate
        if self.wherefound: return_object[Constants.wherefound] = self.wherefound
        if self.facetlimit: return_object[Constants.facetlimit] = self.facetlimit
        if self.facets: return_object[Constants.facets] = self.facets
        if self.filteredgroupby: return_object[Constants.filteredgroupby] = self.filteredgroupby
        if self.suggestTerm: return_object[Constants.suggestTerm] = self.suggestTerm
        return return_object


if __name__ == '__main__':

    m_items = [StringValue({'value':'www'}),StringValue({'value':'222'}),StringValue({'value':'333'})]
    #bbb = list(map(lambda x: x.to_statement(), m_items))
    #print(json.dumps(bbb))
    #connect_operator = '_'
    #print(connect_operator.join(bbb))

    comp = {Constants.type: 'Comparison', 'property': {'type':'Property', 'property': 'language'}, \
        'operator': ':EQ:', 'value': { Constants.type: 'StringValue', 'value': 'Python'}}
    aas = deserialize_objects(comp)
    assert aas.to_statement() == 'language:EQ:Python'


    aa = IESSearchOptions({})
    aa.top=23
    aa.searchQueryFilter=deserialize_objects({Constants.type: 'Expression', 'items' : [{'type': 'StringValue', \
        'value': 'aaa'},{'type': 'StringValue', 'value': 'bbb'}], 'operator': 'AND'})
    assert aa.to_statement() == "/$all?$top=23&$apply=filter(Search.search(query='aaa AND bbb'))"



    exp1 = Expression({'items': [{Constants.type: 'StringValue', 'value': 'MMMM'},\
        {Constants.type: 'StringValue', 'value': 'KKK'}], 'operator': 'OR'})
    assert exp1.to_statement() == 'MMMM OR KKK'

    exp2 = Expression({})
    exp2.operator = 'AND'
    exp2.items.append(StringValue({'value':'mannheim'}))
    exp2.items.append(StringValue({'value':'heidelberg'}))
    assert exp2.to_statement() == 'mannheim AND heidelberg'


    json_body={
        'top': 10,
        'count': True,
        'whyfound': True,
        'select': ['id', 'name'],
        'estimate': True,
        'wherefound': True,
        'facetlimit': 4,
        'facets': ['city', 'land'],
        'filteredgroupby': False,
        'orderby': [
                {
                    'key': 'city',
                    'order': 'ASC'
                },
                {
                    'key': 'language',
                    'order': 'DESC'
                },
                {
                    'key': 'land'
                }
            ],
        'searchQueryFilter': {Constants.type: 'Expression', 'items' : [\
            {Constants.type: 'ScopeComparison', 'values': ['S1']},\
            {Constants.type: 'Expression', 'items' :[\
                {'type': 'StringValue', 'value': 'test'},\
                {'type': 'StringValue', 'value': 'function'}], 'operator': 'OR'}, \
                {'type': 'StringValue', 'value': 'aaa'},{'type': 'StringValue', 'value': 'bbb'}\
            ], 'operator': 'AND'},
        'odataFilter': {Constants.type: 'Expression', 'items' : [\
            {Constants.type: 'Comparison',\
                'property':  {Constants.type:'Property', 'property':'flag'}, \
                'operator': ' eq ', \
                'value': { Constants.type: 'StringValue', \
                    'value': 'ACTIVE','is_single_quoted': True}}], 'operator': ''}
        }


    es_objects = IESSearchOptions(json_body)
    print(es_objects.to_statement())
    #print(json.dumps(es_objects.searchQueryFilter.to_dict(), indent=4))
    print(json.dumps(es_objects.to_dict(), indent=4))
    expected_statement = '/$all?$top=10&$count=true&$apply=filter(' \
        'Search.search(query=\'SCOPE:S1 AND (test OR function)' \
        ' AND aaa AND bbb\')) and flag eq \'ACTIVE\'&whyfound=true&$select=id,name&$orderby=city ASC,language DESC,' \
        'land&estimate=true&wherefound=true&facetlimit=4&facets=city,land&filteredgroupby=false'
    assert es_objects.to_statement() == expected_statement

    string_value_dict={
        'value': 'sss',
        Constants.is_quoted: True
    }
    sv = StringValue(string_value_dict)
    # print(sv.__dict__)

    # print(json.dumps(sv.__dict__))
    # print(json.dumps(exp2.__dict__, indent=4))
    org_str = "a*\\a\\a*b?b'c'd?\"ee\"ff"
    #print(org_str)
    #print(escapePhrase(org_str))


    esc_query = 'n AND a OR c'
    #print(escapeQuery(esc_query))

    term_definition = {Constants.term: 'mannh"eim', Constants.do_esh_escaping: True,\
        Constants.search_options: { \
            Constants.fuzzinessThreshold:0.5,\
            Constants.weight:0.9,\
            Constants.fuzzySearchOptions:'search=typeahead'}}
    term = Term(term_definition)
    print(term.to_statement())
    assert term.to_statement() == 'mannh"eim~0.5[search=typeahead]^0.9'


    phrase_definition = {'phrase': 'heidelberg', \
        Constants.search_options: {\
            Constants.fuzzinessThreshold:0.5,\
            Constants.weight:0.9,\
            Constants.fuzzySearchOptions:'search=typeahead'}}
    phrase = Phrase(phrase_definition)
    assert phrase.to_statement() == '"heidelberg"~0.5[search=typeahead]^0.9'



    suggest_json_body={
        'suggestTerm': 'bas'
    }
    suggest_es_objects = IESSearchOptions(suggest_json_body)
    print(suggest_es_objects.to_statement())
    assert suggest_es_objects.to_statement() == "/$all/GetSuggestion(term='bas')?$top=10"


    metadata_json_body={
        'resourcePath': '/$metadata'
    }
    metadata_es_objects = IESSearchOptions(metadata_json_body)
    print(metadata_es_objects.to_statement())
    assert metadata_es_objects.to_statement() == '/$metadata'



    assert WithinOperator({}).to_statement() == ':WITHIN:'
    assert WithinOperator({'id':4}).to_statement() == ':WITHIN(4):'

    assert CoveredByOperator({}).to_statement() == ':COVERED_BY:'
    assert CoveredByOperator({'id':5}).to_statement() == ':COVERED_BY(5):'

    assert IntersectsOperator({}).to_statement() == ':INTERSECTS:'
    assert IntersectsOperator({'id':6}).to_statement() == ':INTERSECTS(6):'

    assert pointCoordinates({'x': 3.4, 'y': 4.25}) == '3.4 4.25'


    assert PointValues({'point': {'x': 3.4, 'y': 4.25}}).to_statement() == 'POINT(3.4 4.25)'
    assert PointValues({'point': {'x': 3.4, 'y': 4.25}, 'search_options': {'weight': 3.2}})\
        .to_statement() == 'POINT(3.4 4.25)^3.2'


    assert MultiPointValues({'points':[{'x': 3.4, 'y': 4.25},{'x': 3.6, 'y': 4.28}]})\
        .to_statement() == 'MULTIPOINT((3.4 4.25),(3.6 4.28))'

    assert toLineStringArray([{'x': 3.4, 'y': 4.25},{'x': 3.6, 'y': 4.28}]) == '(3.4 4.25, 3.6 4.28)'
    assert LineStringValues({'points':[{'x': 3.4, 'y': 4.25},{'x': 3.6, 'y': 4.28}]})\
        .to_statement() == 'LINESTRING(3.4 4.25, 3.6 4.28)'
    assert CircularStringValues({'points':[{'x': 3.4, 'y': 4.25},{'x': 3.6, 'y': 4.28},{'x': 3.7, 'y': 4.78},\
        {'x': 3.4, 'y': 4.25}]}).to_statement() == 'CIRCULARSTRING(3.4 4.25, 3.6 4.28, 3.7 4.78, 3.4 4.25)'
    assert MultiLineStringValues({'points':[{'x': 3.4, 'y': 4.25},{'x': 3.6, 'y': 4.28},{'x': 3.7, 'y': 4.78},\
        {'x': 3.4, 'y': 4.25}]}).to_statement() == 'MULTILINESTRING(3.4 4.25, 3.6 4.28, 3.7 4.78, 3.4 4.25)'


    assert toPolygonStringArray([
        [{'x': 3.4, 'y': 4.25},{'x': 3.6, 'y': 4.28},{'x': 3.7, 'y': 4.78}],
        [{'x': 1.4, 'y': 2.25},{'x': 1.6, 'y': 5.28},{'x': 2.7, 'y': 6.78}]
        ]) == '((3.4 4.25, 3.6 4.28, 3.7 4.78), (1.4 2.25, 1.6 5.28, 2.7 6.78))'
    assert PolygonValues({'points':[
        [{'x': 3.4, 'y': 4.25},{'x': 3.6, 'y': 4.28},{'x': 3.7, 'y': 4.78}],
        [{'x': 1.4, 'y': 2.25},{'x': 1.6, 'y': 5.28},{'x': 2.7, 'y': 6.78}]
        ]}).to_statement() == 'POLYGON((3.4 4.25, 3.6 4.28, 3.7 4.78), (1.4 2.25, 1.6 5.28, 2.7 6.78))'

    assert GeometryCollectionValues({'geometryCollection': [
        {'type': 'LineStringValues','points':[{'x': 3.4, 'y': 4.25},{'x': 3.6, 'y': 4.28}]},
        {'type': 'PolygonValues','points':[
        [{'x': 3.4, 'y': 4.25},{'x': 3.6, 'y': 4.28},{'x': 3.7, 'y': 4.78}],
        [{'x': 1.4, 'y': 2.25},{'x': 1.6, 'y': 5.28},{'x': 2.7, 'y': 6.78}]
        ]}
        ]} ).to_statement() == 'GEOMETRYCOLLECTION(LINESTRING(3.4 4.25, 3.6 4.28), ' \
            'POLYGON((3.4 4.25, 3.6 4.28, 3.7 4.78), (1.4 2.25, 1.6 5.28, 2.7 6.78)))'
    # deserialization
    json_circular_string = {'type': 'CircularStringValues', 'points':[{'x': 3.4, 'y': 4.25},\
        {'x': 3.6, 'y': 4.28},{'x': 3.7, 'y': 4.78},{'x': 3.4, 'y': 4.25}]}
    assert deserialize_objects(json_circular_string).to_statement() == \
        'CIRCULARSTRING(3.4 4.25, 3.6 4.28, 3.7 4.78, 3.4 4.25)'


    print(StringValue({'value':'aaa'}).to_dict())
    print(NumberValue({'value':3.2}).to_dict())
    print(BooleanValue({'value':True}).to_dict())
    print(Term({'term':'mannheim'}).to_dict())
    print(Phrase({'phrase':'to be'}).to_dict())
    print(Property({'property':'language'}).to_dict())

    comparison_object = deserialize_objects({Constants.type: 'Comparison','property':  \
        {Constants.type:'Property', 'property':'flag'}, 'operator': ':EQ(S):', \
            'value': { Constants.type: 'StringValue', 'value': 'ACTIVE'}})
    print(comparison_object.to_statement())
    print(comparison_object.to_dict())

    assert escapePhrase('aaa?bbb') == 'aaa\\?bbb'

    print(' -----> everything fine <----- ')
