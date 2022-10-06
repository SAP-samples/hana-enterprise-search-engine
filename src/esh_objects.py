"""Classes to define a query"""
from enum import Enum
from lib2to3.pytree import Base
from typing import List, Literal, Annotated
import json
from pydantic import BaseModel, Field

#class EshBaseModel(BaseModel):
#    class Config:
#        extra = 'forbid'


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
    searchOptions = 'searchOptions'
    fuzzySearchOptions = 'fuzzySearchOptions'
    isQuoted = 'isQuoted'
    doEshEscaping = 'doEshEscaping'
    weight = 'weight'
    fuzzinessThreshold = 'fuzzinessThreshold'
    type = 'type'
    phrase = 'phrase'
    withoutEnclosing = 'withoutEnclosing'
    isSingleQuoted = 'isSingleQuoted'
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
    namespace = 'namespace'
    coordinates = 'coordinates'
    geometries = 'geometries'
    entity = 'entity'
    attribute = 'attribute'
    alias = 'alias'

def serialize_geometry_collection(collection):
    try:
        collection[0]
        return f"({','.join(list(map(lambda i: serialize_geometry_collection(i), collection)))})"
    except TypeError:
        return f"{' '.join(list(map(lambda i: str(i), collection)))}"

def deserialize_objects(item):
    # print(item)
    if type(item) is dict:
        if Constants.type in item.keys():
            if item[Constants.type] == StringValue.__name__:
                return StringValue(item)
            elif item[Constants.type] == Property.__name__:
                return Property(item)
            elif item[Constants.type] == Term.__name__:
                return Term(item)
            elif item[Constants.type] == Phrase.__name__:
                return Phrase(item)
            elif item[Constants.type] == NumberValue.__name__:
                return NumberValue(item)
            elif item[Constants.type] == BooleanValue.__name__:
                return BooleanValue(item)
            elif item[Constants.type] == Comparison.__name__:
                return Comparison(item)
            elif item[Constants.type] == ScopeComparison.__name__:
                return ScopeComparison(item)
            elif item[Constants.type] == Expression.__name__:
                return Expression(item)
            elif item[Constants.type] == CoveredByOperator.__name__:
                return CoveredByOperator(item)
            elif item[Constants.type] == IntersectsOperator.__name__:
                return IntersectsOperator(item)
            elif item[Constants.type] == Path.__name__:
                return Path(item)
            elif item[Constants.type] == MultiValues.__name__:
                return MultiValues({Constants.items: list(map(lambda item: deserialize_objects(item), item[Constants.items]))})
            elif item[Constants.type] == Point.__name__:
                return Point(item)
            elif item[Constants.type] == LineString.__name__:
                return LineString(item)
            elif item[Constants.type] == Polygon.__name__:
                return Polygon(item)
            elif item[Constants.type] == MultiPoint.__name__:
                return MultiPoint(item)
            elif item[Constants.type] == MultiLineString.__name__:
                return MultiLineString(item)
            elif item[Constants.type] == MultiPolygon.__name__:
                return MultiPolygon(item)
            elif item[Constants.type] == CircularString.__name__:
                return CircularString(item)
            elif item[Constants.type] == GeometryCollection.__name__:
                return GeometryCollection({Constants.geometries: list(map(lambda geometry: deserialize_objects(geometry), item[Constants.geometries]))})
            else:
                raise Exception('unknown item type: ' + item[Constants.type])
        else:
            raise Exception('missing mandatory property type: ' + json.dumps(item))
    else:
        return item

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
    def __init__(self):
        self.type = self.__class__.__name__

    def to_statement(self):
        raise NotImplementedError

    def to_dict(self):
        return {Constants.type: self.type, **self.__dict__}

class OrderBySorting(str, Enum):
    asc = "ASC"
    desc = "DESC"

class OrderBy(BaseModel):
    key: str
    order: OrderBySorting | None = None

    def to_statement(self):
        if self.order:
            return f'{self.key} {self.order}'
        else:
            return self.key
class Property(BaseModel):
    type: Literal['Property'] = 'Property'
    property: str
    prefixOperator: str | None = None

    def to_statement(self):
        property_value = self.property if not type(self.property) is list else ".".join(self.property)
        if self.prefixOperator:
            return self.prefixOperator + ' ' + property_value
        else:
            return property_value

