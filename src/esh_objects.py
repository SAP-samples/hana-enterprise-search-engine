"""Classes to define a query"""
from enum import Enum
import re
from typing import List, Literal, Annotated, Union
import json
from unittest import result
from pydantic import BaseModel, Field
import xml.etree.ElementTree as ET 
from xml.etree.ElementTree import tostring

import esh_client

reservedCharacters = ['\\', '-', '(', ')', '~', '^', '\'', ':', "'", '[', ']'] # Placeholders * and ?
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
    escapePlaceholders = 'escapePlaceholders'
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

class FuzzySearchOptionsInternal(esh_client.FuzzySearchOptions):

    def to_statement(self):
        result_array = []
        if hasattr(self, 'abbreviationSimilarity') and self.abbreviationSimilarity is not None:
            result_array.append(f"abbreviationSimilarity={self.abbreviationSimilarity}")
        if hasattr(self, 'andSymmetric') and self.andSymmetric is not None:
            result_array.append(f"andSymmetric={self.andSymmetric}")  
        if hasattr(self, 'andThreshold') and self.andThreshold is not None:
            result_array.append(f"andThreshold={self.andThreshold}")  
        if hasattr(self, 'bestMatchingTokenWeight') and self.bestMatchingTokenWeight is not None:
            result_array.append(f"bestMatchingTokenWeight={self.bestMatchingTokenWeight}")  
        if hasattr(self, 'composeWords') and self.composeWords is not None:
            result_array.append(f"composeWords={self.composeWords}")  
        if hasattr(self, 'compoundWordWeight') and self.compoundWordWeight is not None:
            result_array.append(f"compoundWordWeight={self.compoundWordWeight}")  
        if hasattr(self, 'considerNonMatchingTokens') and self.considerNonMatchingTokens is not None:
            result_array.append(f"considerNonMatchingTokens={self.considerNonMatchingTokens}")  
        if hasattr(self, 'decomposeWords') and self.decomposeWords is not None:
            result_array.append(f"decomposeWords={self.decomposeWords}")  
        if hasattr(self, 'emptyScore') and self.emptyScore is not None:
            result_array.append(f"emptyScore={self.emptyScore}")  
        if hasattr(self, 'errorDevaluate') and self.errorDevaluate is not None:
            result_array.append(f"errorDevaluate={self.errorDevaluate}")  
        if hasattr(self, 'excessTokenWeight') and self.excessTokenWeight is not None:
            result_array.append(f"excessTokenWeight={self.excessTokenWeight}")  
        if hasattr(self, 'fuzzySubstringMatch') and self.fuzzySubstringMatch is not None:
            result_array.append(f"fuzzySubstringMatch={self.fuzzySubstringMatch}")  
        if hasattr(self, 'interScriptMatching') and self.interScriptMatching is not None:
            result_array.append(f"interScriptMatching={self.interScriptMatching}")  
        if hasattr(self, 'lengthTolerance') and self.lengthTolerance is not None:
            result_array.append(f"lengthTolerance={self.lengthTolerance}")  
        if hasattr(self, 'maxDateDistance') and self.maxDateDistance is not None:
            result_array.append(f"maxDateDistance={self.maxDateDistance}")  
        if hasattr(self, 'minSearchLength') and self.minSearchLength is not None:
            result_array.append(f"minSearchLength={self.minSearchLength}")  
        if hasattr(self, 'minTextScore') and self.minTextScore is not None:
            result_array.append(f"minTextScore={self.minTextScore}")  
        if hasattr(self, 'phraseCheckFactor') and self.phraseCheckFactor is not None:
            result_array.append(f"phraseCheckFactor={self.phraseCheckFactor}")  
        if hasattr(self, 'returnAll') and self.returnAll is not None:
            result_array.append(f"returnAll={self.returnAll}")  
        if hasattr(self, 'scoreFunction') and self.scoreFunction is not None:
            result_array.append(f"scoreFunction={self.scoreFunction}")  
        if hasattr(self, 'scoreFunctionDecay') and self.scoreFunctionDecay is not None:
            result_array.append(f"scoreFunctionDecay={self.scoreFunctionDecay}")  
        if hasattr(self, 'scoreFunctionOffset') and self.scoreFunctionOffset is not None:
            result_array.append(f"scoreFunctionOffset={self.scoreFunctionOffset}")  
        if hasattr(self, 'scoreFunctionScale') and self.scoreFunctionScale is not None:
            result_array.append(f"scoreFunctionScale={self.scoreFunctionScale}")  
        if hasattr(self, 'searchMode') and self.searchMode is not None:
            result_array.append(f"searchMode={self.searchMode}")  
        if hasattr(self, 'similarCalculationMode') and self.similarCalculationMode is not None:
            result_array.append(f"similarCalculationMode={self.similarCalculationMode}")  
        if hasattr(self, 'spellCheckFactor') and self.spellCheckFactor is not None:
            result_array.append(f"spellCheckFactor={self.spellCheckFactor}")  
        if hasattr(self, 'stopwordListId') and self.stopwordListId is not None:
            result_array.append(f"stopwordListId={self.stopwordListId}")  
        if hasattr(self, 'stopwordTable') and self.stopwordTable is not None:
            result_array.append(f"stopwordTable={self.stopwordTable}")  
        if hasattr(self, 'termMappingListId') and self.termMappingListId is not None:
            result_array.append(f"termMappingListId={self.termMappingListId}")  
        if hasattr(self, 'textSearch') and self.textSearch is not None:
            result_array.append(f"textSearch={self.textSearch}")
        if len(result_array) > 0:
            return f'{",".join(result_array)}'
        return None

