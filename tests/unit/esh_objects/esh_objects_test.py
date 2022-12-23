import unittest
import json

import esh_client
import esh_objects


class TestStringMethods(unittest.TestCase):

    
    def test_term(self):
        term = esh_objects.StringValueInternal(value="Heidelberg")
        self.assertEqual(term.to_statement(), 'Heidelberg')

        term_json = '''
            {
                "type": "StringValue",
                "value": "Heidelberg"
            }
        '''
        term_dict = json.loads(term_json)
        term2 = esh_client.StringValue.parse_obj(term_dict)
        self.assertEqual(term2.dict(exclude_none=True), term_dict)


    def test_phrase(self):
        phrase = esh_client.StringValue(value="Mannheim", isPhrase=True)
        phrase_mapped = esh_objects.map_query(phrase)
        self.assertEqual(phrase_mapped.to_statement(), '"Mannheim"')

        phrase_json = '''
            {
                "type": "StringValue",
                "value": "Mannheim",
                "isPhrase": true
            }
        '''
        phrase_dict = json.loads(phrase_json)
        phrase2 = esh_client.StringValue.parse_obj(phrase_dict)
        phrase2_mapped = esh_objects.map_query(phrase2)
        self.assertEqual(phrase2.dict(exclude_none=True), phrase_dict)


    def test_expression(self):
        expression_object = esh_client.Expression(
                operator=esh_client.LogicalOperator.AND,
                items= [
                    esh_client.Comparison(
                        property= esh_client.Property(property=['lastName']),
                        operator= esh_client.ComparisonOperator.Search,
                        value= esh_client.StringValue(value='Doe')),
                    esh_client.Comparison(
                        property= esh_client.Property(property=['firstName']),
                        operator= esh_client.ComparisonOperator.Search,
                        value= esh_client.StringValue(value='Jane'))
                ]
            )
        expression_json = '''
            {
                "type": "Expression",
                "operator": "AND",
                "items": [
                    {
                        "type": "Comparison",
                        "property": {
                            "type": "Property",
                            "property": ["lastName"]
                        },
                        "operator": ":",
                        "value": {
                            "type": "StringValue",
                            "value": "Doe"
                        }
                    },
                    {
                        "type": "Comparison",
                        "property": {
                            "type": "Property",
                            "property": ["firstName"]
                        },
                        "operator": ":",
                        "value": {
                            "type": "StringValue",
                            "value": "Jane"
                        }
                    }
                ]
            }
        '''
        expression_dict = json.loads(expression_json)
        expression = esh_client.Expression.parse_obj(expression_dict)
        expression_mapped = esh_objects.map_query(expression)
        self.assertEqual(expression_mapped.to_statement(), "(lastName:Doe AND firstName:Jane)")
        self.assertEqual(expression_object.dict(exclude_none=True),expression_dict)

    def test_string_value(self):
        so = esh_client.EshObject(
            count=True,
            top=1,
            searchQueryFilter=esh_client.Expression(
                operator=esh_client.LogicalOperator.AND,
                items= [
                    esh_client.Comparison(
                        property= esh_client.Property(property=['firstName']),
                        operator= esh_client.ComparisonOperator.Search,
                        value= esh_client.StringValue(
                            value='Jane',
                            searchOptions=esh_client.SearchOptions(fuzzinessThreshold=0.7)))]))
        so_mapped = esh_objects.map_query(so)
        # print(so_mapped.to_statement())
        # TODO
        # self.assertEqual(so_mapped.to_statement(),"/$all?$top=1&$count=true&$apply=filter(Search.search(query='SCOPE:Person AND firstName:Jane~0.7'))")

    def test_row(self):
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
                                                property= esh_client.Property(property=['lastName']),
                                                operator= esh_client.ComparisonOperator.Search,
                                                value= esh_client.StringValue(value='Doe')),
                                            esh_client.Comparison(
                                                property= esh_client.Property(property=['firstName']),
                                                operator= esh_client.ComparisonOperator.Search,
                                                value= esh_client.StringValue(value='John'))
                                                ]
                            ),
                            esh_client.Expression(
                                operator=esh_client.LogicalOperator.AND,
                                items= [
                                        esh_client.Comparison(
                                            property= esh_client.Property(property=['lastName']),
                                            operator= esh_client.ComparisonOperator.Search,
                                            value= esh_client.StringValue(value='Doe')),
                                        esh_client.Comparison(
                                            property= esh_client.Property(property=['firstName']),
                                            operator= esh_client.ComparisonOperator.Search,
                                            value= esh_client.StringValue(value='Jane'))
                                    ]
                            )
                        ]
                    )
        )
        so_mapped = esh_objects.map_query(so)
        #print(f'ESH query statement: {so_mapped.to_statement()}')
        #print('-----cccc-----')
        #print(json.dumps(so_mapped.dict(exclude_none=True), indent=2))
        #print(so_mapped.to_statement())
        self.assertEqual(so_mapped.to_statement(), "/$all?$top=10&$count=true&$apply=filter(Search.search(query='SCOPE:Person ((lastName:Doe AND firstName:John) OR (lastName:Doe AND firstName:Jane))'))")

    def test_esh_objects_main_tests(self):
        mapped_object = esh_objects.map_query(esh_client.Property(property=['aa']))
        self.assertEqual(mapped_object.to_statement(), 'aa')

        mapped_object_b = esh_objects.map_query(esh_client.Property(property=['bb','cc']))
        print(mapped_object_b.to_statement())
        self.assertEqual(mapped_object_b.to_statement(), "bb.cc")

        mapped_comparison = esh_objects.map_query(esh_client.Comparison(property="land",operator=esh_client.ComparisonOperator.EqualCaseInsensitive,value="negde"))
        m_items = [esh_client.StringValue(value='www'), esh_client.StringValue(value='222'), esh_client.StringValue(value='333')]

        comp = {'property': "language", \
            'operator': ':EQ:', 'value': { esh_objects.Constants.type: 'StringValue', 'value': 'Python'}}
        aas = esh_objects.map_query(esh_client.Comparison.parse_obj(comp))
        self.assertEqual(aas.to_statement(), 'language:EQ:Python')

        comp1 = {'property': {'type':"Property", "property": ["language"]}, \
            'operator': ':EQ:', 'value': { esh_objects.Constants.type: 'StringValue', 'value': 'Java'}}
        aas1 = esh_objects.map_query(esh_client.Comparison.parse_obj(comp1))
        self.assertEqual(aas1.to_statement(), 'language:EQ:Java')



        exp1 = esh_objects.map_query(esh_client.Expression(items=[esh_client.StringValue(value='MMMM'),\
            esh_client.StringValue(value='KKK')], operator='OR'))
        self.assertEqual(exp1.to_statement(), '(MMMM OR KKK)')
    
        aa = esh_client.EshObject.parse_obj({'searchQueryFilter': { esh_objects.Constants.type: 'Expression', 'items' : [{'type': 'StringValue', \
        'value': 'aaa'},{'type': 'StringValue', 'value': 'bbb'}], 'operator': 'AND'}})
        bbb = esh_objects.map_query(aa)
        self.assertEqual(bbb.to_statement(), "/$all?$top=10&$apply=filter(Search.search(query='(aaa AND bbb)'))")

        exp2 = esh_objects.ExpressionInternal()
        exp2.operator = 'AND'
        exp2.items = []
        exp2.items.append(esh_objects.StringValueInternal(value='mannheim'))
        exp2.items.append(esh_objects.StringValueInternal(value='heidelberg'))
        self.assertEqual(exp2.to_statement(), '(mannheim AND heidelberg)')


        json_body={
            'top': 10,
            'count': True,
            'whyfound': True,
            'select': [
                        {
                            'property': ['id']
                        },
                        {
                            'property': ['name']
                        }
                    ],
            'estimate': True,
            'wherefound': True,
            'facetlimit': 4,
            'scope': ['S1'],
            'facets': [
                        {
                            'property': ['city']
                        },
                        {
                            'property': ['land']
                        }],
            'filteredgroupby': False,
            'orderby': [
                    {
                        'key': {
                            'property': ['city']
                        },
                        'order': 'ASC'
                    },
                    {
                        'key': {
                            'property': ['language']
                        },
                        'order': 'DESC'
                    },
                    {
                        'key': {
                            'property': ['land']
                        }
                    }
                ],
            'searchQueryFilter': { esh_objects.Constants.type: 'Expression',\
                'operator': 'OR',\
                'items' :[\
                    {'type': 'StringValue', 'value': 'test'},\
                    {'type': 'StringValue', 'value': 'function'}]
                }
            }


        es_objects = esh_client.EshObject.parse_obj(json_body)
        es_mapped_objects = esh_objects.map_query(es_objects)
        print(es_mapped_objects.to_statement())
        # print(json.dumps(es_objects.searchQueryFilter.to_dict(), indent=4))
        # print(json.dumps(es_objects.to_dict(), indent=4))
        expected_statement = '/$all?$top=10&$count=true&$apply=filter(' \
            'Search.search(query=\'SCOPE:S1 (test OR function)\'' \
            '))&whyfound=true&$select=id,name&$orderby=city ASC,language DESC,' \
            'land&estimate=true&wherefound=true&facetlimit=4&facets=city,land&filteredgroupby=false'
        print(es_mapped_objects.to_statement())
        self.assertEqual(es_mapped_objects.to_statement(), expected_statement)

        sv = esh_client.StringValue(value='sss', isQuoted=True)
        # print(sv.__dict__)

        # print(json.dumps(sv.__dict__))
        # print(json.dumps(exp2.__dict__, indent=4))
        org_str = "a*\\a\\a*b?b'c'd?\"ee\"ff"
        #print(org_str)
        #print(escapePhrase(org_str))


        esc_query = 'n AND a OR c'
        #print(escapeQuery(esc_query))

        term_definition = { esh_objects.Constants.term: 'mannh"eim', esh_objects.Constants.escapePlaceholders: True,\
            esh_objects.Constants.searchOptions: { \
                esh_objects.Constants.fuzzinessThreshold:0.5,\
                esh_objects.Constants.weight:0.9,\
                esh_objects.Constants.fuzzySearchOptions:'search=typeahead'}}
        # TODO add the test after removing Term class

        fuzzy_search_options_1 = esh_objects.FuzzySearchOptionsInternal()
        fuzzy_search_options_1.similarCalculationMode = esh_client.SimilarCalculationMode.typeAhead;
        searchOpts = esh_objects.SearchOptionsInternal(fuzzinessThreshold=0.5,fuzzySearchOptions=fuzzy_search_options_1,weight=0.9)
        self.assertEqual(searchOpts.to_statement(), '~0.5[similarCalculationMode=typeAhead]^0.9')

        '''      
        term = TermInternal(term='mannh"eim', doEshEscaping=True,\
            searchOptions=SearchOptionsInternal(fuzzinessThreshold=0.5,fuzzySearchOptions='search=typeahead',weight=0.9))
        print(term.to_statement())
        self.assertEqual(term.to_statement() == 'mannh"eim~0.5[search=typeahead]^0.9'
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
        phrase_mapped = esh_objects.map_query(phrase)
        self.assertEqual(phrase_mapped.to_statement() == '"heidelberg"~0.5[search=typeahead]^0.9'
        '''


        suggest_json_body={
            'suggestTerm': 'bas'
        }
        suggest_es_object = esh_client.EshObject.parse_obj(suggest_json_body)
        suggest_es_object_mapped = esh_objects.map_query(suggest_es_object)
        print(suggest_es_object_mapped.to_statement())
        self.assertEqual(suggest_es_object_mapped.to_statement(), "/$all/GetSuggestion(term='bas')?$top=10")


        metadata_json_body={
            'resourcePath': '/$metadata'
        }
        metadata_es_object = esh_client.EshObject.parse_obj(metadata_json_body)
        metadata_es_object_mapped = esh_objects.map_query(metadata_es_object)
        self.assertEqual(metadata_es_object_mapped.to_statement(), '/$metadata')



        self.assertEqual(esh_objects.WithinOperatorInternal().to_statement(), ':WITHIN:')
        self.assertEqual(esh_objects.WithinOperatorInternal(id=4).to_statement(), ':WITHIN(4):')

        self.assertEqual(esh_objects.CoveredByOperatorInternal().to_statement(), ':COVERED_BY:')
        self.assertEqual(esh_objects.CoveredByOperatorInternal(id=5).to_statement(), ':COVERED_BY(5):')

        self.assertEqual(esh_objects.IntersectsOperatorInternal().to_statement(), ':INTERSECTS:')
        self.assertEqual(esh_objects.IntersectsOperatorInternal(id=6).to_statement(), ':INTERSECTS(6):')

        self.assertEqual(esh_objects.escapePhrase('aaa?bbb'), 'aaa\\?bbb')

        json_expression = '''
            {
                "type": "Expression",
                "items": [
                    {
                        "type": "Property",
                        "property": ["city"]
                    },{
                        "type": "Property",
                        "property": ["country"]
                    }
                ]
            }
        '''
        deserialized_object_expression = esh_client.Expression.parse_obj(json.loads(json_expression))
        # self.assertEqual(deserialized_object_expression.type == Expression.__name__
        # print(json.dumps(deserialized_object_expression.to_dict()))
        # print(deserialized_object_expression.to_statement())
        deserialized_object_expression_mapped = esh_objects.map_query(deserialized_object_expression)
        self.assertEqual(deserialized_object_expression_mapped.to_statement(), '(city country)')

        json_property = '''
            {
                "type": "Property",
                "property": ["city"]
            }
        '''
        deserialized_object_property_city = esh_client.Property.parse_obj(json.loads(json_property))
        self.assertEqual(deserialized_object_property_city.type, esh_client.Property.__name__)

        object_property_internal_mapped = esh_objects.map_query(deserialized_object_property_city)
        print(object_property_internal_mapped.to_statement())
        print(json.dumps(object_property_internal_mapped.dict()))

        self.assertTrue(isinstance(object_property_internal_mapped, esh_client.Property))
        self.assertTrue(isinstance(object_property_internal_mapped, esh_objects.PropertyInternal))
        self.assertTrue(object_property_internal_mapped.to_statement() == 'city')

        json_comparison = '''
                {
                    "type": "Comparison",
                    "property": {
                        "type": "Property",
                        "property": ["city"]
                    },
                    "operator": ":",
                    "value": {
                        "type": "StringValue",
                        "value": "Mannheim"
                    }
                }
            '''






        deserialized_object_comparison = esh_client.Comparison.parse_obj(json.loads(json_comparison))
        self.assertEqual(deserialized_object_comparison.type, esh_client.Comparison.__name__)
        deserialized_object_comparison_mapped = esh_objects.map_query(deserialized_object_comparison)
        self.assertEqual(deserialized_object_comparison_mapped.to_statement(), 'city:Mannheim')

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
        self.assertEqual(des_obj.type, "MultiValues")
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
        self.assertEqual(deserialized_object_point.type, "Point")
        deserialized_object_point_mapped = esh_objects.map_query(deserialized_object_point)
        self.assertEqual(deserialized_object_point_mapped.to_statement(), "POINT(1.1 2.2)^3.2")

        circular_string_json = '''
            {
                "type": "CircularString", 
                "coordinates": [
                    [33.3, 11.1], [11.1, 33.3], [44.4, 44.4]
                ]
            }
        '''
        deserialized_object_circular_string = esh_client.CircularString.parse_obj(json.loads(circular_string_json))
        self.assertEqual(deserialized_object_circular_string.type, "CircularString")
        deserialized_object_circular_string_mapped = esh_objects.map_query(deserialized_object_circular_string)
        self.assertEqual(deserialized_object_circular_string_mapped.to_statement(), "CIRCULARSTRING(33.3 11.1,11.1 33.3,44.4 44.4)")

        linestring_json = '''
            {
                "type": "LineString", 
                "coordinates": [
                    [33.3, 11.1], [11.1, 33.3], [44.4, 44.4]
                ]
            }
        '''
        deserialized_object_linestring = esh_client.LineString.parse_obj(json.loads(linestring_json))
        self.assertEqual(deserialized_object_linestring.type, "LineString")
        deserialized_object_linestring_mapped = esh_objects.map_query(deserialized_object_linestring)
        self.assertEqual(deserialized_object_linestring_mapped.to_statement(), "LINESTRING(33.3 11.1,11.1 33.3,44.4 44.4)")

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
        self.assertEqual(deserialized_object_polygon.type, esh_client.Polygon.__name__)
        deserialized_object_polygon_mapped = esh_objects.map_query(deserialized_object_polygon)
        self.assertEqual(deserialized_object_polygon_mapped.to_statement(), "POLYGON((30.3 10.1,40.4 40.4,10.1 30.3,30.3 10.1))")

        multipoint_json = '''
            {
                "type": "MultiPoint", 
                "coordinates": [
                    [11.1, 44.4], [44.4, 33.3], [22.2, 22.2], [33.3, 11.1]
                ]
            }
        '''
        deserialized_object_multipoint = esh_client.MultiPoint.parse_obj(json.loads(multipoint_json))
        self.assertEqual(deserialized_object_multipoint.type, "MultiPoint")
        deserialized_object_multipoint_mapped = esh_objects.map_query(deserialized_object_multipoint)
        self.assertEqual(deserialized_object_multipoint_mapped.to_statement(), "MULTIPOINT(11.1 44.4,44.4 33.3,22.2 22.2,33.3 11.1)")

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
        self.assertEqual(deserialized_object_multilinestring.type, "MultiLineString")
        deserialized_object_multilinestring_mapped = esh_objects.map_query(deserialized_object_multilinestring)
        self.assertEqual(deserialized_object_multilinestring_mapped.to_statement(), "MULTILINESTRING((11.1 11.1,22.2 22.2,11.1 44.4),(44.4 44.4,33.3 33.3,44.4 22.2,33.3 11.1))")

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
        self.assertEqual(deserialized_object_multipolygon.type, "MultiPolygon")
        deserialized_object_multipolygon_mapped = esh_objects.map_query(deserialized_object_multipolygon)
        self.assertEqual(deserialized_object_multipolygon_mapped.to_statement(), "MULTIPOLYGON(((33.3 22.2,45.4 44.4,11.1 44.4,33.3 22.2)),((15.4 5.4,44.4 11.1,11.1 22.2,5.4 11.1,15.4 5.4)))")

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
        self.assertEqual(deserialized_object_multipolygon2.type, "MultiPolygon")
        deserialized_object_multipolygon2_mapped = esh_objects.map_query(deserialized_object_multipolygon2)
        self.assertEqual(deserialized_object_multipolygon2_mapped.to_statement(), "MULTIPOLYGON(((44.4 44.4,22.2 45.4,45.4 33.3,44.4 44.4)),((22.2 35.4,11.1 33.3,11.1 11.1,33.3 5.4,45.4 22.2,22.2 35.4),(33.3 22.2,22.2 15.4,22.2 25.4,33.3 22.2)))")

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
        self.assertEqual(deserialized_object_multigeometry_collection.type, "GeometryCollection")
        self.assertEqual(deserialized_object_multigeometry_collection.geometries[0].type, "Point")
        self.assertEqual(deserialized_object_multigeometry_collection.geometries[1].type, "LineString")
        self.assertEqual(deserialized_object_multigeometry_collection.geometries[2].type, "Polygon")

        deserialized_object_multigeometry_collection_mapped = esh_objects.map_query(deserialized_object_multigeometry_collection)
        self.assertEqual(deserialized_object_multigeometry_collection_mapped.type, "GeometryCollectionInternal")
        self.assertEqual(deserialized_object_multigeometry_collection_mapped.geometries[0].type, "PointInternal")
        self.assertEqual(deserialized_object_multigeometry_collection_mapped.geometries[1].type, "LineStringInternal")
        self.assertEqual(deserialized_object_multigeometry_collection_mapped.geometries[2].type, "PolygonInternal")
        print(deserialized_object_multigeometry_collection_mapped.to_statement())
        self.assertEqual(deserialized_object_multigeometry_collection_mapped.to_statement(), "GEOMETRYCOLLECTION(GEOMETRYBASE(44.4 11.1),GEOMETRYBASE(11.1 11.1,22.2 22.2,11.1 44.4),GEOMETRYBASE((30.3 10.1,40.4 40.4,10.1 30.3,30.3 10.1)))")

        self.assertEqual(esh_objects.serialize_geometry_collection([1.1,2.2]), "1.1 2.2")
        self.assertEqual(esh_objects.serialize_geometry_collection([[1.1,2.2],[3.3,4.4]]), "(1.1 2.2,3.3 4.4)")
        self.assertEqual(esh_objects.serialize_geometry_collection([[[1.1,2.2],[3.3,4.4]],[[5.5,6.6],[7.7,8.8]]]), "((1.1 2.2,3.3 4.4),(5.5 6.6,7.7 8.8))")

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

        property_simple = esh_client.Property(property=["someText"])
        property_simple_mapped = esh_objects.map_query(property_simple)
        self.assertEqual(property_simple_mapped.to_statement(), 'someText')

        property_array = esh_client.Property(property=["one", "two"])
        property_array_mapped = esh_objects.map_query(property_array)
        self.assertEqual(property_array_mapped.to_statement(), 'one.two')
        

        so = esh_client.EshObject(
            searchQueryFilter=esh_client.Expression(
                operator='AND',
                items= [
                    esh_client.Comparison(
                        property= esh_client.Property(property=['lastName']),
                        operator= esh_client.ComparisonOperator.Search,
                        value= esh_client.StringValue(value='Doe')),
                    esh_client.Comparison(
                        property= esh_client.Property(property=['firstName']),
                        operator= esh_client.ComparisonOperator.Search,
                        value= esh_client.StringValue(value='Jane'))
                    ]
                )
        )
        so_mapped = esh_objects.map_query(so)
        print(so_mapped.to_statement())
        # print(json.dumps(so.dict(exclude_none=True), indent = 4))

        self.assertEqual(so_mapped.to_statement(), "/$all?$top=10&$apply=filter(Search.search(query='(lastName:Doe AND firstName:Jane)'))")


        mv = esh_client.MultiValues(items=["one", "two"], separator=",", encloseStart="[", encloseEnd="]")
        mv_mapped = esh_objects.map_query(mv)
        self.assertEqual(mv_mapped.to_statement(), "[one,two]")

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
        unary_expression_mapped = esh_objects.map_query(unary_expression)  
        self.assertEqual(unary_expression_mapped.to_statement(), "ROW:(city:EQ:Mannheim AND company:EQ:SAP)")
        
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
                                                    property= esh_client.Property(property=['lastName']),
                                                    operator= esh_client.ComparisonOperator.Search,
                                                    value= esh_client.StringValue(value='Doe')),
                                                esh_client.Comparison(
                                                    property= esh_client.Property(property=['firstName']),
                                                    operator= esh_client.ComparisonOperator.Search,
                                                    value= esh_client.StringValue(value='John'))
                                                    ]
                                ),
                                esh_client.Expression(
                                    operator=esh_client.LogicalOperator.AND,
                                    items= [
                                            esh_client.Comparison(
                                                property= esh_client.Property(property=['lastName']),
                                                operator= esh_client.ComparisonOperator.Search,
                                                value= esh_client.StringValue(value='Doe')),
                                            esh_client.Comparison(
                                                property= esh_client.Property(property=['firstName']),
                                                operator= esh_client.ComparisonOperator.Search,
                                                value= esh_client.StringValue(value='Jane'))
                                        ]
                                )
                            ]
                        )
            )
        so_mapped = esh_objects.map_query(so)
        #print(f'ESH query statement: {so_mapped.to_statement()}')
        #print('-----cccc-----')
        #print(json.dumps(so_mapped.dict(exclude_none=True), indent=2))
        self.assertEqual(so_mapped.to_statement(), "/$all?$top=10&$count=true&$apply=filter(Search.search(query='SCOPE:Person ((lastName:Doe AND firstName:John) OR (lastName:Doe AND firstName:Jane))'))")


        # Term as StringValue without ESH escaping
        termA = esh_client.StringValue(value='heidelberg')
        termA_mapped = esh_objects.map_query(termA)
        self.assertEqual(termA_mapped.to_statement(), 'heidelberg')

        # Term as StringValue with ESH escaping
        termB = esh_client.StringValue(value='heidel"berg', escapePlaceholders=True)
        termB_mapped = esh_objects.map_query(termB)
        self.assertEqual(termB_mapped.to_statement(), 'heidel"berg') # this means: heidel\"berg

        # Term as StringValue with ESH escaping
        termC = esh_client.StringValue(value='heidel"berg', escapePlaceholders=True, isPhrase=True)
        termC_mapped = esh_objects.map_query(termC)
        self.assertEqual(termC_mapped.to_statement(), '"heidel\\"berg"') # this means: heidel\"berg

        # Phrase as StringValue without ESHEscaping
        phraseA = esh_client.StringValue(value='heidel*berg',isPhrase=True)
        phraseA_mapped = esh_objects.map_query(phraseA)
        self.assertEqual(phraseA_mapped.to_statement(), '"heidel*berg"')

        termD = esh_client.StringValue(value='heidel*berg', escapePlaceholders=True)
        termD_mapped = esh_objects.map_query(termD)
        self.assertEqual(termD_mapped.to_statement(), 'heidel\\*berg') # this means: heidel\*berg

        termE = esh_client.StringValue(value='heidel*berg')
        termE_mapped = esh_objects.map_query(termE)
        self.assertEqual(termE_mapped.to_statement(), 'heidel*berg')


        # Phrase as StringValue with ESHEscaping
        phraseB = esh_client.StringValue(value='mann*heim',isPhrase=True,escapePlaceholders=True)
        phraseB_mapped = esh_objects.map_query(phraseB)
        self.assertEqual(phraseB_mapped.to_statement(), '"mann\\\\*heim"')

        auth_json = '''
            {
                "type": "AuthInternal",
                "value": {
                            "type": "ComparisonInternal",
                            "property": {
                                "type": "PropertyInternal",
                                "property": ["city"]
                            },
                            "operator": ":",
                            "value": {
                                "type": "StringValueInternal",
                                "value": "Mannheim"
                            }
                        }
            }
        '''
        auth_mapped = esh_objects.AuthInternal.parse_obj(json.loads(auth_json))
        self.assertEqual(auth_mapped.to_statement(), 'AUTH:(city:Mannheim)')
        auth_object_mapped = esh_objects.AuthInternal(
            value=esh_objects.ComparisonInternal(
                property=esh_objects.PropertyInternal(property=["city"]),
                operator=esh_client.ComparisonOperator.Search,
                value=esh_objects.StringValueInternal(value="walldorf")
            )
        )
        self.assertEqual(auth_object_mapped.to_statement(), 'AUTH:(city:walldorf)')
        esh_object_with_auth_json = '''
            {
                "auth": {
                    "type": "AuthInternal",
                    "value": {
                            "type": "ComparisonInternal",
                            "property": {
                                "type": "PropertyInternal",
                                "property": ["city"]
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
        esh_object_with_auth_mapped = esh_objects.EshObjectInternal.parse_obj(json.loads(esh_object_with_auth_json))
        self.assertEqual(esh_object_with_auth_mapped.to_statement(), "/$all?$top=10&$apply=filter(Search.search(query='AUTH:(city:Mannheim)'))")

        filter_json = '''
            {
                "type": "Filter",
                "value": {
                            "type": "Comparison",
                            "property": {
                                "type": "Property",
                                "property": ["city"]
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
        filter_mapped = esh_objects.map_query(filter)
        self.assertEqual(filter_mapped.to_statement(), 'FILTER:(city:Mannheim)')
        filter_object = esh_client.Filter(
            value=esh_client.Comparison(
                property=esh_client.Property(property=["city"]),
                operator=esh_client.ComparisonOperator.Search,
                value=esh_client.StringValue(value="walldorf")
            )
        )
        filter_object_mapped = esh_objects.map_query(filter_object)
        self.assertEqual(filter_object_mapped.to_statement(), 'FILTER:(city:walldorf)')
        esh_object_with_filter_json = '''
            {
                "filter": {
                    "type": "Filter",
                    "value": {
                            "type": "Comparison",
                            "property": {
                                "type": "Property",
                                "property": ["city"]
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
        esh_object_with_filter_mapped = esh_objects.map_query(esh_object_with_filter)
        self.assertEqual(esh_object_with_filter_mapped.to_statement(), "/$all?$top=10&$apply=filter(Search.search(query='FILTER:(city:Mannheim)'))")


        filterwf_json = '''
            {
                "type": "FilterWF",
                "value": {
                            "type": "Comparison",
                            "property": {
                                "type": "Property",
                                "property": ["city"]
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
        filterwf_mapped = esh_objects.map_query(filterwf)
        self.assertEqual(filterwf_mapped.to_statement(), 'FILTERWF:(city:Mannheim)')
        filterwf_object = esh_client.FilterWF(
            value=esh_client.Comparison(
                property=esh_client.Property(property=["city"]),
                operator=esh_client.ComparisonOperator.Search,
                value=esh_client.StringValue(value="walldorf")
            )
        )
        filterwf_object_mapped = esh_objects.map_query(filterwf_object)
        self.assertEqual(filterwf_object_mapped.to_statement(), 'FILTERWF:(city:walldorf)')
        esh_object_with_filterwf_json = '''
            {
                "filter": {
                    "type": "FilterWF",
                    "value": {
                            "type": "Comparison",
                            "property": {
                                "type": "Property",
                                "property": ["city"]
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
        esh_object_with_filterwf_mapped = esh_objects.map_query(esh_object_with_filterwf)
        self.assertEqual(esh_object_with_filterwf_mapped.to_statement(), "/$all?$top=10&$apply=filter(Search.search(query='FILTERWF:(city:Heidelberg)'))")



        boost_json = '''
            {
                "type": "Boost",
                "value": {
                            "type": "Comparison",
                            "property": {
                                "type": "Property",
                                "property": ["city"]
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
        boost_mapped = esh_objects.map_query(boost)
        self.assertEqual(boost_mapped.to_statement(), 'BOOST:(city:Mannheim)')
        boost_object = esh_client.Boost(
            value=esh_client.Comparison(
                property=esh_client.Property(property=["city"]),
                operator=esh_client.ComparisonOperator.Search,
                value=esh_client.StringValue(value="walldorf")
            )
        )
        boost_object_mapped = esh_objects.map_query(boost_object)
        self.assertEqual(boost_object_mapped.to_statement(), 'BOOST:(city:walldorf)')
        esh_object_with_boost_json = '''
            {
                "boost": [
                    {
                        "type": "Boost",
                        "value": {
                                "type": "Comparison",
                                "property": {
                                    "type": "Property",
                                    "property": ["city"]
                                },
                                "operator": ":",
                                "value": {
                                    "type": "StringValue",
                                    "value": "Heidelberg"
                                }
                            }
                    }
                ]
            }
        '''
        esh_object_with_boost = esh_client.EshObject.parse_obj(json.loads(esh_object_with_boost_json))
        esh_object_with_boost_mapped = esh_objects.map_query(esh_object_with_boost)
        self.assertEqual(esh_object_with_boost_mapped.to_statement(), "/$all?$top=10&$apply=filter(Search.search(query='BOOST:(city:Heidelberg)'))" )

        esh_object_with_boost_array_json = '''
            {
                "boost": [
                    {
                        "type": "Boost",
                        "value": {
                                    "type": "Comparison",
                                    "property": {
                                        "type": "Property",
                                        "property": ["language"]
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
                                        "property": ["city"]
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
        esh_object_with_boost_array_mapped = esh_objects.map_query(esh_object_with_boost_array)
        self.assertEqual(esh_object_with_boost_array_mapped.to_statement(), "/$all?$top=10&$apply=filter(Search.search(query='(BOOST:(language:en) BOOST:(city:mannheim))'))")

        fuzzy_search_options = esh_objects.FuzzySearchOptionsInternal()
        fuzzy_search_options.textSearch = esh_client.TextSearch.compare
        fuzzy_search_options.abbreviationSimilarity = 0.9
        self.assertEqual(fuzzy_search_options.to_statement(), "abbreviationSimilarity=0.9,textSearch=compare")

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
        string_value_with_fuzzy_options_mapped = esh_objects.map_query(string_value_with_fuzzy_options)
        self.assertEqual(string_value_with_fuzzy_options_mapped.to_statement(), "frankfurt~0.78[considerNonMatchingTokens=input]")


        termJune = esh_client.StringValue(value='June:')
        termJune_mapped = esh_objects.map_query(termJune)
        self.assertEqual(termJune_mapped.to_statement(), 'June\\:')

        termJune_fuzziness = esh_client.StringValue(value='J?une:', searchOptions=esh_client.SearchOptions(fuzzinessThreshold=0.73))
        termJune_fuzziness_mapped = esh_objects.map_query(termJune_fuzziness)
        self.assertEqual(termJune_fuzziness_mapped.to_statement(), 'J?une\\:~0.73')

        termJune_fuzziness_placeholder = esh_client.StringValue(value='J?une:', escapePlaceholders=True, searchOptions=esh_client.SearchOptions(fuzzinessThreshold=0.73))
        termJune_fuzziness_placeholder_mapped = esh_objects.map_query(termJune_fuzziness_placeholder)
        self.assertEqual(termJune_fuzziness_placeholder_mapped.to_statement(), 'J\\?une\\:~0.73')

        termJune_fuzziness_phrase = esh_client.StringValue(value='J?une:', isPhrase=True, searchOptions=esh_client.SearchOptions(fuzzinessThreshold=0.73))
        termJune_fuzziness_mapped_phrase = esh_objects.map_query(termJune_fuzziness_phrase)
        self.assertEqual(termJune_fuzziness_mapped_phrase.to_statement(), '"J?une\\\\:"~0.73')

        termJune_fuzziness_phrase = esh_client.StringValue(value='J?une:', isPhrase=True, escapePlaceholders=True, searchOptions=esh_client.SearchOptions(fuzzinessThreshold=0.73))
        termJune_fuzziness_mapped_phrase = esh_objects.map_query(termJune_fuzziness_phrase)
        self.assertEqual(termJune_fuzziness_mapped_phrase.to_statement(), '"J\\\\?une\\\\:"~0.73')

        mv = esh_client.MultiValues(items=["firstName", "lastName"])
        co = esh_client.Comparison(
            property= esh_client.MultiValues(items=["firstName", "lastName"],separator=",",encloseStart="(", encloseEnd=")"),
            operator=esh_client.ComparisonOperator.Search,
            value= esh_client.MultiValues(items=["Max", "Mustermann"],encloseStart="(", encloseEnd=")")
        )
        
        
        co_mapped = esh_objects.map_query(co)
        print(co_mapped.to_statement())

        range_value_1 = esh_client.RangeValue(
                            start=esh_client.StringValue(value="fromSomething"),
                            end=esh_client.StringValue(value="toSomething"),
                            excludeStart=True,
                            excludeEnd=True
                        )
        range_value_1_mapped = esh_objects.map_query(range_value_1)
        self.assertEqual(range_value_1_mapped.to_statement(), "]fromSomething toSomething[")

        range_value_2 = esh_client.RangeValue(
                            start=esh_client.StringValue(value="fromSomething"),
                            end=esh_client.StringValue(value="toSomething")
                        )
        range_value_2_mapped = esh_objects.map_query(range_value_2)
        self.assertEqual(range_value_2_mapped.to_statement(), "[fromSomething toSomething]")

        number_value_float = esh_client.NumberValue(value=2.3)
        number_value_float_mapped = esh_objects.map_query(number_value_float)
        self.assertEqual(number_value_float_mapped.to_statement(), "2.3")


        number_value_int = esh_client.NumberValue(value=5)
        number_value_int_mapped = esh_objects.map_query(number_value_int)
        self.assertEqual(number_value_int_mapped.to_statement(), "5.0")

        bool_value_true = esh_client.BooleanValue(value=True)
        bool_value_true_mapped = esh_objects.map_query(bool_value_true)
        self.assertEqual(bool_value_true_mapped.to_statement(), "true")

        bool_value_false = esh_client.BooleanValue(value=False)
        bool_value_false_mapped = esh_objects.map_query(bool_value_false)
        self.assertEqual(bool_value_false_mapped.to_statement(), "false")

        so1 = esh_client.EshObject(
            count=True,
            top=4,
            scope=['Document'],
            searchQueryFilter=esh_client.Expression(
            operator=esh_client.LogicalOperator.AND,
            items=[
                esh_client.Comparison(
                    property=esh_client.Property(property=['createdAt']),
                    operator=esh_client.ComparisonOperator.BetweenCaseInsensitive,
                    value=esh_client.RangeValue(start='2022-10-01', end='2022-10-31')
                )]

        ))
        so1_mapped = esh_objects.map_query(so1)
        print(so1_mapped.to_statement())


        so2 = esh_client.EshObject(
            count=True,
            top=4,
            scope=['Document'],
            searchQueryFilter=esh_client.Expression(
                operator=esh_client.LogicalOperator.AND,
                items=[
                    esh_client.Comparison(
                        property=esh_client.Property(property=['createdAt']),
                        operator=esh_client.ComparisonOperator.BetweenCaseInsensitive,
                        value=esh_client.RangeValue(
                            start=esh_client.DateValue(value='2022-12-01'),
                            end=esh_client.DateValue(value='2022-12-31'))
                    )]
            )
        )
        so2_mapped = esh_objects.map_query(so2)
        print(so2_mapped.to_statement())

        so_polygon = esh_client.Polygon(coordinates=[[[0.0, 0.0], [4.0, 0.0], [2.0, 2.0], [0.0, 0.0]]])
        so_polygon_mapped = esh_objects.map_query(so_polygon)
        self.assertEqual(so_polygon_mapped.to_statement(), "POLYGON((0.0 0.0,4.0 0.0,2.0 2.0,0.0 0.0))")


        so_geo = esh_client.EshObject(
            count=True,
            top=6,
            scope=['Person'],
            searchQueryFilter=esh_client.Expression(
                operator=esh_client.LogicalOperator.AND,
                items=[
                    esh_client.Comparison(
                        property=esh_client.Property(property=['relLocation', 'location', 'position']),
                        operator=esh_client.CoveredByOperator(),
                        value=esh_client.Polygon(coordinates=[
                            [
                                [-0.31173706054687506, 51.618869218965926],
                                [0.10574340820312501, 51.63762391020278],
                                [0.09887695312500001, 51.36920841344186],
                                [-0.28976440429687506, 51.40348936856666],
                                [-0.32135009765625006, 51.5693878622646],
                                [-0.31173706054687506, 51.618869218965926]
                            ]
                        ])
                    )]
            )
        )

        so_geo_mapped = esh_objects.map_query(so_geo)
        # print(so_geo_mapped.to_statement())
        self.assertEqual(so_geo_mapped.to_statement(), "/$all?$top=6&$count=true&$apply=filter(Search.search(query='SCOPE:Person relLocation.location.position:COVERED_BY:POLYGON((-0.31173706054687506 51.618869218965926,0.10574340820312501 51.63762391020278,0.09887695312500001 51.36920841344186,-0.28976440429687506 51.40348936856666,-0.32135009765625006 51.5693878622646,-0.31173706054687506 51.618869218965926))'))")



        print(' -----> everything fine <----- ')    

    ''' 
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
    '''
if __name__ == '__main__':
    unittest.main()