class Term(BaseModel):
    type: Literal['Term'] = 'Term'
    term: str 
    isQuoted: bool | None = False
    doEshEscaping: bool | None = False
    searchOptions: str | None = None

    def from_dict(self, item):
        super().__init__()
        keys = item.keys()
        self.term = item[Constants.term]
        self.isQuoted = item[Constants.isQuoted] if Constants.isQuoted in keys else False
        self.doEshEscaping = item[Constants.doEshEscaping] if Constants.doEshEscaping in keys else False
        self.searchOptions = item[Constants.searchOptions] if Constants.searchOptions in keys else None

    def to_statement(self):
        if self.doEshEscaping:
            final_term = f'"{escapePhrase(self.term)}"'if self.isQuoted else escapeQuery(self.term)
        else:
            final_term = f'"{self.term}"' if self.isQuoted else self.term
        return addFuzzySearchOptions(final_term, self.searchOptions)

class Phrase(BaseModel):
    type: Literal['Phrase'] = 'Phrase'
    phrase: str
    searchOptions: str = None
    doEshEscaping: bool = True

    def to_statement(self):
        if self.doEshEscaping:
            final_phrase = escapePhrase(self.phrase)
        else:
            final_phrase = self.phrase
        return addFuzzySearchOptions('\"' + final_phrase + '\"', self.searchOptions)


class StringValue(BaseModel):
    type: Literal['StringValue'] = 'StringValue'
    value: str
    isQuoted: bool = False
    isSingleQuoted: bool = False
    withoutEnclosing: bool = False

    def to_statement(self):
        #if self.withoutEnclosing:
        #    return String(Number.parseFloat(this.value));
        if self.isQuoted:
            return f'"{escapeDoubleQuoteAndBackslash(self.value)}"'
        if self.isSingleQuoted:
            return f"'{escapeSingleQuote(self.value)}'"
        return self.value



class NumberValue(BaseModel):
    type: Literal['NumberValue'] = 'NumberValue'
    value: int | float

    def to_statement(self):
        return f'{self.value}'

class BooleanValue(BaseModel):
    type: Literal['BooleanValue'] = 'BooleanValue'
    value: bool

    def to_statement(self):
        return json.dumps(self.value)

class ScopeComparison(BaseModel):
    type: Literal['ScopeComparison'] = 'ScopeComparison'
    values: str | List[str]

    def to_statement(self):
        if isinstance(self.values, str):
            return f'SCOPE:{scope_values}'
        elif len(self.values) == 1:
            return f'SCOPE:{self.values[0]}'
        else:
            scope_values = ' OR '.join(self.values)
            return f'SCOPE:({scope_values})'

class Comparison(BaseModel):
    type: Literal['Comparison'] = 'Comparison'
    property: str | Property
    operator: str
    value: str | StringValue | None = None

    def to_statement(self):
        property_to_statement = getattr(self.property, "to_statement", None)
        if callable(property_to_statement):
            property = self.property.to_statement()
        else:
            property = self.property
        value_to_statement = getattr(self.value, "to_statement", None)
        if callable(value_to_statement):
            value = self.value.to_statement()
        else:
            value = self.value
        return f'{property}{self.operator}{value}'
        

    def to_dict(self):
        return {
            Constants.type: self.type,
            Constants.property: self.property.to_dict(),
            Constants.operator: self.operator,
            Constants.value: self.value.to_dict()
        }

 
            
class Expression(BaseModel):
    type: Literal['Expression'] = 'Expression'
    operator: str = ''
    items: List[Annotated[Comparison | Term | StringValue,  Field(discriminator='type')]] | None = None

    
    def get_expression_statement(self, expression_item):
        if isinstance(expression_item, Expression): 
            return f'({expression_item.to_statement()})'
        else:
            try:
                return expression_item.to_statement()
            except: 
                return f'{expression_item}'

    def to_statement(self):
        if self.operator != '':
            connect_operator = f' {self.operator} '
        else:
            connect_operator = ' '
        statements = list(map(lambda item: self.get_expression_statement(item), self.items))
        if len(self.items) > 1 and not isinstance(self.items[0], Expression) and not isinstance(self.items[0], ScopeComparison):
            return f"({connect_operator.join(statements)})"
        return connect_operator.join(statements)

    def to_dict(self):
        return {
            Constants.type: self.type,
            Constants.items: list(map(lambda x: x.to_dict(), self.items)),
            Constants.operator: self.operator
        }

