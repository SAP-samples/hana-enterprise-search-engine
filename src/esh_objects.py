"""Classes to define a query"""
from enum import Enum
import re
from typing import List, Literal, Annotated, Union
import json
from unittest import result
from pydantic import BaseModel, Field

import esh_client

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

# Expression = ForwardRef('Expression')       
ExpressionValueInternal = Union[Annotated[Union["UnaryExpressionInternal",  \
    "ExpressionInternal", "ComparisonInternal","WithinOperator", "CoveredByOperator", \
    "IntersectsOperator", "TermInternal", "PointInternal", "LineStringInternal", "CircularStringInternal", "PolygonInternal", \
    "MultiPointInternal", "MultiLineStringInternal", "MultiPolygonInternal", "GeometryCollectionInternal", "NumberValueInternal", \
    "BooleanValueInternal", "StringValueInternal", "PhraseInternal", "PropertyInternal",  "MultiValuesInternal"], \
    Field(discriminator="type")], str]

class SearchOptionsInternal(esh_client.SearchOptions):

    def to_statement(self) -> str:
        returnStatement = ""
        if self.fuzzinessThreshold:
            returnStatement = returnStatement + '~' + str(self.fuzzinessThreshold)
        if self.fuzzySearchOptions:
            if not self.fuzzinessThreshold:
                returnStatement = returnStatement + '~0.8'
            returnStatement = returnStatement + '[' + self.fuzzySearchOptions + ']'
        if self.weight:
            returnStatement = returnStatement + '^' + str(self.weight)
        return returnStatement


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

def addFuzzySearchOptions(item: str, searchOptions: SearchOptionsInternal) -> str:
    if searchOptions:
        return item + searchOptions.to_statement()
    return item


class OrderByInternal(esh_client.OrderBy):

    def to_statement(self):
        if self.order:
            return f'{self.key} {self.order}'
        else:
            return self.key
class PropertyInternal(esh_client.Property):
    type: Literal['PropertyInternal'] = 'PropertyInternal'

    def to_statement(self):
        property_value = self.property if not type(self.property) is list else ".".join(self.property)
        if self.prefixOperator:
            return self.prefixOperator + ' ' + property_value
        else:
            return property_value

class TermInternal(esh_client.Term):

    def to_statement(self):
        if self.doEshEscaping:
            final_term = f'"{escapePhrase(self.term)}"'if self.isQuoted else escapeQuery(self.term)
        else:
            final_term = f'"{self.term}"' if self.isQuoted else self.term
        return addFuzzySearchOptions(final_term, self.searchOptions)

class PhraseInternal(esh_client.Phrase):
    type: Literal['PhraseInternal'] = 'PhraseInternal'

    searchOptions: SearchOptionsInternal | None

    def to_statement(self):
        if self.doEshEscaping:
            final_phrase = escapePhrase(self.phrase)
        else:
            final_phrase = self.phrase
        return addFuzzySearchOptions('\"' + final_phrase + '\"', self.searchOptions)

class StringValueInternal(esh_client.StringValue):

    type: Literal['StringValueInternal'] = 'StringValueInternal'

    def to_statement(self):
        #if self.withoutEnclosing:
        #    return String(Number.parseFloat(this.value));
        return_value = None
        if self.isQuoted:
            return f'"{escapeDoubleQuoteAndBackslash(self.value)}"'
        if self.isSingleQuoted:
            return f"'{escapeSingleQuote(self.value)}'"
        if return_value is None:
            return_value = self.value
        return addFuzzySearchOptions(return_value, self.searchOptions)


class NumberValueInternal(esh_client.NumberValue):

    def to_statement(self):
        return f'{self.value}'

class BooleanValueInternal(esh_client.BooleanValue):

    def to_statement(self):
        return json.dumps(self.value)