def serialize_geometry_collection(collection):
    try:
        collection[0]
        return f"({','.join(list(map(lambda i: serialize_geometry_collection(i), collection)))})"
    except TypeError:
        return f"{' '.join(list(map(lambda i: str(i), collection)))}"

# Expression = ForwardRef('Expression')       
ExpressionValueInternal = Union[Annotated[Union["UnaryExpressionInternal",  \
    "ExpressionInternal", "ComparisonInternal","WithinOperator", "CoveredByOperator", \
    "IntersectsOperator",  "PointInternal", "LineStringInternal", "CircularStringInternal", "PolygonInternal", \
    "MultiPointInternal", "MultiLineStringInternal", "MultiPolygonInternal", "GeometryCollectionInternal", "NumberValueInternal", \
    "BooleanValueInternal", "StringValueInternal", "AuthInternal", "FilterInternal", "FilterWFInternal", \
    "PropertyInternal",  "MultiValuesInternal", "BoostInternal"], \
    Field(discriminator="type")], str]

class SearchOptionsInternal(esh_client.SearchOptions):
    fuzzySearchOptions: FuzzySearchOptionsInternal | None

    def to_statement(self) -> str:
        returnStatement = ""
        if self.fuzzinessThreshold:
            returnStatement = returnStatement + '~' + str(self.fuzzinessThreshold)
        if self.fuzzySearchOptions:
            if not self.fuzzinessThreshold:
                returnStatement = returnStatement + '~0.8'
            returnStatement = returnStatement + '[' + self.fuzzySearchOptions.to_statement() + ']'
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

def doEscapePlaceholders(value: str) -> str:
    return value.replace('?', '\?').replace('*', '\*')

def escapePhrase(value: str) -> str:
    return value.replace('\\','\\\\').replace('"','\\"').replace('*','\\*').replace('?','\\?').replace("'","''")

def addFuzzySearchOptions(item: str, searchOptions: SearchOptionsInternal) -> str:
    if searchOptions:
        return item + searchOptions.to_statement()
    return item

class PropertyInternal(esh_client.Property):
    type: Literal['PropertyInternal'] = 'PropertyInternal'
    property: str

    def to_statement(self):
        return self.property

class OrderByInternal(esh_client.OrderBy):
    type: Literal['OrderByInternal'] = 'OrderByInternal'
    key: PropertyInternal
    def to_statement(self):
        if self.order:
            return f'{self.key.to_statement()} {self.order}'
        else:
            return self.key.to_statement()


'''
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
'''
class StringValueInternal(esh_client.StringValue):

    type: Literal['StringValueInternal'] = 'StringValueInternal'

    # isPhrase: bool | None
    # escapePlaceholders: bool | None: bool | None

    def to_statement(self):
        #if self.withoutEnclosing:
        #    return String(Number.parseFloat(this.value));
        # return_value = None
        escaped_value = escapeQuery(self.value)
        if self.escapePlaceholders:
            escaped_value = doEscapePlaceholders(escaped_value)
        if self.isPhrase:
            escaped_value = f'"{escapeDoubleQuoteAndBackslash(escaped_value)}"'
            # return_value = '\"' + return_value + '\"'
        return addFuzzySearchOptions(escaped_value, self.searchOptions)


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

class ComparisonPropertiesListInternal(MultiValuesInternal):

    def __init__(self, items):
        super(MultiValuesInternal, self).__init__(items=items, separator=", ",encloseStart="(",encloseEnd=")")

class EshLanguageOperators(BaseModel):
    value: ExpressionInternal | ComparisonInternal

    def to_statement(self) -> str:
        auth_statement = self.value.to_statement()
        if auth_statement.startswith("("):
            return f"{self.operator}{auth_statement}"
        else:
            return f"{self.operator}({auth_statement})"
class AuthInternal(EshLanguageOperators):
    type: Literal['AuthInternal'] = 'AuthInternal'  
    operator: str = "AUTH:"

    # TODO add validation to check ComparisonOperators
    # allowed only EQ(S), LT(S), BT(S) and IS:NULL

class FilterInternal(EshLanguageOperators):
    type: Literal['FilterInternal'] = 'FilterInternal'  
    operator: str = "FILTER:"

class FilterWFInternal(EshLanguageOperators):
    type: Literal['FilterWFInternal'] = 'FilterWFInternal'  
    operator: str = "FILTERWF:"

class BoostInternal(EshLanguageOperators):
    type: Literal['BoostInternal'] = 'BoostInternal'  
    operator: str = "BOOST:"
    