'''
class SpatialReferenceSystemsOperator(EshBaseModel):

    id: int = None

    def to_statement(self):
        statement_value = ''
        if self.id:
            statement_value = '(' + str(self.id) + '):'
        return f':{statement_value}'


class SpatialReferenceSystemsOperatorBase(IToStatement):

    functionName: str
    id: int = None

    def to_statement(self) -> str:
        if self.id:
            return f':{self.functionName}({str(self.id)}):'
        else:
            return f':{self.functionName}:'
'''
class WithinOperator(BaseModel):
    type: Literal['WithinOperator'] = 'WithinOperator'
    id: int = None

    def to_statement(self) -> str:
        if self.id:
            return f':WITHIN({str(self.id)}):'
        else:
            return ':WITHIN:'


class CoveredByOperator(BaseModel):
    type: Literal['CoveredByOperator'] = 'CoveredByOperator'
    id: int = None

    def to_statement(self) -> str:
        if self.id:
            return f':COVERED_BY({str(self.id)}):'
        else:
            return ':COVERED_BY:'

class IntersectsOperator(BaseModel):
    type: Literal['IntersectsOperator'] = 'IntersectsOperator'
    id: int = None

    def to_statement(self) -> str:
        if self.id:
            return f':INTERSECTS({str(self.id)}):'
        else:
            return ':INTERSECTS:'

class GeometryBase(BaseModel):
    coordinates: list
    searchOptions: dict | None = None

    def to_statement(self):
        try:
            self.coordinates[0][0]
            return addFuzzySearchOptions(f'{self.__class__.__name__.upper()}{serialize_geometry_collection(self.coordinates)}', self.searchOptions)
        except TypeError:
            #return f"{' '.join(list(map(lambda i: str(i), collection)))}"
            return addFuzzySearchOptions(f'{self.__class__.__name__.upper()}({serialize_geometry_collection(self.coordinates)})', self.searchOptions)

class Point(GeometryBase):
    type: Literal['Point'] = 'Point'

class LineString(GeometryBase):
    type: Literal['LineString'] = 'LineString'

class CircularString(GeometryBase):
    type: Literal['CircularString'] = 'CircularString'

class Polygon(GeometryBase):
    type: Literal['Polygon'] = 'Polygon'

class MultiPoint(GeometryBase):
    type: Literal['MultiPoint'] = 'MultiPoint'

class MultiLineString(GeometryBase):
    type: Literal['MultiLineString'] = 'MultiLineString'

class MultiPolygon(GeometryBase):
    type: Literal['MultiPolygon'] = 'MultiPolygon'

class GeometryCollection(BaseModel):
    type: Literal['GeometryCollection'] = 'GeometryCollection'
    geometries: list[GeometryBase]
    def __init__(self, item: dict):
        super().__init__()
        self.geometries = item[Constants.geometries]

    def to_statement(self):
        return f"{self.__class__.__name__.upper()}({','.join(list(map(lambda i: i.to_statement(), self.geometries)))})" 

    def to_dict(self):
        return {Constants.type: self.type, Constants.geometries: list(map(lambda geometry: geometry.to_dict(), self.geometries))}


class Path(BaseModel):
    type: Literal['Path'] = 'Path'
    entity: str | None = None
    namespace: str | None = None
    alias: str | None = None
    attribute: str | None = None


    def to_statement(self) -> str:
        return f'Path({self.namespace},{self.entity},{self.alias},{self.attribute})'

class MultiValues(BaseModel):
    type: Literal['MultiValues'] = 'MultiValues'    
    items: List[BaseModel] = []
    
    def to_dict(self) -> dict:
       return {Constants.type: self.type, Constants.items: list(map(lambda item: item.to_dict(), self.items)) }

    def to_statement(self) -> str:
        return json.dumps(self.to_dict())

