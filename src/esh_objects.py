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
    "ExpressionInternal", "ComparisonInternal","WithinOperatorInternal", "CoveredByOperatorInternal", \
    "IntersectsOperatorInternal",  "PointInternal", "LineStringInternal", "CircularStringInternal", "PolygonInternal", \
    "MultiPointInternal", "MultiLineStringInternal", "MultiPolygonInternal", "GeometryCollectionInternal", "NumberValueInternal", \
    "BooleanValueInternal", "StringValueInternal", "AuthInternal", "FilterInternal", "FilterWFInternal", \
    "PropertyInternal",  "MultiValuesInternal", "BoostInternal", "RangeValueInternal", "DateValueInternal"], \
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

    def to_statement(self):
        return ".".join(self.property)

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

class DateValueInternal(esh_client.DateValue):

    def to_statement(self):
        return f'{self.value}'

class BooleanValueInternal(esh_client.BooleanValue):

    def to_statement(self):
        return json.dumps(self.value)

class RangeValueInternal(esh_client.RangeValue):

    type: Literal['RangeValueInternal'] = 'RangeValueInternal'
    start: ExpressionValueInternal
    end: ExpressionValueInternal

    def to_statement(self):
        start_bracket = "]" if self.excludeStart else "["
        end_bracket = "[" if self.excludeEnd else "]"

        start_to_statement = getattr(self.start, "to_statement", None)
        if callable(start_to_statement):
            start_value = self.start.to_statement()
        else:
            start_value = self.start
        end_to_statement = getattr(self.end, "to_statement", None)
        if callable(end_to_statement):
            end_value = self.end.to_statement()
        else:
            end_value = self.end

        return f'{start_bracket}{start_value} {end_value}{end_bracket}'

class ComparisonInternal(BaseModel):
    type: Literal['ComparisonInternal'] = 'ComparisonInternal'
    property: str | ExpressionValueInternal
    operator: esh_client.ComparisonOperator | ExpressionValueInternal
    value: str | ExpressionValueInternal | None

    def to_statement(self):
        property_to_statement = getattr(self.property, "to_statement", None)
        if callable(property_to_statement):
            property = self.property.to_statement()
        else:
            property = self.property
        operator_to_statement = getattr(self.operator, "to_statement", None)
        if callable(operator_to_statement):
            operator_to_statement = self.operator.to_statement()
        else:
            operator_to_statement = self.operator
        value_to_statement = getattr(self.value, "to_statement", None)
        if callable(value_to_statement):
            value = self.value.to_statement()
        else:
            value = self.value
        return f'{property}{operator_to_statement}{value}'

        
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


class WithinOperatorInternal(esh_client.WithinOperator):
    type: Literal['WithinOperatorInternal'] = 'WithinOperatorInternal'

    def to_statement(self) -> str:
        if self.id:
            return f':WITHIN({str(self.id)}):'
        else:
            return ':WITHIN:'


class CoveredByOperatorInternal(esh_client.CoveredByOperator):
    type: Literal['CoveredByOperatorInternal'] = 'CoveredByOperatorInternal'

    def to_statement(self) -> str:
        if self.id:
            return f':COVERED_BY({str(self.id)}):'
        else:
            return ':COVERED_BY:'

class IntersectsOperatorInternal(esh_client.IntersectsOperator):
    type: Literal['IntersectsOperatorInternal'] = 'IntersectsOperatorInternal'

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
RangeValueInternal.update_forward_refs()
class EshObjectInternal(esh_client.EshObject):
    type: Literal['EshObjectInternal'] = 'EshObjectInternal' 
    searchQueryFilter: ExpressionInternal | None
    orderby: List[OrderByInternal] | None
    auth: AuthInternal | None
    filter: FilterInternal | FilterWFInternal | None
    boost: list[BoostInternal] | None
    facets: list[PropertyInternal] | None
    select: list[PropertyInternal] | None
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
            case 'NumberValue':
                result = NumberValueInternal(
                    value= item.value
                )
            case 'DateValue':
                result = DateValueInternal(
                    value= item.value
                )
            case 'BooleanValue':
                result = BooleanValueInternal(
                    value=item.value
                )
            case 'RangeValue':
                result = RangeValueInternal(
                    start=map_query(item.start),
                    end=map_query(item.end),
                    excludeStart=item.excludeStart,
                    excludeEnd=item.excludeEnd
                )
            case 'Property':
                result = PropertyInternal(
                    property = item.property
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
            case 'WithinOperator':
                result = WithinOperatorInternal(
                    id=item.id
                )
            case 'CoveredByOperator':
                result = CoveredByOperatorInternal(
                    id=item.id
                )
            case 'IntersectsOperator':
                result = IntersectsOperatorInternal(
                    id=item.id
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
                        attributeView = ET.SubElement(ruleset, "attributeView", name=f'"{rule_set_request.attributeView.db_schema}"."{rule_set_request.attributeView.name}"')
                        # TODO add nonUniqueKeys only if there are 1:n joins and return only unique IDs
                        attributeView.set("nonUniqueKeys","true")
                        keyColumn = ET.SubElement(attributeView, "keyColumn", name=rule_set_request.attributeView.key_column)

                    if rule_set_request.rules is not None:
                        for rule_definition in rule_set_request.rules:
                            rule = ET.SubElement(ruleset, "rule", name=rule_definition.name)


                            for ruleset_column in rule_definition.columns:
                                rule1column1 = ET.SubElement(rule, "column", name=ruleset_column.name, minFuzziness=str(ruleset_column.minFuzziness))
                                ifMissing = ET.SubElement(rule1column1, "ifMissing", action=ruleset_column.ifMissingAction)


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
    ET.indent(tree, space=" ", level=0)

    # root = tree.getroot()  
    # return tostring(root, encoding='utf8',xml_declaration=False).decode('utf8')

    return tree

def convert_search_rule_set_query_to_string(search_result_set_tree: ET.ElementTree):
    return tostring(search_result_set_tree.getroot(), encoding='utf8',xml_declaration=False).decode('utf8')