ComparisonInternal.update_forward_refs()
ExpressionInternal.update_forward_refs()
UnaryExpressionInternal.update_forward_refs()
MultiValuesInternal.update_forward_refs()
class EshObjectInternal(esh_client.EshObject):
    type: Literal['EshObjectInternal'] = 'EshObjectInternal' 
    searchQueryFilter: ExpressionInternal | None
    orderby: List[OrderByInternal] | None
    auth: AuthInternal | None
    filter: FilterInternal | FilterWFInternal | None
    boost: BoostInternal | list[BoostInternal] | None
    facets: PropertyInternal | list[PropertyInternal] | None
    select: PropertyInternal | list[PropertyInternal] | None

    class Config:
        extra = 'forbid'

    def to_statement(self) -> str:
        esh = '/$all' if self.resourcePath is None else self.resourcePath
        if self.auth:
            if self.searchQueryFilter:
                self.searchQueryFilter.items.append(self.auth)
            else:
                self.searchQueryFilter = ExpressionInternal(
                    items=[
                        self.auth
                    ]
                )
        if self.filter:
            if self.searchQueryFilter:
                self.searchQueryFilter.items.append(self.filter)
            else:
                self.searchQueryFilter = ExpressionInternal(
                    items=[
                        self.filter
                    ]
                )
        if self.boost:
            if self.searchQueryFilter:
                if isinstance(self.boost, list):
                    for o in self.boost:
                        self.searchQueryFilter.items.append(o)
                else:
                    self.searchQueryFilter.items.append(self.boost)
            else:
                if isinstance(self.boost, list):
                    boosts = self.boost
                else:
                    boosts = [self.boost]
                self.searchQueryFilter = ExpressionInternal(
                    items=boosts
                )
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
                if len(self.scope) == 1:
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
                if isinstance(self.select, list):
                    select_value = ','.join(list(map(lambda i: i.to_statement(),self.select)))
                else:
                    select_value = self.select.to_statement()
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
                if isinstance(self.facets, list):
                    facets_value = ','.join(list(map(lambda i: i.to_statement(),self.facets)))
                else:
                    facets_value = self.facets.to_statement()
                esh += f'&{Constants.facets}={facets_value}'
            if self.filteredgroupby is not None:
                esh += f'&{Constants.filteredgroupby}={json.dumps(self.filteredgroupby)}'
        return esh