'''
class IESSearchOptions(IToStatement):
    def __init__(self, item: dict = {}):
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
'''
class EshObject(BaseModel):
    top: int | None = 10
    skip: int | None = None
    count: bool | None = None
    searchQueryFilter: Expression | None = None
    odataFilter:  Expression | Comparison | None = None
    whyfound: bool | None = None
    select: list[str] | None = None
    orderby: List[OrderBy] | None = None
    estimate: bool | None = None
    wherefound: bool | None = None
    facetlimit: int | None = None
    facets: list[str] | None = None
    filteredgroupby: bool | None = None
    suggestTerm: str | None = None
    resourcePath:str | None = None

    class Config:
        extra = 'forbid'

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
                #order_by_value = ','.join(list(map(lambda x: f'{x[Constants.key]} {x[Constants.order]}' \
                #    if x.order is not None  else x[Constants.key], self.orderby)))

                order_by_value = ','.join(list(map(lambda x: x.to_statement(), self.orderby)))
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
    assert aa.to_statement() == "/$all?$top=23&$apply=filter(Search.search(query='(aaa AND bbb)'))"



    exp1 = Expression({'items': [{Constants.type: 'StringValue', 'value': 'MMMM'},\
        {Constants.type: 'StringValue', 'value': 'KKK'}], 'operator': 'OR'})
    assert exp1.to_statement() == '(MMMM OR KKK)'

    exp2 = Expression({})
    exp2.operator = 'AND'
    exp2.items.append(StringValue({'value':'mannheim'}))
    exp2.items.append(StringValue({'value':'heidelberg'}))
    assert exp2.to_statement() == '(mannheim AND heidelberg)'


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
                    'value': 'ACTIVE','isSingleQuoted': True}}], 'operator': ''}
        }


    es_objects = IESSearchOptions(json_body)
    print(es_objects.to_statement())
    #print(json.dumps(es_objects.searchQueryFilter.to_dict(), indent=4))
    print(json.dumps(es_objects.to_dict(), indent=4))
    expected_statement = '/$all?$top=10&$count=true&$apply=filter(' \
        'Search.search(query=\'SCOPE:S1 AND ((test OR function))' \
        ' AND aaa AND bbb\')) and flag eq \'ACTIVE\'&whyfound=true&$select=id,name&$orderby=city ASC,language DESC,' \
        'land&estimate=true&wherefound=true&facetlimit=4&facets=city,land&filteredgroupby=false'
    assert es_objects.to_statement() == expected_statement

    string_value_dict={
        'value': 'sss',
        Constants.isQuoted: True
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

    term_definition = {Constants.term: 'mannh"eim', Constants.doEshEscaping: True,\
        Constants.searchOptions: { \
            Constants.fuzzinessThreshold:0.5,\
            Constants.weight:0.9,\
            Constants.fuzzySearchOptions:'search=typeahead'}}
    term = Term(term_definition)
    print(term.to_statement())
    assert term.to_statement() == 'mannh"eim~0.5[search=typeahead]^0.9'


    phrase_definition = {'phrase': 'heidelberg', \
        Constants.searchOptions: {\
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

    person = Path({'entity': "Person"})
    print(person.to_statement())
    # json_path_person = {'type': 'Path', 'value':{'type': 'StringValue', 'value': 'mannheim'}}
    json_path_person = {'type': 'Path', 'entity': 'Person','attribute':['m1','m2']}
    print(deserialize_objects(json_path_person).to_statement())
    print(json.dumps(deserialize_objects(json_path_person).to_dict()))
    assert deserialize_objects(json_path_person).to_statement() == "Path(None,Person,None,['m1', 'm2'])"
    multiValuesA = MultiValues({'items':[person,deserialize_objects(json_path_person)]})
    print(multiValuesA.to_statement())

    multi_values = MultiValues({'items': [StringValue({"value":"one"}),StringValue({"value":"two"})]})
    # multi_values_json = json.dumps(multi_values.to_dict())
    deserialized_object_multi_values = deserialize_objects(multi_values.to_dict())
    assert deserialized_object_multi_values.type == "MultiValues"
    assert deserialized_object_multi_values.items[0].type == "StringValue"
    assert deserialized_object_multi_values.items[1].type == "StringValue"
    # print(multiValues.to_statement())
    # print(json.dumps(StringValue({'value':'vv'}).to_dict()))
    json_expression = '''
        {
            "type": "Expression",
            "items": [
                {
                    "type": "Property",
                    "property": "city"
                },{
                    "type": "Property",
                    "property": "country"
                }
            ]
        }
    '''
    deserialized_object_expression = deserialize_objects(json.loads(json_expression))
    assert deserialized_object_expression.type == Expression.__name__
    print(json.dumps(deserialized_object_expression.to_dict()))
    print(deserialized_object_expression.to_statement())

    json_property = '''
        {
            "type": "Property",
            "property": "city"
        }
    '''
    deserialized_object_property = deserialize_objects(json.loads(json_property))
    assert deserialized_object_property.type == Property.__name__
    print(json.dumps(deserialized_object_property.to_dict()))

    json_property_with_array = '''
        {
            "type": "Property",
            "property": ["city", "ok"]
        }
    '''
    deserialized_object_property_with_array = deserialize_objects(json.loads(json_property_with_array))
    assert deserialized_object_property_with_array.type == Property.__name__
    print(json.dumps(deserialized_object_property_with_array.to_dict()))

    json_comparison = '''
            {
                "type": "Comparison",
                "property": {
                    "type": "Property",
                    "property": "city"
                },
                "operator": ":",
                "value": {
                    "type": "StringValue",
                    "value": "Mannheim"
                }
            }
        '''
    deserialized_object_comparison = deserialize_objects(json.loads(json_comparison))
    assert deserialized_object_comparison.type == Comparison.__name__

    print(json.dumps(deserialized_object_comparison.to_dict()))

    json_multi_values = '''
        {
            "type": "MultiValues",
            "items":[
                {
                    "type": "StringValue", 
                    "value": "one", 
                    "isQuoted": false, 
                    "isSingleQuoted": false, 
                    "withoutEnclosing": false
                }, 
                {
                    "type": "StringValue", 
                    "value": "two", 
                    "isQuoted": false, 
                    "isSingleQuoted": false, 
                    "withoutEnclosing": false
                }
            ]
        }
    '''
    des_obj = deserialize_objects(json.loads(json_multi_values))
    assert des_obj.type == "MultiValues"
    print(json.dumps(des_obj.to_dict()))


    pathEntity1 = Path({'namespace':'N1','entity':'E1','path_index': 1,'attribute':'a1'})
    pathEntity2 = Path({'namespace':'N1','entity':'E2','path_index': 2,'attribute':['a1','a2']})

    print(json.dumps(pathEntity1.to_dict()))
    print(json.dumps(pathEntity2.to_dict()))
    multiValuesPath = MultiValues({'items': [pathEntity1, pathEntity2]})
    print(multiValuesPath.to_statement())

    point_json = '''
        {
            "type": "Point",
            "coordinates": [
                1.1, 2.2
            ],
            "searchOptions": {"weight": 3.2}
        }
    '''
    deserialized_object_point = deserialize_objects(json.loads(point_json))
    assert deserialized_object_point.type == "Point"
    print(deserialized_object_point.to_statement())
    print(json.dumps(deserialized_object_point.to_dict()))

    circular_string_json = '''
        {
            "type": "CircularString", 
            "coordinates": [
                [33.3, 11.1], [11.1, 33.3], [44.4, 44.4]
            ]
        }
    '''
    deserialized_object_circular_string = deserialize_objects(json.loads(circular_string_json))
    assert deserialized_object_circular_string.type == "CircularString"
    print(deserialized_object_circular_string.to_statement())
    print(json.dumps(deserialized_object_circular_string.to_dict()))

    linestring_json = '''
        {
            "type": "LineString", 
            "coordinates": [
                [33.3, 11.1], [11.1, 33.3], [44.4, 44.4]
            ]
        }
    '''
    deserialized_object_linestring = deserialize_objects(json.loads(linestring_json))
    assert deserialized_object_linestring.type == "LineString"
    print(deserialized_object_linestring.to_statement())
    print(json.dumps(deserialized_object_linestring.to_dict()))

    polygon_json = '''
        {
            "type": "Polygon", 
            "coordinates": [
                [
                    [30.3, 10.1], 
                    [40.4, 40.4], 
                    [10.1, 30.3], 
                    [30.3, 10.1]
                ]
            ]
        }
    '''
    deserialized_object_polygon = deserialize_objects(json.loads(polygon_json))
    assert deserialized_object_polygon.type == Polygon.__name__
    print(deserialized_object_polygon.to_statement())
    print(json.dumps(deserialized_object_polygon.to_dict()))

    multipoint_json = '''
        {
            "type": "MultiPoint", 
            "coordinates": [
                [11.1, 44.4], [44.4, 33.3], [22.2, 22.2], [33.3, 11.1]
            ]
        }
    '''
    deserialized_object_multipoint = deserialize_objects(json.loads(multipoint_json))
    assert deserialized_object_multipoint.type == "MultiPoint"
    print(deserialized_object_multipoint.to_statement())
    print(json.dumps(deserialized_object_multipoint.to_dict()))

    multilinestring_json = '''
        {
            "type": "MultiLineString", 
            "coordinates": [
                [[11.1, 11.1], [22.2, 22.2], [11.1, 44.4]], 
                [[44.4, 44.4], [33.3, 33.3], [44.4, 22.2], [33.3, 11.1]]
            ]
        }
    '''
    deserialized_object_multilinestring = deserialize_objects(json.loads(multilinestring_json))
    assert deserialized_object_multilinestring.type == "MultiLineString"
    print(deserialized_object_multilinestring.to_statement())
    print(json.dumps(deserialized_object_multilinestring.to_dict()))

    multipolygon_json = '''
        {
            "type": "MultiPolygon", 
            "coordinates": [
                [
                    [[33.3, 22.2], [45.4, 44.4], [11.1, 44.4], [33.3, 22.2]]
                ], 
                [
                    [[15.4, 5.4], [44.4, 11.1], [11.1, 22.2], [5.4, 11.1], [15.4, 5.4]]
                ]
            ]
        }
    '''
    deserialized_object_multipolygon = deserialize_objects(json.loads(multipolygon_json))
    assert deserialized_object_multipolygon.type == "MultiPolygon"
    print(deserialized_object_multipolygon.to_statement())
    print(json.dumps(deserialized_object_multipolygon.to_dict()))

    multipolygon2_json = '''
        {
            "type": "MultiPolygon", 
            "coordinates": [
                [
                    [[44.4, 44.4], [22.2, 45.4], [45.4, 33.3], [44.4, 44.4]]
                ], 
                [
                    [[22.2, 35.4], [11.1, 33.3], [11.1, 11.1], [33.3, 5.4], [45.4, 22.2], [22.2, 35.4]], 
                    [[33.3, 22.2], [22.2, 15.4], [22.2, 25.4], [33.3, 22.2]]
                ]
            ]
        }
    '''
    deserialized_object_multipolygon2 = deserialize_objects(json.loads(multipolygon2_json))
    assert deserialized_object_multipolygon2.type == "MultiPolygon"
    print(deserialized_object_multipolygon2.to_statement())
    print(json.dumps(deserialized_object_multipolygon2.to_dict()))

    multigeometry_collection_json = '''
        {
            "type": "GeometryCollection",
            "geometries": [
                {
                    "type": "Point",
                    "coordinates": [44.4, 11.1]
                },
                {
                    "type": "LineString",
                    "coordinates": [
                        [11.1, 11.1], [22.2, 22.2], [11.1, 44.4]
                    ]
                },
                {
                    "type": "Polygon",
                    "coordinates":  [[[30.3, 10.1], [40.4, 40.4], [10.1, 30.3], [30.3, 10.1]]]
                }
            ]
        }
    '''
    deserialized_object_multigeometry_collection = deserialize_objects(json.loads(multigeometry_collection_json))
    assert deserialized_object_multigeometry_collection.type == "GeometryCollection"
    assert deserialized_object_multigeometry_collection.geometries[0].type == "Point"
    assert deserialized_object_multigeometry_collection.geometries[1].type == "LineString"
    assert deserialized_object_multigeometry_collection.geometries[2].type == "Polygon"
    print(deserialized_object_multigeometry_collection.to_statement())
    print(json.dumps(deserialized_object_multigeometry_collection.to_dict()))


    print(deserialized_object_point.to_statement())


    print(serialize_geometry_collection([1.1,2.2]))
    print(serialize_geometry_collection([[1.1,2.2],[3.3,4.4]]))
    print(serialize_geometry_collection([[[1.1,2.2],[3.3,4.4]],[[5.5,6.6],[7.7,8.8]]]))

    #print(deserialized_object_point.to_statement())
    #print(deserialized_object_linestring.to_statement())
    #print(deserialized_object_circular_string.to_statement())
    #print(deserialized_object_polygon.to_statement())
    #print(deserialized_object_multipoint.to_statement())
    #print(deserialized_object_multilinestring.to_statement())
    #print(deserialized_object_multipolygon.to_statement())
    #print(deserialized_object_multigeometry_collection.to_statement())
    for i in [  deserialized_object_point,
                deserialized_object_linestring,
                deserialized_object_circular_string,
                deserialized_object_polygon,
                deserialized_object_multipoint,
                deserialized_object_multilinestring,
                deserialized_object_multipolygon,
                deserialized_object_multigeometry_collection]:
        print(i.to_statement())
        print(json.dumps(i.to_dict()))
    print(deserialized_object_expression.to_statement())
    print(json.dumps(deserialized_object_property_with_array.to_dict()))
    print(deserialized_object_property_with_array.to_statement())
    print(' -----> everything fine <----- ')
