"""Classes to define a query"""
from enum import Enum
from typing import Any, List, Literal, Annotated, Union
from pydantic import BaseModel, Field

class LogicalOperator(str, Enum):
  AND = "AND"
  TIGHT_AND = ""
  OR = "OR"
  NOT = "NOT"

class ComparisonOperator(str, Enum):
    Search = ":"
    EqualCaseInsensitive = ":EQ:"
    NotEqualCaseInsensitive = ":NE:"
    LessThanCaseInsensitive = ":LT:"
    LessThanOrEqualCaseInsensitive = ":LE:"
    GreaterThanCaseInsensitive = ":GT:"
    GreaterThanOrEqualCaseInsensitive = ":GE:"
    EqualCaseSensitive = ":EQ(S):"
    NotEqualCaseSensitive = ":NE(S):"
    LessThanCaseSensitive = ":LT(S):"
    LessThanOrEqualCaseSensitive = ":LE(S):"
    GreaterThanCaseSensitive = ":GT(S):"
    GreaterThanOrEqualCaseSensitive = ":GE(S):"
    IsNull = ":IS:NULL"
    BetweenCaseInsensitive = ":BT:"
    BetweenCaseSensitive = ":BT(S):"
    DescendantOf = ":DESCENDANT_OF:"
    ChildOf = ":CHILD_OF:"

class WithinOperator(BaseModel):
    type: Literal['WithinOperator'] = 'WithinOperator'
    id: int | None


class CoveredByOperator(BaseModel):
    type: Literal['CoveredByOperator'] = 'CoveredByOperator'
    id: int | None


class IntersectsOperator(BaseModel):
    type: Literal['IntersectsOperator'] = 'IntersectsOperator'
    id: int | None
 
ExpressionValue = Union[Annotated[Union["UnaryExpression", \
    "Expression", "Comparison", "WithinOperator", "CoveredByOperator", \
    "IntersectsOperator", "Point", "LineString", "CircularString", "Polygon", \
    "MultiPoint", "MultiLineString", "MultiPolygon", "GeometryCollection", "NumberValue", \
    "BooleanValue", "StringValue",  "Property",  "MultiValues", "Filter", "FilterWF", \
    "Boost", "RangeValue", "DateValue"], \
    Field(discriminator="type")], str]

class NonMatchingTokens(str, Enum):
   max = "max"
   min = "min"
   all = "all"
   input = 'input'
   table = 'table'

class FuzzySubstringMatch(str, Enum):
    off = 'off'
    on = 'on'
    anywhere = 'anywhere'
    beginning = 'beginning'

class OnEnum(str, Enum):
    on = 'on' 

class ScoreFunction(str, Enum):
    linear = 'linear'
    gaussian = 'gaussian'
    logarithmic = 'logarithmic'

class SearchMode(str, Enum):
    default = 'default'
    null = 'null'
    alphanum = 'alphanum'
    housenumber = 'housenumber'
    postcode = 'postcode'
    identifier = 'identifier'
    alphanum_identifier = 'alphanum_identifier'

class SimilarCalculationMode(str, Enum):
     compare = 'compare'
     typeAhead = 'typeAhead' 
     searchCompare = 'searchCompare'
     search = 'search'
     symmetricSearch = 'symmetricSearch'
     sunstringSearch = 'sunstringSearch'
     flexible = 'flexible'

class TextSearch(str, Enum):
    compare = 'compare'
    fulltext = 'fulltext'

class PhraseCheckFactor(float, Enum):
    zeroNine = 0.9
    one = 1

class FuzzySearchOptions(BaseModel):
    abbreviationSimilarity: float | None #    0.0..1.0
    andSymmetric: float | None #     0.0..1.0
    andThreshold: float | None #     0.0..1.0
    bestMatchingTokenWeight: float | None # 0.0..1.0
    composeWords: int | None #     1..5
    compoundWordWeight: float | None # 0.0..1.0
    considerNonMatchingTokens: NonMatchingTokens | None
    decomposeWords: int | None #    1..5
    emptyScore: float | None # example: 0.9
    errorDevaluate: float | None # 0..1 0.9
    excessTokenWeight: float | None #   0.0..1.0
    fuzzySubstringMatch:FuzzySubstringMatch | None
    interScriptMatching: OnEnum | None
    lengthTolerance: float | None # Range 0..1, default is 0.5
    maxDateDistance: int | None # 5
    minSearchLength: int | None # int 0,1,2,3,4,5
    minTextScore: int | None #  0.0..1.0
    phraseCheckFactor: PhraseCheckFactor | None #  0.9 | 1
    returnAll: OnEnum | None
    scoreFunction: ScoreFunction | None
    scoreFunctionDecay: float | None #  0 <= decay < 1 (linear),  0 < decay < 1 (gaussian)
    scoreFunctionOffset: float | None #     offset >= 0
    scoreFunctionScale: float | None #     scale > 0
    searchMode: SearchMode | None
    similarCalculationMode: SimilarCalculationMode | None
    spellCheckFactor: float | None #    0.0 .. 1.0
    stopwordListId: str | None #    stopwordListId=legalform -> freeform string     stopwordListId=mylist1,mylist2,mylist3
    stopwordTable: str | None #    stopwordTable=[<schemaname>.]<tablename> TODO maybe object schema: str, table: str
    termMappingListId: str | None # TODO maybe list is also possible   termMappingListId=01 => free string => check if it is possible as a list (comma separated string)
    termMappingTable: str | None #  termMappingTable=tm_view
    # TODO maybe with schema as object example with schema: termMappingTable="_SYS_BIC"."tm_map/TM_MAP_VIEW",termMappingListId=01,textSearch=compare
    textSearch: TextSearch | None