def map_search_options(result, item):
    if item.searchOptions is not None:
        result.searchOptions=SearchOptionsInternal(
            fuzzinessThreshold=item.searchOptions.fuzzinessThreshold,
            weight=item.searchOptions.weight
        )
        if item.searchOptions.fuzzySearchOptions is not None:
            result.searchOptions.fuzzySearchOptions = FuzzySearchOptionsInternal()
            if hasattr(item.searchOptions.fuzzySearchOptions, 'abbreviationSimilarity') and item.searchOptions.fuzzySearchOptions.abbreviationSimilarity is not None:
                result.searchOptions.fuzzySearchOptions.abbreviationSimilarity = item.searchOptions.fuzzySearchOptions.abbreviationSimilarity
            if hasattr(item.searchOptions.fuzzySearchOptions, 'andSymmetric') and item.searchOptions.fuzzySearchOptions.andSymmetric is not None:
                result.searchOptions.fuzzySearchOptions.andSymmetric = item.searchOptions.fuzzySearchOptions.andSymmetric  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'andThreshold') and item.searchOptions.fuzzySearchOptions.andThreshold is not None:
                result.searchOptions.fuzzySearchOptions.andThreshold = item.searchOptions.fuzzySearchOptions.andThreshold
            if hasattr(item.searchOptions.fuzzySearchOptions, 'bestMatchingTokenWeight') and item.searchOptions.fuzzySearchOptions.bestMatchingTokenWeight is not None:
                result.searchOptions.fuzzySearchOptions.bestMatchingTokenWeight = item.searchOptions.fuzzySearchOptions.bestMatchingTokenWeight 
            if hasattr(item.searchOptions.fuzzySearchOptions, 'composeWords') and item.searchOptions.fuzzySearchOptions.composeWords is not None:
                result.searchOptions.fuzzySearchOptions.composeWords = item.searchOptions.fuzzySearchOptions.composeWords  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'compoundWordWeight') and item.searchOptions.fuzzySearchOptions.compoundWordWeight is not None:
                result.searchOptions.fuzzySearchOptions.compoundWordWeight = item.searchOptions.fuzzySearchOptions.compoundWordWeight  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'considerNonMatchingTokens') and item.searchOptions.fuzzySearchOptions.considerNonMatchingTokens is not None:
                result.searchOptions.fuzzySearchOptions.considerNonMatchingTokens = item.searchOptions.fuzzySearchOptions.considerNonMatchingTokens  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'decomposeWords') and item.searchOptions.fuzzySearchOptions.decomposeWords is not None:
                result.searchOptions.fuzzySearchOptions.decomposeWords = item.searchOptions.fuzzySearchOptions.decomposeWords  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'emptyScore') and item.searchOptions.fuzzySearchOptions.emptyScore is not None:
                result.searchOptions.fuzzySearchOptions.emptyScore = item.searchOptions.fuzzySearchOptions.emptyScore 
            if hasattr(item.searchOptions.fuzzySearchOptions, 'errorDevaluate') and item.searchOptions.fuzzySearchOptions.errorDevaluate is not None:
                result.searchOptions.fuzzySearchOptions.errorDevaluate = item.searchOptions.fuzzySearchOptions.errorDevaluate
            if hasattr(item.searchOptions.fuzzySearchOptions, 'excessTokenWeight') and item.searchOptions.fuzzySearchOptions.excessTokenWeight is not None:
                result.searchOptions.fuzzySearchOptions.excessTokenWeight = item.searchOptions.fuzzySearchOptions.excessTokenWeight
            if hasattr(item.searchOptions.fuzzySearchOptions, 'fuzzySubstringMatch') and item.searchOptions.fuzzySearchOptions.fuzzySubstringMatch is not None:
                result.searchOptions.fuzzySearchOptions.fuzzySubstringMatch = item.searchOptions.fuzzySearchOptions.fuzzySubstringMatch
            if hasattr(item.searchOptions.fuzzySearchOptions, 'interScriptMatching') and item.searchOptions.fuzzySearchOptions.interScriptMatching is not None:
                result.searchOptions.fuzzySearchOptions.interScriptMatching = item.searchOptions.fuzzySearchOptions.interScriptMatching
            if hasattr(item.searchOptions.fuzzySearchOptions, 'lengthTolerance') and item.searchOptions.fuzzySearchOptions.lengthTolerance is not None:
                result.searchOptions.fuzzySearchOptions.lengthTolerance = item.searchOptions.fuzzySearchOptions.lengthTolerance
            if hasattr(item.searchOptions.fuzzySearchOptions, 'maxDateDistance') and item.searchOptions.fuzzySearchOptions.maxDateDistance is not None:
                result.searchOptions.fuzzySearchOptions.maxDateDistance = item.searchOptions.fuzzySearchOptions.maxDateDistance  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'minSearchLength') and item.searchOptions.fuzzySearchOptions.minSearchLength is not None:
                result.searchOptions.fuzzySearchOptions.minSearchLength = item.searchOptions.fuzzySearchOptions.minSearchLength  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'minTextScore') and item.searchOptions.fuzzySearchOptions.minTextScore is not None:
                result.searchOptions.fuzzySearchOptions.minTextScore = item.searchOptions.fuzzySearchOptions.minTextScore 
            if hasattr(item.searchOptions.fuzzySearchOptions, 'phraseCheckFactor') and item.searchOptions.fuzzySearchOptions.phraseCheckFactor is not None:
                result.searchOptions.fuzzySearchOptions.phraseCheckFactor = item.searchOptions.fuzzySearchOptions.phraseCheckFactor  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'returnAll') and item.searchOptions.fuzzySearchOptions.returnAll is not None:
                result.searchOptions.fuzzySearchOptions.returnAll = item.searchOptions.fuzzySearchOptions.returnAll
            if hasattr(item.searchOptions.fuzzySearchOptions, 'scoreFunction') and item.searchOptions.fuzzySearchOptions.scoreFunction is not None:
                result.searchOptions.fuzzySearchOptions.scoreFunction = item.searchOptions.fuzzySearchOptions.scoreFunction
            if hasattr(item.searchOptions.fuzzySearchOptions, 'scoreFunctionDecay') and item.searchOptions.fuzzySearchOptions.scoreFunctionDecay is not None:
                result.searchOptions.fuzzySearchOptions.scoreFunctionDecay = item.searchOptions.fuzzySearchOptions.scoreFunctionDecay
            if hasattr(item.searchOptions.fuzzySearchOptions, 'scoreFunctionOffset') and item.searchOptions.fuzzySearchOptions.scoreFunctionOffset is not None:
                result.searchOptions.fuzzySearchOptions.scoreFunctionOffset = item.searchOptions.fuzzySearchOptions.scoreFunctionOffset 
            if hasattr(item.searchOptions.fuzzySearchOptions, 'scoreFunctionScale') and item.searchOptions.fuzzySearchOptions.scoreFunctionScale is not None:
                result.searchOptions.fuzzySearchOptions.scoreFunctionScale = item.searchOptions.fuzzySearchOptions.scoreFunctionScale
            if hasattr(item.searchOptions.fuzzySearchOptions, 'searchMode') and item.searchOptions.fuzzySearchOptions.searchMode is not None:
                result.searchOptions.fuzzySearchOptions.searchMode = item.searchOptions.fuzzySearchOptions.searchMode  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'similarCalculationMode') and item.searchOptions.fuzzySearchOptions.similarCalculationMode is not None:
                result.searchOptions.fuzzySearchOptions.similarCalculationMode = item.searchOptions.fuzzySearchOptions.similarCalculationMode  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'spellCheckFactor') and item.searchOptions.fuzzySearchOptions.spellCheckFactor is not None:
                result.searchOptions.fuzzySearchOptions.spellCheckFactor = item.searchOptions.fuzzySearchOptions.spellCheckFactor  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'stopwordListId') and item.searchOptions.fuzzySearchOptions.stopwordListId is not None:
                result.searchOptions.fuzzySearchOptions.stopwordListId = item.searchOptions.fuzzySearchOptions.stopwordListId  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'stopwordTable') and item.searchOptions.fuzzySearchOptions.stopwordTable is not None:
                result.searchOptions.fuzzySearchOptions.stopwordTable = item.searchOptions.fuzzySearchOptions.stopwordTable  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'termMappingListId') and item.searchOptions.fuzzySearchOptions.termMappingListId is not None:
                result.searchOptions.fuzzySearchOptions.termMappingListId = item.searchOptions.fuzzySearchOptions.termMappingListId  
            if hasattr(item.searchOptions.fuzzySearchOptions, 'textSearch') and item.searchOptions.fuzzySearchOptions.textSearch is not None:
                result.searchOptions.fuzzySearchOptions.textSearch = item.searchOptions.fuzzySearchOptions.textSearch


