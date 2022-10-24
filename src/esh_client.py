"""Classes to define a query"""
from enum import Enum
from typing import List, Literal, Annotated, Union
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

 
ExpressionValue = Union[Annotated[Union["UnaryExpression", \
    "Expression", "Comparison", "WithinOperator", "CoveredByOperator", \
    "IntersectsOperator", "Term", "Point", "LineString", "CircularString", "Polygon", \
    "MultiPoint", "MultiLineString", "MultiPolygon", "GeometryCollection", "NumberValue", \
    "BooleanValue", "StringValue", "Phrase", "Property",  "MultiValues"], \
    Field(discriminator="type")], str]

class SearchOptions(BaseModel):
    fuzzinessThreshold: float | int | None
    fuzzySearchOptions:  str | None  
    weight: float | int | None


class OrderBySorting(str, Enum):
    asc = "ASC"
    desc = "DESC"

class OrderBy(BaseModel):
    key: str
    order: OrderBySorting | None


class Property(BaseModel):
    type: Literal['Property'] = 'Property'
    property: str | list[str]
    prefixOperator: str | None


    
class Term(BaseModel):
    type: Literal['Term'] = 'Term'
    term: str 
    isQuoted: bool | None
    doEshEscaping: bool | None
    searchOptions: SearchOptions | None



class Phrase(BaseModel):
    type: Literal['Phrase'] = 'Phrase'
    phrase: str
    searchOptions: SearchOptions | None
    doEshEscaping: bool | None


class StringValue(BaseModel):
    type: Literal['StringValue'] = 'StringValue'
    value: str
    isQuoted: bool | None
    isSingleQuoted: bool | None
    withoutEnclosing: bool | None
    searchOptions: SearchOptions | None



class NumberValue(BaseModel):
    type: Literal['NumberValue'] = 'NumberValue'
    value: int | float


class BooleanValue(BaseModel):
    type: Literal['BooleanValue'] = 'BooleanValue'
    value: bool
class Comparison(BaseModel):
    type: Literal['Comparison'] = 'Comparison'
    property: str | ExpressionValue
    operator: ComparisonOperator
    value: str | ExpressionValue | None

class Expression(BaseModel):
    type: Literal['Expression'] = 'Expression'
    operator: LogicalOperator | None
    items: List[ExpressionValue] | None


class UnaryOperator(str, Enum):
  NOT = "NOT"
  ROW = "ROW"
  AUTH = "AUTH"
  FILTER = "FILTER"
  FILTERWF = "FILTERWF"
  BOOST = "BOOST"

class UnaryExpression(BaseModel):
    type: Literal['UnaryExpression'] = 'UnaryExpression'
    operator: UnaryOperator
    item: ExpressionValue


class WithinOperator(BaseModel):
    type: Literal['WithinOperator'] = 'WithinOperator'
    id: int | None


class CoveredByOperator(BaseModel):
    type: Literal['CoveredByOperator'] = 'CoveredByOperator'
    id: int | None


class IntersectsOperator(BaseModel):
    type: Literal['IntersectsOperator'] = 'IntersectsOperator'
    id: int | None


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
    items: List[ExpressionValue] = []
    separator: str | None = None
    encloseStart: str | None = None
    encloseEnd: str | None = None

    
Comparison.update_forward_refs()
Expression.update_forward_refs()
UnaryExpression.update_forward_refs()

class EshObject(BaseModel):
    type: Literal['EshObject'] = 'EshObject'
    top: int | None
    skip: int | None
    count: bool | None
    scope: str | List[str] | None
    searchQueryFilter: Expression | None
    whyfound: bool | None
    select: list[str] | None
    orderby: List[OrderBy] | None
    estimate: bool | None
    wherefound: bool | None
    facetlimit: int | None
    facets: list[str] | None
    filteredgroupby: bool | None
    suggestTerm: str | None
    resourcePath:str | None

    class Config:
        extra = 'forbid'