class ComparisonInternal(BaseModel):
    type: Literal['ComparisonInternal'] = 'ComparisonInternal'
    property: str | ExpressionValueInternal
    operator: esh_client.ComparisonOperator
    value: str | ExpressionValueInternal | None

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

        
class ExpressionInternal(esh_client.Expression):
    type: Literal['ExpressionInternal'] = 'ExpressionInternal'
    items: List[ExpressionValueInternal] | None
    
    def get_expression_statement(self, expression_item):
        if isinstance(expression_item, ExpressionInternal): 
            return f'{expression_item.to_statement()}'
        else:
            try:
                return expression_item.to_statement()
            except: 
                return f'{expression_item}'

    def to_statement(self):
        if self.items is None:
            raise Exception("Expression: Missing mandatory parameter 'items'")
        operator = self.operator if self.operator is not None else esh_client.LogicalOperator.TIGHT_AND
        if operator != '':
            connect_operator = f' {operator} '
        else:
            connect_operator = ' '
        statements = list(map(lambda item: self.get_expression_statement(item), self.items))
        if len(self.items) > 1:
            return f"({connect_operator.join(statements)})"
            # return f"{connect_operator.join(statements)}"
        return connect_operator.join(statements)


class UnaryExpressionInternal(esh_client.UnaryExpression):
    type: Literal['UnaryExpressionInternal'] = 'UnaryExpressionInternal'
    item: ExpressionValueInternal

    def to_statement(self):
        if self.item is None:
            raise Exception("UnaryExpression: Missing mandatory parameter 'item'")
        if self.operator is None:
            raise Exception("UnaryExpression: Missing mandatory parameter 'operator'")
        item_statement = self.item.to_statement()
        if item_statement.startswith("(") and item_statement.endswith(")"):
            return f"{self.operator}:{item_statement}"
        return f"{self.operator}:({item_statement})"


class WithinOperator(BaseModel):
    type: Literal['WithinOperator'] = 'WithinOperator'
    id: int | None

    def to_statement(self) -> str:
        if self.id:
            return f':WITHIN({str(self.id)}):'
        else:
            return ':WITHIN:'


class CoveredByOperator(BaseModel):
    type: Literal['CoveredByOperator'] = 'CoveredByOperator'
    id: int | None

    def to_statement(self) -> str:
        if self.id:
            return f':COVERED_BY({str(self.id)}):'
        else:
            return ':COVERED_BY:'

class IntersectsOperator(BaseModel):
    type: Literal['IntersectsOperator'] = 'IntersectsOperator'
    id: int | None

    def to_statement(self) -> str:
        if self.id:
            return f':INTERSECTS({str(self.id)}):'
        else:
            return ':INTERSECTS:'

class GeometryBaseInternal(BaseModel):
    type: str
    coordinates: list
    searchOptions: SearchOptionsInternal | None

    def to_statement(self, geometry_type = None):
        if not self.type.endswith("Internal"):
            raise Exception(f"GeometryBaseInternal: Unexpected object '{self.type}'.")
        if geometry_type is None:
            geometry_type = self.__class__.__name__[:-(len("Internal"))].upper()
        try:
            self.coordinates[0][0]
            return addFuzzySearchOptions(f'{geometry_type}{serialize_geometry_collection(self.coordinates)}', self.searchOptions)
        except TypeError:
            #return f"{' '.join(list(map(lambda i: str(i), collection)))}"
            return addFuzzySearchOptions(f'{geometry_type}({serialize_geometry_collection(self.coordinates)})', self.searchOptions)

class PointInternal(GeometryBaseInternal):
    type: Literal['PointInternal'] = 'PointInternal'

class LineStringInternal(GeometryBaseInternal):
    type: Literal['LineStringInternal'] = 'LineStringInternal'

class CircularStringInternal(GeometryBaseInternal):
    type: Literal['CircularStringInternal'] = 'CircularStringInternal'

class PolygonInternal(GeometryBaseInternal):
    type: Literal['PolygonInternal'] = 'PolygonInternal'

class MultiPointInternal(GeometryBaseInternal):
    type: Literal['MultiPointInternal'] = 'MultiPointInternal'

class MultiLineStringInternal(GeometryBaseInternal):
    type: Literal['MultiLineStringInternal'] = 'MultiLineStringInternal'

class MultiPolygonInternal(GeometryBaseInternal):
    type: Literal['MultiPolygonInternal'] = 'MultiPolygonInternal'