def map_query(item):

    def remove2(x):
        return x[1:-1].replace('\\\\','\\')

    result = None

    if hasattr(item, 'type'):
        item_type = item.type

        match item_type:
            case 'StringValue':
                result = StringValueInternal(
                    value=item.value,
                    isPhrase=item.isPhrase,
                    escapePlaceholders=item.escapePlaceholders
                )
                map_search_options(result, item)
                # if item.searchOptions is not None:
                #    result.searchOptions=SearchOptionsInternal(
                #        fuzzinessThreshold=item.searchOptions.fuzzinessThreshold,
                #        fuzzySearchOptions=item.searchOptions.fuzzySearchOptions,
                #        weight=item.searchOptions.weight
                #    )
            case 'Property':
                result = PropertyInternal(
                    property = item.property if isinstance(item.property, str) else ".".join(item.property)
                )
            case 'OrderBy':
                result = OrderByInternal(
                    key = map_query(item.key),
                    order = item.order
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
                map_search_options(result, item)
            case 'LineString':
                result = LineStringInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )
                map_search_options(result, item)        
            case 'CircularString':
                result = CircularStringInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )
                map_search_options(result, item)     
            case 'Polygon':
                result = PolygonInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )
                map_search_options(result, item)        
            case 'MultiPoint':
                result = MultiPointInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )
                map_search_options(result, item)
            case 'MultiLineString':
                result = MultiLineStringInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )
                map_search_options(result, item)
            case 'MultiPolygon':
                result = MultiPolygonInternal(
                    coordinates=item.coordinates,
                    searchOptions=item.searchOptions
                )
                map_search_options(result, item)       
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
            # case 'Auth':
            #     result = AuthInternal(
            #         value=map_query(item.value)
            #    )
            case 'Filter':
                result = FilterInternal(
                    value=map_query(item.value)
                )
            case 'FilterWF':
                result = FilterWFInternal(
                    value=map_query(item.value)
                )
            case 'Boost':
                result = BoostInternal(
                    value=map_query(item.value)
                )
            case 'EshObject':
                result = EshObjectInternal(
                    searchQueryFilter=map_query(item.searchQueryFilter),
                    orderby=list(map(lambda i: map_query(i), item.orderby)) if isinstance(item.orderby, list) else map_query(item.orderby),
                    top=item.top,
                    skip=item.skip,
                    filter=map_query(item.filter),
                    scope=item.scope,
                    count=item.count,
                    whyfound=item.whyfound,
                    select=list(map(lambda i: map_query(i), item.select)) if isinstance(item.select, list) else map_query(item.select),
                    estimate=item.estimate,
                    wherefound=item.wherefound,
                    facetlimit=item.facetlimit,
                    facets=list(map(lambda i: map_query(i), item.facets)) if isinstance(item.facets, list) else map_query(item.facets),
                    filteredgroupby=item.filteredgroupby,
                    suggestTerm=item.suggestTerm,
                    resourcePath=item.resourcePath
                )
                if item.boost:
                    if isinstance(item.boost, list):  
                        result.boost = list(map(lambda i: map_query(i), item.boost)) 
                    else:
                        result.boost = map_query(item.boost)
            case _:
                raise Exception(f"map_query: Unexpected type '{item_type}'.")
    else:
        result = item
    return result


def generate_search_rule_set_query(search_result_set: esh_client.SearchRuleSet):
    if search_result_set.query:
            if search_result_set.query is not None:
                offset_value = None
                if search_result_set.query.limit is not None:
                    limit_value = str(search_result_set.query.limit)
                else:
                    limit_value = "10" # default value is 10
                if search_result_set.query.offset is not None:
                    offset_value = str(search_result_set.query.offset)
                if offset_value is not None:
                    query = ET.Element("query", limit=limit_value, offset=offset_value)
                else:
                    query = ET.Element("query", limit=limit_value)
            else:
                query = ET.Element("query", limit="10")

            if search_result_set.query.ruleset is not None:
                for rule_set_request in search_result_set.query.ruleset:
                    ruleset = ET.Element("ruleset", scoreSelection='firstRule')
                    if rule_set_request.attributeView is not None:
                        # attributeview = ET.Element("attributeview", scoreSelection='firstRule')
                        attributeView = ET.SubElement(ruleset, "attributeView", name=f'{rule_set_request.attributeView.db_schema}.{rule_set_request.attributeView.name}')
                        keyColumn = ET.SubElement(attributeView, "keyColumn", name=rule_set_request.attributeView.key_column)

                    if rule_set_request.rule is not None:
                        rule = ET.SubElement(ruleset, "rule", name=rule_set_request.rule.name)


                        
                        rule1column1 = ET.SubElement(rule, "column", name=rule_set_request.rule.column.name, minFuzziness=str(rule_set_request.rule.column.minFuzziness))
                        ifMissing = ET.SubElement(rule1column1, "ifMissing", action=rule_set_request.rule.column.ifMissingAction)


                        '''
                        if search_result_set.query.ruleset.rule.column is not None:
                            column = ET.SubElement(rule, "column", name='Rule 1')
                            if search_result_set.query.ruleset.rule.column.ifMissingAction is not None:
                                ifMissing = ET.SubElement(column, "ifMissing", action=search_result_set.query.ruleset.rule.column.ifMissingAction.ifMissingAction)
                        '''
                        # keyColumn = ET.SubElement(attributeView, "keyColumn", name='EMPLOYEE_ID')

                    query.append(ruleset)

            
            

            if search_result_set.query.column is not None:
                for column_request in search_result_set.query.column:
                    column = ET.Element("column", name=column_request.name)
                    if column_request.value is not None:
                        column.text = column_request.value
                    query.append(column)

            # resultsetcolumnSCORE = ET.Element("resultsetcolumn", name="_SCORE")
            # resultsetcolumnRULE_ID = ET.Element("resultsetcolumn", name="_RULE_ID")
            # resultsetcolumnID = ET.Element("resultsetcolumn", name="ID")
            if search_result_set.query.resultsetcolumn is not None:
                query.append(ET.Element("resultsetcolumn", name="_SCORE"))
                query.append(ET.Element("resultsetcolumn", name="_RULE_ID"))
                query.append(ET.Element("resultsetcolumn", name="ID"))
                for resultSetColumn in search_result_set.query.resultsetcolumn:
                    query.append(ET.Element("resultsetcolumn", name=resultSetColumn.name))

            # query = ET.Element("query")
    tree = ET.ElementTree(query)

    # root = tree.getroot()  
    # return tostring(root, encoding='utf8',xml_declaration=False).decode('utf8')

    return tree

