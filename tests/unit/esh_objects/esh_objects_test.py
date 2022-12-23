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
        assert so_mapped.to_statement() == "/$all?$top=10&$count=true&$apply=filter(Search.search(query='SCOPE:Person ((lastName:Doe AND firstName:John) OR (lastName:Doe AND firstName:Jane))'))"
        

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