class GeometryCollectionInternal(esh_client.GeometryCollection):
    type: Literal['GeometryCollectionInternal'] = 'GeometryCollectionInternal'
    geometries: list[GeometryBaseInternal]

    def to_statement(self):
        return f"GEOMETRYCOLLECTION({','.join(list(map(lambda i: i.to_statement(geometry_type = 'GEOMETRYBASE'), self.geometries)))})" 

class MultiValuesInternal(esh_client.MultiValues):
    type: Literal['MultiValuesInternal'] = 'MultiValuesInternal'    
    items: List[ExpressionValueInternal] = []

    def to_statement(self) -> str:
        separator = " " if self.separator is None else self.separator
        return_value = separator.join(list(map(lambda item: item if isinstance(item, str) else item.to_statement(), self.items)))
        if self.encloseStart is not None:
            return_value = f'{self.encloseStart}{return_value}'
        if self.encloseEnd is not None:
            return_value = f'{return_value}{self.encloseEnd}'
        return return_value


ComparisonInternal.update_forward_refs()
ExpressionInternal.update_forward_refs()
UnaryExpressionInternal.update_forward_refs()
class EshObjectInternal(esh_client.EshObject):
    type: Literal['EshObjectInternal'] = 'EshObjectInternal' 
    searchQueryFilter: ExpressionInternal | None
    orderby: List[OrderByInternal] | None

    class Config:
        extra = 'forbid'

    def to_statement(self):
        esh = '/$all' if self.resourcePath is None else self.resourcePath
        searchQueryFilter = self.searchQueryFilter.to_statement() if self.searchQueryFilter else ''
        if self.suggestTerm is not None:
            escaped_suggested_term = self.suggestTerm.replace("'","''")
            esh += f"/GetSuggestion(term='{escaped_suggested_term}')"
        if esh.startswith('/$all'):
            esh += '?'
            if self.top is None:
                top = 10
            else:
                top = self.top
            esh += f'${Constants.top}={top}'
            if self.skip is not None:
                esh += f'&${Constants.skip}={self.skip}'
            if self.count is not None:
                esh += f'&${Constants.count}={json.dumps(self.count)}'
            scope_filter = None
            if self.scope:
                if isinstance(self.scope, str):
                    scope_filter = self.scope
                elif len(self.scope) == 1:
                    scope_filter = self.scope[0]
                else:
                    scope_filter = f'({" OR ".join(self.scope)})'
            if searchQueryFilter != '':
                if scope_filter is not None:
                    searchQueryFilter = f'SCOPE:{scope_filter} {searchQueryFilter}'
                esh += f"&$apply=filter(Search.search(query='{searchQueryFilter}'))"
            elif scope_filter is not None:
                esh += f"&$apply=filter(Search.search(query='SCOPE:{scope_filter}'))"
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