def convert_search_rule_set_query_to_string(search_result_set_tree: ET.ElementTree):
    return tostring(search_result_set_tree.getroot(), encoding='utf8',xml_declaration=False).decode('utf8')

if __name__ == '__main__':

    mapped_object = map_query(esh_client.Property(property='aa'))
    assert mapped_object.to_statement() == 'aa'

    mapped_object_b = map_query(esh_client.Property(property=['bb','cc']))
    print(mapped_object_b.to_statement())
    assert mapped_object_b.to_statement() == "bb.cc"

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
        'select': [
                    {
                        'property': 'id'
                    },
                    {
                        'property': 'name'
                    }
                ],
        'estimate': True,
        'wherefound': True,
        'facetlimit': 4,
        'scope': ['S1'],
        'facets': [
                    {
                        'property': 'city'
                    },
                    {
                        'property': 'land'
                    }],
        'filteredgroupby': False,
        'orderby': [
                {
                    'key': {
                        'property': 'city'
                    },
                    'order': 'ASC'
                },
                {
                    'key': {
                        'property': 'language'
                    },
                    'order': 'DESC'
                },
                {
                    'key': {
                        'property': 'land'
                    }
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

    term_definition = {Constants.term: 'mannh"eim', Constants.escapePlaceholders: True,\
        Constants.searchOptions: { \
            Constants.fuzzinessThreshold:0.5,\
            Constants.weight:0.9,\
            Constants.fuzzySearchOptions:'search=typeahead'}}
    # TODO add the test after removing Term class

    fuzzy_search_options_1 = FuzzySearchOptionsInternal()
    fuzzy_search_options_1.similarCalculationMode = esh_client.SimilarCalculationMode.typeAhead;
    searchOpts = SearchOptionsInternal(fuzzinessThreshold=0.5,fuzzySearchOptions=fuzzy_search_options_1,weight=0.9)
    assert searchOpts.to_statement() == '~0.5[similarCalculationMode=typeAhead]^0.9'

    '''      
    term = TermInternal(term='mannh"eim', doEshEscaping=True,\
        searchOptions=SearchOptionsInternal(fuzzinessThreshold=0.5,fuzzySearchOptions='search=typeahead',weight=0.9))
    print(term.to_statement())
    assert term.to_statement() == 'mannh"eim~0.5[search=typeahead]^0.9'
    termHD = TermInternal(term='Heidelberg')
    print(json.dumps(termHD.dict()))
    '''

    '''
    phrase_definition = {'type': 'Phrase','phrase': 'heidelberg', \
        Constants.searchOptions: {\
            Constants.fuzzinessThreshold:0.5,\
            Constants.weight:0.9,\
            Constants.fuzzySearchOptions:'search=typeahead'}}
    phrase = esh_client.Phrase.parse_obj(phrase_definition)
    phrase_mapped = map_query(phrase)
    assert phrase_mapped.to_statement() == '"heidelberg"~0.5[search=typeahead]^0.9'
    '''


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
                    "value": "one"
                }, 
                {
                    "type": "StringValue", 
                    "value": "two"
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
            scope=['Person'],
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


    # Term as StringValue without ESH escaping
    termA = esh_client.StringValue(value='heidelberg')
    termA_mapped = map_query(termA)
    assert termA_mapped.to_statement() == 'heidelberg'

    # Term as StringValue with ESH escaping
    termB = esh_client.StringValue(value='heidel"berg', escapePlaceholders=True)
    termB_mapped = map_query(termB)
    assert termB_mapped.to_statement() == 'heidel"berg' # this means: heidel\"berg

    # Term as StringValue with ESH escaping
    termC = esh_client.StringValue(value='heidel"berg', escapePlaceholders=True, isPhrase=True)
    termC_mapped = map_query(termC)
    assert termC_mapped.to_statement() == '"heidel\\"berg"' # this means: heidel\"berg

    # Phrase as StringValue without ESHEscaping
    phraseA = esh_client.StringValue(value='heidel*berg',isPhrase=True)
    phraseA_mapped = map_query(phraseA)
    assert phraseA_mapped.to_statement() == '"heidel*berg"'

    termD = esh_client.StringValue(value='heidel*berg', escapePlaceholders=True)
    termD_mapped = map_query(termD)
    assert termD_mapped.to_statement() == 'heidel\\*berg' # this means: heidel\*berg

    termE = esh_client.StringValue(value='heidel*berg')
    termE_mapped = map_query(termE)
    assert termE_mapped.to_statement() == 'heidel*berg'


    # Phrase as StringValue with ESHEscaping
    phraseB = esh_client.StringValue(value='mann*heim',isPhrase=True,escapePlaceholders=True)
    phraseB_mapped = map_query(phraseB)
    assert phraseB_mapped.to_statement() == '"mann\\\\*heim"'

    auth_json = '''
        {
            "type": "AuthInternal",
            "value": {
                        "type": "ComparisonInternal",
                        "property": {
                            "type": "PropertyInternal",
                            "property": "city"
                        },
                        "operator": ":",
                        "value": {
                            "type": "StringValueInternal",
                            "value": "Mannheim"
                        }
                    }
        }
    '''
    auth_mapped = AuthInternal.parse_obj(json.loads(auth_json))
    assert auth_mapped.to_statement() == 'AUTH:(city:Mannheim)'
    auth_object_mapped = AuthInternal(
        value=ComparisonInternal(
            property=PropertyInternal(property="city"),
            operator=esh_client.ComparisonOperator.Search,
            value=StringValueInternal(value="walldorf")
        )
    )
    assert auth_object_mapped.to_statement() == 'AUTH:(city:walldorf)'
    esh_object_with_auth_json = '''
        {
            "auth": {
                "type": "AuthInternal",
                "value": {
                        "type": "ComparisonInternal",
                        "property": {
                            "type": "PropertyInternal",
                            "property": "city"
                        },
                        "operator": ":",
                        "value": {
                            "type": "StringValueInternal",
                            "value": "Mannheim"
                        }
                    }
            }
        }
    '''
    esh_object_with_auth_mapped = EshObjectInternal.parse_obj(json.loads(esh_object_with_auth_json))
    assert esh_object_with_auth_mapped.to_statement() == "/$all?$top=10&$apply=filter(Search.search(query='AUTH:(city:Mannheim)'))"

    filter_json = '''
        {
            "type": "Filter",
            "value": {
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
        }
    '''
    filter = esh_client.Filter.parse_obj(json.loads(filter_json))
    filter_mapped = map_query(filter)
    assert filter_mapped.to_statement() == 'FILTER:(city:Mannheim)'
    filter_object = esh_client.Filter(
        value=esh_client.Comparison(
            property=esh_client.Property(property="city"),
            operator=esh_client.ComparisonOperator.Search,
            value=esh_client.StringValue(value="walldorf")
        )
    )
    filter_object_mapped = map_query(filter_object)
    assert filter_object_mapped.to_statement() == 'FILTER:(city:walldorf)'
    esh_object_with_filter_json = '''
        {
            "filter": {
                "type": "Filter",
                "value": {
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
            }
        }
    '''
    esh_object_with_filter = esh_client.EshObject.parse_obj(json.loads(esh_object_with_filter_json))
    esh_object_with_filter_mapped = map_query(esh_object_with_filter)
    assert esh_object_with_filter_mapped.to_statement() == "/$all?$top=10&$apply=filter(Search.search(query='FILTER:(city:Mannheim)'))"    


    filterwf_json = '''
        {
            "type": "FilterWF",
            "value": {
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
        }
    '''
    filterwf = esh_client.FilterWF.parse_obj(json.loads(filterwf_json))
    filterwf_mapped = map_query(filterwf)
    assert filterwf_mapped.to_statement() == 'FILTERWF:(city:Mannheim)'
    filterwf_object = esh_client.FilterWF(
        value=esh_client.Comparison(
            property=esh_client.Property(property="city"),
            operator=esh_client.ComparisonOperator.Search,
            value=esh_client.StringValue(value="walldorf")
        )
    )
    filterwf_object_mapped = map_query(filterwf_object)
    assert filterwf_object_mapped.to_statement() == 'FILTERWF:(city:walldorf)'
    esh_object_with_filterwf_json = '''
        {
            "filter": {
                "type": "FilterWF",
                "value": {
                        "type": "Comparison",
                        "property": {
                            "type": "Property",
                            "property": "city"
                        },
                        "operator": ":",
                        "value": {
                            "type": "StringValue",
                            "value": "Heidelberg"
                        }
                    }
            }
        }
    '''
    esh_object_with_filterwf = esh_client.EshObject.parse_obj(json.loads(esh_object_with_filterwf_json))
    esh_object_with_filterwf_mapped = map_query(esh_object_with_filterwf)
    assert esh_object_with_filterwf_mapped.to_statement() == "/$all?$top=10&$apply=filter(Search.search(query='FILTERWF:(city:Heidelberg)'))"   



    boost_json = '''
        {
            "type": "Boost",
            "value": {
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
        }
    '''
    boost = esh_client.Boost.parse_obj(json.loads(boost_json))
    boost_mapped = map_query(boost)
    assert boost_mapped.to_statement() == 'BOOST:(city:Mannheim)'
    boost_object = esh_client.Boost(
        value=esh_client.Comparison(
            property=esh_client.Property(property="city"),
            operator=esh_client.ComparisonOperator.Search,
            value=esh_client.StringValue(value="walldorf")
        )
    )
    boost_object_mapped = map_query(boost_object)
    assert boost_object_mapped.to_statement() == 'BOOST:(city:walldorf)'
    esh_object_with_boost_json = '''
        {
            "boost": {
                "type": "Boost",
                "value": {
                        "type": "Comparison",
                        "property": {
                            "type": "Property",
                            "property": "city"
                        },
                        "operator": ":",
                        "value": {
                            "type": "StringValue",
                            "value": "Heidelberg"
                        }
                    }
            }
        }
    '''
    esh_object_with_boost = esh_client.EshObject.parse_obj(json.loads(esh_object_with_boost_json))
    esh_object_with_boost_mapped = map_query(esh_object_with_boost)
    assert esh_object_with_boost_mapped.to_statement() == "/$all?$top=10&$apply=filter(Search.search(query='BOOST:(city:Heidelberg)'))"  

    esh_object_with_boost_array_json = '''
        {
            "boost": [
                {
                    "type": "Boost",
                    "value": {
                                "type": "Comparison",
                                "property": {
                                    "type": "Property",
                                    "property": "language"
                                },
                                "operator": ":",
                                "value": {
                                    "type": "StringValue",
                                    "value": "en"
                                }
                            }
                },
                {
                    "type": "Boost",
                    "value": {
                                "type": "Comparison",
                                "property": {
                                    "type": "Property",
                                    "property": "city"
                                },
                                "operator": ":",
                                "value": {
                                    "type": "StringValue",
                                    "value": "mannheim"
                                }
                            }
                }


            ]
        }
    '''
    esh_object_with_boost_array = esh_client.EshObject.parse_obj(json.loads(esh_object_with_boost_array_json))
    esh_object_with_boost_array_mapped = map_query(esh_object_with_boost_array)
    assert esh_object_with_boost_array_mapped.to_statement() == "/$all?$top=10&$apply=filter(Search.search(query='(BOOST:(language:en) BOOST:(city:mannheim))'))"    

    fuzzy_search_options = FuzzySearchOptionsInternal()
    fuzzy_search_options.textSearch = esh_client.TextSearch.compare
    fuzzy_search_options.abbreviationSimilarity = 0.9
    assert fuzzy_search_options.to_statement() == "abbreviationSimilarity=0.9,textSearch=compare"

    string_value_with_fuzzy_options_json = '''
        {
            "type": "StringValue",
            "value": "frankfurt",
            "searchOptions": {
                "fuzzinessThreshold": 0.78,
                "fuzzySearchOptions": {
                    "considerNonMatchingTokens": "input"
                }
            }
        }
    '''
    string_value_with_fuzzy_options = esh_client.StringValue.parse_obj(json.loads(string_value_with_fuzzy_options_json))
    string_value_with_fuzzy_options_mapped = map_query(string_value_with_fuzzy_options)
    assert string_value_with_fuzzy_options_mapped.to_statement() == "frankfurt~0.78[considerNonMatchingTokens=input]"


    termJune = esh_client.StringValue(value='June:')
    termJune_mapped = map_query(termJune)
    assert termJune_mapped.to_statement() == 'June\\:'

    termJune_fuzziness = esh_client.StringValue(value='J?une:', searchOptions=esh_client.SearchOptions(fuzzinessThreshold=0.73))
    termJune_fuzziness_mapped = map_query(termJune_fuzziness)
    assert termJune_fuzziness_mapped.to_statement() == 'J?une\\:~0.73'

    termJune_fuzziness_placeholder = esh_client.StringValue(value='J?une:', escapePlaceholders=True, searchOptions=esh_client.SearchOptions(fuzzinessThreshold=0.73))
    termJune_fuzziness_placeholder_mapped = map_query(termJune_fuzziness_placeholder)
    assert termJune_fuzziness_placeholder_mapped.to_statement() == 'J\\?une\\:~0.73'

    termJune_fuzziness_phrase = esh_client.StringValue(value='J?une:', isPhrase=True, searchOptions=esh_client.SearchOptions(fuzzinessThreshold=0.73))
    termJune_fuzziness_mapped_phrase = map_query(termJune_fuzziness_phrase)
    assert termJune_fuzziness_mapped_phrase.to_statement() == '"J?une\\\\:"~0.73'

    termJune_fuzziness_phrase = esh_client.StringValue(value='J?une:', isPhrase=True, escapePlaceholders=True, searchOptions=esh_client.SearchOptions(fuzzinessThreshold=0.73))
    termJune_fuzziness_mapped_phrase = map_query(termJune_fuzziness_phrase)
    assert termJune_fuzziness_mapped_phrase.to_statement() == '"J\\\\?une\\\\:"~0.73'

    mv = esh_client.MultiValues(items=["firstName", "lastName"])
    co = esh_client.Comparison(
        property= esh_client.MultiValues(items=["firstName", "lastName"],separator=",",encloseStart="(", encloseEnd=")"),
        operator=esh_client.ComparisonOperator.Search,
        value= esh_client.MultiValues(items=["Max", "Mustermann"],encloseStart="(", encloseEnd=")")
    )
    
    
    co_mapped = map_query(co)
    print(co_mapped.to_statement())

    print(' -----> everything fine <----- ')