class SearchOptions(BaseModel):
    fuzzinessThreshold: float | int | None
    fuzzySearchOptions:  FuzzySearchOptions | None  
    weight: float | int | None


class OrderBySorting(str, Enum):
    asc = "ASC"
    desc = "DESC"

class Property(BaseModel):
    type: Literal['Property'] = 'Property'
    property: list[str]

class OrderBy(BaseModel):
    type: Literal['OrderBy'] = 'OrderBy'
    key: Property
    order: OrderBySorting | None

class StringValue(BaseModel):
    type: Literal['StringValue'] = 'StringValue'
    value: str
    isPhrase: bool | None
    escapePlaceholders: bool | None
    searchOptions: SearchOptions | None

class DateValue(BaseModel):
    type: Literal['DateValue'] = 'DateValue'
    value: str

class NumberValue(BaseModel):
    type: Literal['NumberValue'] = 'NumberValue'
    value: float


class BooleanValue(BaseModel):
    type: Literal['BooleanValue'] = 'BooleanValue'
    value: bool

class RangeValue(BaseModel):
    type: Literal['RangeValue'] = 'RangeValue'
    start: ExpressionValue
    end: ExpressionValue
    excludeStart: bool | None
    excludeEnd: bool | None
class Comparison(BaseModel):
    type: Literal['Comparison'] = 'Comparison'
    property: str | ExpressionValue
    operator: str |  WithinOperator | CoveredByOperator | IntersectsOperator
    value: str | ExpressionValue | None

class Expression(BaseModel):
    type: Literal['Expression'] = 'Expression'
    operator: LogicalOperator | None
    items: list[ExpressionValue] | None


class UnaryOperator(str, Enum):
  NOT = "NOT"
  ROW = "ROW"
  # AUTH = "AUTH"
  # FILTER = "FILTER"
  # FILTERWF = "FILTERWF"
  # BOOST = "BOOST"

class UnaryExpression(BaseModel):
    type: Literal['UnaryExpression'] = 'UnaryExpression'
    operator: UnaryOperator
    item: ExpressionValue


class GeometryBase(BaseModel):
    type: str
    coordinates: list
    searchOptions: SearchOptions | None

class Point(GeometryBase):
    type: Literal['Point'] = 'Point'

class LineString(GeometryBase):
    type: Literal['LineString'] = 'LineString'

class CircularString(GeometryBase):
    type: Literal['CircularString'] = 'CircularString'

class Polygon(GeometryBase):
    type: Literal['Polygon'] = 'Polygon'
    coordinates: List[List[List[float]]]

class MultiPoint(GeometryBase):
    type: Literal['MultiPoint'] = 'MultiPoint'

class MultiLineString(GeometryBase):
    type: Literal['MultiLineString'] = 'MultiLineString'

class MultiPolygon(GeometryBase):
    type: Literal['MultiPolygon'] = 'MultiPolygon'

class GeometryCollection(BaseModel):
    type: Literal['GeometryCollection'] = 'GeometryCollection'
    geometries: list[GeometryBase]


class MultiValues(BaseModel):
    type: Literal['MultiValues'] = 'MultiValues'    
    items: list[ExpressionValue] = []
    separator: str | None = None
    encloseStart: str | None = None
    encloseEnd: str | None = None

class Filter(BaseModel):
    type: Literal['Filter'] = 'Filter'   
    value: Expression | Comparison

class FilterWF(BaseModel):
    type: Literal['FilterWF'] = 'FilterWF'   
    value: Expression | Comparison

class Boost(BaseModel):
    type: Literal['Boost'] = 'Boost'   
    value: Expression | Comparison

    
Comparison.update_forward_refs()
Expression.update_forward_refs()
UnaryExpression.update_forward_refs()
MultiValues.update_forward_refs()
RangeValue.update_forward_refs()

class EshObject(BaseModel):
    type: Literal['EshObject'] = 'EshObject'
    top: int | None
    skip: int | None
    count: bool | None
    scope: List[str] | None
    boost: list[Boost] | None
    filter: Filter | FilterWF | None
    searchQueryFilter: Expression | None
    whyfound: bool | None
    select: list[Property] | None
    orderby: list[OrderBy] | None
    estimate: bool | None
    wherefound: bool | None
    facetlimit: int | None
    facets: list[Property] | None
    filteredgroupby: bool | None
    suggestTerm: str | None
    resourcePath:str | None

    class Config:
        extra = 'forbid'



class AttributeView(BaseModel):
    db_schema: str | None = Field(..., alias='schema')
    name: str | None
    key_column: str | None

class Column(BaseModel):
    name: str | None
    value: str | None
    minFuzziness: float | None
    ifMissingAction: str | None
# class Rule(BaseModel):
#    name: str | None
#    column: Column | None

class Rule(BaseModel):
    name: str
    columns: list[Column]
class RuleSet(BaseModel):
    # scoreSelection currently only firstRule
    attributeView: AttributeView | None
    rules: list[Rule] | None
    # name: str

class ResultSetColumn(BaseModel):
    name: str
class Query(BaseModel):
    limit: int | None
    offset: int | None
    ruleset: list[RuleSet] | None # TODO check if it can be a list
    column: list[Column] | None # TODO make it as list
    resultsetcolumn: list[ResultSetColumn] | None

class Parameter(BaseModel):
    name: str
    value: StringValue | NumberValue | BooleanValue | DateValue | MultiValues
class SearchRuleSet(BaseModel):
    query: Query | None




class EshRequest(BaseModel):
    parameters: list[Parameter] | None
    query: EshObject
    rules: list[Rule] | None