def map_query(item):
    result = None

    if hasattr(item, 'type'):
        item_type = item.type

        match item_type:
            case 'StringValue':
                result = StringValueInternal(
                    value=item.value,
                    isQuoted=item.isQuoted,
                    isSingleQuoted=item.isSingleQuoted,
                    withoutEnclosing=item.withoutEnclosing
                )
                if item.searchOptions is not None:
                    result.searchOptions=SearchOptionsInternal(
                        fuzzinessThreshold=item.searchOptions.fuzzinessThreshold,
                        fuzzySearchOptions=item.searchOptions.fuzzySearchOptions,
                        weight=item.searchOptions.weight
                    )
            case 'Property':
                result = PropertyInternal(
                    property=item.property,
                    prefixOperator=item.prefixOperator
                )
            case 'Comparison':
                result = ComparisonInternal(
                    property=map_query(item.property),
                    operator=map_query(item.operator),
                    value=map_query(item.value)
                )
            case 'Expression':
                result = ExpressionInternal(
                    operator=item.operator,
                    items=list(map(lambda i: map_query(i),item.items))
                )
            case 'Phrase':
                result = PhraseInternal(
                    phrase=item.phrase,
                    searchOptions=item.searchOptions,
                    doEshEscaping=item.doEshEscaping
                )
            case 'SearchOptions':
                result = SearchOptionsInternal(
                    weight=item.weight,
                    fuzzinessThreshold=item.fuzzinessThreshold,
                    fuzzySearchOptions=item.fuzzySearchOptions
                )
            case 'Point':
                result = PointInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )
            case 'LineString':
                result = LineStringInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )        
            case 'CircularString':
                result = CircularStringInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )        
            case 'Polygon':
                result = PolygonInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )        
            case 'MultiPoint':
                result = MultiPointInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                ) 
            case 'MultiLineString':
                result = MultiLineStringInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )
            case 'MultiPolygon':
                result = MultiPolygonInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )        
            case 'GeometryCollection':
                result = GeometryCollectionInternal(
                    geometries=list(map(lambda i: map_query(i), item.geometries))
                )
            case 'MultiValues':
                result = MultiValuesInternal(
                    items = list(map(lambda i: map_query(i), item.items)),
                    separator = item.separator,
                    encloseStart = item.encloseStart,
                    encloseEnd = item.encloseEnd
                )
            case 'UnaryExpression':
                result = UnaryExpressionInternal(
                    operator=item.operator,
                    item=map_query(item.item)
                )
            case 'EshObject':
                result = EshObjectInternal(
                    searchQueryFilter=map_query(item.searchQueryFilter),
                    orderby=list(map(lambda i: map_query(i), item.orderby)) if item.orderby else None,
                    top=item.top,
                    skip=item.skip,
                    scope=item.scope,
                    count=item.count,
                    whyfound=item.whyfound,
                    select=item.select,
                    estimate=item.estimate,
                    wherefound=item.wherefound,
                    facetlimit=item.facetlimit,
                    facets=item.facets,
                    filteredgroupby=item.filteredgroupby,
                    suggestTerm=item.suggestTerm,
                    resourcePath=item.resourcePath
                )
            case _:
                raise Exception(f"map_query: Unexpected type '{item_type}'.")
    else:
        result = item
    return result


if __name__ == '__main__':

    mapped_object = map_query(esh_client.Property(property='aa'))
    print(mapped_object.to_statement())

    mapped_comparison = map_query(esh_client.Comparison(property="land",operator=esh_client.ComparisonOperator.EqualCaseInsensitive,value="negde"))
    m_items = [esh_client.StringValue(value='www'), esh_client.StringValue(value='222'), esh_client.StringValue(value='333')]

    comp = {'property': "language", \
        'operator': ':EQ:', 'value': { Constants.type: 'StringValue', 'value': 'Python'}}
    aas = map_query(esh_client.Comparison.parse_obj(comp))
    assert aas.to_statement() == 'language:EQ:Python'

    comp1 = {'property': {'type':"Property", "property": "language"}, \
        'operator': ':EQ:', 'value': { Constants.type: 'StringValue', 'value': 'Java'}}
    aas1 = map_query(esh_client.Comparison.parse_obj(comp1))
    assert aas1.to_statement() == 'language:EQ:Java'



    exp1 = map_query(esh_client.Expression(items=[esh_client.StringValue(value='MMMM'),\
        esh_client.StringValue(value='KKK')], operator='OR'))
    assert exp1.to_statement() == '(MMMM OR KKK)'
   
    aa = esh_client.EshObject.parse_obj({'searchQueryFilter': {Constants.type: 'Expression', 'items' : [{'type': 'StringValue', \
       'value': 'aaa'},{'type': 'StringValue', 'value': 'bbb'}], 'operator': 'AND'}})
    bbb = map_query(aa)
    assert bbb.to_statement() == "/$all?$top=10&$apply=filter(Search.search(query='(aaa AND bbb)'))"

    exp2 = ExpressionInternal()
    exp2.operator = 'AND'
    exp2.items = []
    exp2.items.append(StringValueInternal(value='mannheim'))
    exp2.items.append(StringValueInternal(value='heidelberg'))
    assert exp2.to_statement() == '(mannheim AND heidelberg)'


    json_body={
        'top': 10,
        'count': True,
        'whyfound': True,
        'select': ['id', 'name'],
        'estimate': True,
        'wherefound': True,
        'facetlimit': 4,
        'scope': ['S1'],
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
        'searchQueryFilter': {Constants.type: 'Expression',\
            'operator': 'OR',\
            'items' :[\
                {'type': 'StringValue', 'value': 'test'},\
                {'type': 'StringValue', 'value': 'function'}]
            }
        }


    es_objects = esh_client.EshObject.parse_obj(json_body)
    es_mapped_objects = map_query(es_objects)
    print(es_mapped_objects.to_statement())
    # print(json.dumps(es_objects.searchQueryFilter.to_dict(), indent=4))
    # print(json.dumps(es_objects.to_dict(), indent=4))
    expected_statement = '/$all?$top=10&$count=true&$apply=filter(' \
        'Search.search(query=\'SCOPE:S1 (test OR function)\'' \
        '))&whyfound=true&$select=id,name&$orderby=city ASC,language DESC,' \
        'land&estimate=true&wherefound=true&facetlimit=4&facets=city,land&filteredgroupby=false'
    print(es_mapped_objects.to_statement())
    assert es_mapped_objects.to_statement() == expected_statement

    sv = esh_client.StringValue(value='sss', isQuoted=True)
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
    # TODO add the test after removing Term class


    searchOpts = SearchOptionsInternal(fuzzinessThreshold=0.5,fuzzySearchOptions='search=typeahead',weight=0.9)
    assert searchOpts.to_statement() == '~0.5[search=typeahead]^0.9'
        
    term = TermInternal(term='mannh"eim', doEshEscaping=True,\
        searchOptions=SearchOptionsInternal(fuzzinessThreshold=0.5,fuzzySearchOptions='search=typeahead',weight=0.9))
    print(term.to_statement())
    assert term.to_statement() == 'mannh"eim~0.5[search=typeahead]^0.9'
    termHD = TermInternal(term='Heidelberg')
    print(json.dumps(termHD.dict()))


    phrase_definition = {'type': 'Phrase','phrase': 'heidelberg', \
        Constants.searchOptions: {\
            Constants.fuzzinessThreshold:0.5,\
            Constants.weight:0.9,\
            Constants.fuzzySearchOptions:'search=typeahead'}}
    phrase = esh_client.Phrase.parse_obj(phrase_definition)
    phrase_mapped = map_query(phrase)
    assert phrase_mapped.to_statement() == '"heidelberg"~0.5[search=typeahead]^0.9'



    suggest_json_body={
        'suggestTerm': 'bas'
    }
    suggest_es_object = esh_client.EshObject.parse_obj(suggest_json_body)
    suggest_es_object_mapped = map_query(suggest_es_object)
    print(suggest_es_object_mapped.to_statement())
    assert suggest_es_object_mapped.to_statement() == "/$all/GetSuggestion(term='bas')?$top=10"


    metadata_json_body={
        'resourcePath': '/$metadata'
    }
    metadata_es_object = esh_client.EshObject.parse_obj(metadata_json_body)
    metadata_es_object_mapped = map_query(metadata_es_object)
    assert metadata_es_object_mapped.to_statement() == '/$metadata'



    assert WithinOperator().to_statement() == ':WITHIN:'
    assert WithinOperator(id=4).to_statement() == ':WITHIN(4):'

    assert CoveredByOperator().to_statement() == ':COVERED_BY:'
    assert CoveredByOperator(id=5).to_statement() == ':COVERED_BY(5):'

    assert IntersectsOperator().to_statement() == ':INTERSECTS:'
    assert IntersectsOperator(id=6).to_statement() == ':INTERSECTS(6):'

    assert escapePhrase('aaa?bbb') == 'aaa\\?bbb'

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
    deserialized_object_expression = esh_client.Expression.parse_obj(json.loads(json_expression))
    # assert deserialized_object_expression.type == Expression.__name__
    # print(json.dumps(deserialized_object_expression.to_dict()))
    # print(deserialized_object_expression.to_statement())
    deserialized_object_expression_mapped = map_query(deserialized_object_expression)
    assert deserialized_object_expression_mapped.to_statement() == '(city country)'

    json_property = '''
        {
            "type": "Property",
            "property": "city"
        }
    '''
    deserialized_object_property_city = esh_client.Property.parse_obj(json.loads(json_property))
    assert deserialized_object_property_city.type == esh_client.Property.__name__

    object_property_internal_mapped = map_query(deserialized_object_property_city)
    print(object_property_internal_mapped.to_statement())
    print(json.dumps(object_property_internal_mapped.dict()))

    assert isinstance(object_property_internal_mapped, esh_client.Property)
    assert isinstance(object_property_internal_mapped, PropertyInternal)
    assert object_property_internal_mapped.to_statement() == 'city'

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






    deserialized_object_comparison = esh_client.Comparison.parse_obj(json.loads(json_comparison))
    assert deserialized_object_comparison.type == esh_client.Comparison.__name__
    deserialized_object_comparison_mapped = map_query(deserialized_object_comparison)
    assert deserialized_object_comparison_mapped.to_statement() == 'city:Mannheim'

    # print(json.dumps(deserialized_object_comparison.to_dict()))

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
    des_obj = esh_client.MultiValues.parse_obj(json.loads(json_multi_values))
    assert des_obj.type == "MultiValues"
    # print(json.dumps(des_obj.to_dict()))


    # pathDict1 = {'type': 'Path','namespace':'N1','entity':'E1','path_index': 1,'attribute':'a1'}
    # pathDict2 = {'type': 'Path','namespace':'N1','entity':'E1','path_index': 1,'attribute':'a2'}

    # pathEntity1 = Path.parse_obj(pathDict1)
    # pathEntity2 = Path.parse_obj(pathDict2)


    # multiValuesPath = MultiValues.parse_obj({'type': 'MultiValues','items': [pathDict1, pathDict2]})
    # print(multiValuesPath.to_statement())

    point_json = '''
        {
            "type": "Point",
            "coordinates": [
                1.1, 2.2
            ],
            "searchOptions": {"weight": 3.2}
        }
    '''
    deserialized_object_point = esh_client.Point.parse_obj(json.loads(point_json))
    assert deserialized_object_point.type == "Point"
    deserialized_object_point_mapped = map_query(deserialized_object_point)
    assert deserialized_object_point_mapped.to_statement() == "POINT(1.1 2.2)^3.2"

    circular_string_json = '''
        {
            "type": "CircularString", 
            "coordinates": [
                [33.3, 11.1], [11.1, 33.3], [44.4, 44.4]
            ]
        }
    '''
    deserialized_object_circular_string = esh_client.CircularString.parse_obj(json.loads(circular_string_json))
    assert deserialized_object_circular_string.type == "CircularString"
    deserialized_object_circular_string_mapped = map_query(deserialized_object_circular_string)
    assert deserialized_object_circular_string_mapped.to_statement()  == "CIRCULARSTRING(33.3 11.1,11.1 33.3,44.4 44.4)"

    linestring_json = '''
        {
            "type": "LineString", 
            "coordinates": [
                [33.3, 11.1], [11.1, 33.3], [44.4, 44.4]
            ]
        }
    '''
    deserialized_object_linestring = esh_client.LineString.parse_obj(json.loads(linestring_json))
    assert deserialized_object_linestring.type == "LineString"
    deserialized_object_linestring_mapped = map_query(deserialized_object_linestring)
    assert deserialized_object_linestring_mapped.to_statement() == "LINESTRING(33.3 11.1,11.1 33.3,44.4 44.4)"

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
    deserialized_object_polygon = esh_client.Polygon.parse_obj(json.loads(polygon_json))
    assert deserialized_object_polygon.type == esh_client.Polygon.__name__
    deserialized_object_polygon_mapped = map_query(deserialized_object_polygon)
    assert deserialized_object_polygon_mapped.to_statement() == "POLYGON((30.3 10.1,40.4 40.4,10.1 30.3,30.3 10.1))"

    multipoint_json = '''
        {
            "type": "MultiPoint", 
            "coordinates": [
                [11.1, 44.4], [44.4, 33.3], [22.2, 22.2], [33.3, 11.1]
            ]
        }
    '''
    deserialized_object_multipoint = esh_client.MultiPoint.parse_obj(json.loads(multipoint_json))
    assert deserialized_object_multipoint.type == "MultiPoint"
    deserialized_object_multipoint_mapped = map_query(deserialized_object_multipoint)
    assert deserialized_object_multipoint_mapped.to_statement() == "MULTIPOINT(11.1 44.4,44.4 33.3,22.2 22.2,33.3 11.1)"

    multilinestring_json = '''
        {
            "type": "MultiLineString", 
            "coordinates": [
                [[11.1, 11.1], [22.2, 22.2], [11.1, 44.4]], 
                [[44.4, 44.4], [33.3, 33.3], [44.4, 22.2], [33.3, 11.1]]
            ]
        }
    '''
    deserialized_object_multilinestring = esh_client.MultiLineString.parse_obj(json.loads(multilinestring_json))
    assert deserialized_object_multilinestring.type == "MultiLineString"
    deserialized_object_multilinestring_mapped = map_query(deserialized_object_multilinestring)
    assert deserialized_object_multilinestring_mapped.to_statement() == "MULTILINESTRING((11.1 11.1,22.2 22.2,11.1 44.4),(44.4 44.4,33.3 33.3,44.4 22.2,33.3 11.1))"

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
    deserialized_object_multipolygon = esh_client.MultiPolygon.parse_obj(json.loads(multipolygon_json))
    assert deserialized_object_multipolygon.type == "MultiPolygon"
    deserialized_object_multipolygon_mapped = map_query(deserialized_object_multipolygon)
    assert deserialized_object_multipolygon_mapped.to_statement() == "MULTIPOLYGON(((33.3 22.2,45.4 44.4,11.1 44.4,33.3 22.2)),((15.4 5.4,44.4 11.1,11.1 22.2,5.4 11.1,15.4 5.4)))"

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
    deserialized_object_multipolygon2 = esh_client.MultiPolygon.parse_obj(json.loads(multipolygon2_json))
    assert deserialized_object_multipolygon2.type == "MultiPolygon"
    deserialized_object_multipolygon2_mapped = map_query(deserialized_object_multipolygon2)
    assert deserialized_object_multipolygon2_mapped.to_statement() == "MULTIPOLYGON(((44.4 44.4,22.2 45.4,45.4 33.3,44.4 44.4)),((22.2 35.4,11.1 33.3,11.1 11.1,33.3 5.4,45.4 22.2,22.2 35.4),(33.3 22.2,22.2 15.4,22.2 25.4,33.3 22.2)))"

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
    deserialized_object_multigeometry_collection = esh_client.GeometryCollection.parse_obj(json.loads(multigeometry_collection_json))
    assert deserialized_object_multigeometry_collection.type == "GeometryCollection"
    assert deserialized_object_multigeometry_collection.geometries[0].type == "Point"
    assert deserialized_object_multigeometry_collection.geometries[1].type == "LineString"
    assert deserialized_object_multigeometry_collection.geometries[2].type == "Polygon"

    deserialized_object_multigeometry_collection_mapped = map_query(deserialized_object_multigeometry_collection)
    assert deserialized_object_multigeometry_collection_mapped.type == "GeometryCollectionInternal"
    assert deserialized_object_multigeometry_collection_mapped.geometries[0].type == "PointInternal"
    assert deserialized_object_multigeometry_collection_mapped.geometries[1].type == "LineStringInternal"
    assert deserialized_object_multigeometry_collection_mapped.geometries[2].type == "PolygonInternal"
    print(deserialized_object_multigeometry_collection_mapped.to_statement())
    assert deserialized_object_multigeometry_collection_mapped.to_statement() == "GEOMETRYCOLLECTION(GEOMETRYBASE(44.4 11.1),GEOMETRYBASE(11.1 11.1,22.2 22.2,11.1 44.4),GEOMETRYBASE((30.3 10.1,40.4 40.4,10.1 30.3,30.3 10.1)))"

    assert serialize_geometry_collection([1.1,2.2]) == "1.1 2.2"
    assert serialize_geometry_collection([[1.1,2.2],[3.3,4.4]]) == "(1.1 2.2,3.3 4.4)"
    assert serialize_geometry_collection([[[1.1,2.2],[3.3,4.4]],[[5.5,6.6],[7.7,8.8]]]) == "((1.1 2.2,3.3 4.4),(5.5 6.6,7.7 8.8))"

    for i in [  deserialized_object_point_mapped,
                deserialized_object_linestring_mapped,
                deserialized_object_circular_string_mapped,
                deserialized_object_polygon_mapped,
                deserialized_object_multipoint_mapped,
                deserialized_object_multilinestring_mapped,
                deserialized_object_multipolygon_mapped,
                deserialized_object_multigeometry_collection_mapped]:
        print(i.to_statement())
    print(deserialized_object_expression_mapped.to_statement())

    property_simple = esh_client.Property(property="someText")
    property_simple_mapped = map_query(property_simple)
    assert property_simple_mapped.to_statement() == 'someText'

    property_array = esh_client.Property(property=["one", "two"])
    property_array_mapped = map_query(property_array)
    assert property_array_mapped.to_statement() == 'one.two'
    

    so = esh_client.EshObject(
        searchQueryFilter=esh_client.Expression(
            operator='AND',
            items= [
                esh_client.Comparison(
                    property= esh_client.Property(property='lastName'),
                    operator= esh_client.ComparisonOperator.Search,
                    value= esh_client.StringValue(value='Doe')),
                esh_client.Comparison(
                    property= esh_client.Property(property='firstName'),
                    operator= esh_client.ComparisonOperator.Search,
                    value= esh_client.StringValue(value='Jane'))
                ]
            )
    )
    so_mapped = map_query(so)
    print(so_mapped.to_statement())
    # print(json.dumps(so.dict(exclude_none=True), indent = 4))

    assert so_mapped.to_statement() == "/$all?$top=10&$apply=filter(Search.search(query='(lastName:Doe AND firstName:Jane)'))"


    mv = esh_client.MultiValues(items=["one", "two"], separator=",", encloseStart="[", encloseEnd="]")
    mv_mapped = map_query(mv)
    assert mv_mapped.to_statement() == "[one,two]"

    unary_expression = esh_client.UnaryExpression(
        operator=esh_client.UnaryOperator.ROW, 
        item=esh_client.Expression(
            operator=esh_client.LogicalOperator.AND,
            items=[
                esh_client.Comparison(
                    property="city",
                    operator=esh_client.ComparisonOperator.EqualCaseInsensitive,
                    value=esh_client.StringValue(value="Mannheim")),
                esh_client.Comparison(
                    property="company",
                    operator=esh_client.ComparisonOperator.EqualCaseInsensitive,
                    value=esh_client.StringValue(value="SAP")),  
            ]
            )
        )
    unary_expression_mapped = map_query(unary_expression)  
    assert unary_expression_mapped.to_statement() == "ROW:(city:EQ:Mannheim AND company:EQ:SAP)"
    
    so = esh_client.EshObject(
            count=True,
            top=10,
            scope='Person',
            searchQueryFilter=esh_client.Expression(
                        operator=esh_client.LogicalOperator.OR,
                        items=[
                            esh_client.Expression(
                                operator=esh_client.LogicalOperator.AND,
                                        items= [
                                            esh_client.Comparison(
                                                property= esh_client.Property(property='lastName'),
                                                operator= esh_client.ComparisonOperator.Search,
                                                value= esh_client.StringValue(value='Doe')),
                                            esh_client.Comparison(
                                                property= esh_client.Property(property='firstName'),
                                                operator= esh_client.ComparisonOperator.Search,
                                                value= esh_client.StringValue(value='John'))
                                                ]
                            ),
                            esh_client.Expression(
                                operator=esh_client.LogicalOperator.AND,
                                items= [
                                        esh_client.Comparison(
                                            property= esh_client.Property(property='lastName'),
                                            operator= esh_client.ComparisonOperator.Search,
                                            value= esh_client.StringValue(value='Doe')),
                                        esh_client.Comparison(
                                            property= esh_client.Property(property='firstName'),
                                            operator= esh_client.ComparisonOperator.Search,
                                            value= esh_client.StringValue(value='Jane'))
                                    ]
                            )
                        ]
                    )
        )
    so_mapped = map_query(so)
    #print(f'ESH query statement: {so_mapped.to_statement()}')
    #print('-----cccc-----')
    #print(json.dumps(so_mapped.dict(exclude_none=True), indent=2))
    assert so_mapped.to_statement() == "/$all?$top=10&$count=true&$apply=filter(Search.search(query='SCOPE:Person ((lastName:Doe AND firstName:John) OR (lastName:Doe AND firstName:Jane))'))"

    print(' -----> everything fine <----- ')