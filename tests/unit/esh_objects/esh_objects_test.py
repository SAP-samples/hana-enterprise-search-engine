import unittest
import json

from src import esh_objects as esh


class TestStringMethods(unittest.TestCase):

    
    def test_term(self):
        term = esh.Term(term="Heidelberg")
        self.assertEqual(term.to_statement(), 'Heidelberg')

        term_json = '''
            {
                "type": "Term",
                "term": "Heidelberg"
            }
        '''
        term_dict = json.loads(term_json)
        term2 = esh.Term.parse_obj(term_dict)
        self.assertEqual(term2.dict(exclude_none=True), term_dict)


    def test_phrase(self):
        phrase = esh.Phrase(phrase="Mannheim")
        self.assertEqual(phrase.to_statement(), '"Mannheim"')

        phrase_json = '''
            {
                "type": "Phrase",
                "phrase": "Mannheim"
            }
        '''
        phrase_dict = json.loads(phrase_json)
        phrase2 = esh.Phrase.parse_obj(phrase_dict)
        self.assertEqual(phrase2.dict(exclude_none=True), phrase_dict)

        phrase3_json = '''
            {
                "type": "Phrase",
                "phrase": "Mannheim",
                "doEshEscaping": false
            }
        '''
        phrase3 = esh.Phrase.parse_obj(json.loads(phrase3_json))
        self.assertEqual(phrase3.dict(exclude_none=True), json.loads(phrase3_json))

    def test_expression(self):
        expression_object = esh.Expression(
                operator=esh.LogicalOperator.AND,
                items= [
                    esh.ScopeComparison(values='Person'),
                    esh.Comparison(
                        property= esh.Property(property='lastName'),
                        operator= esh.ComparisonOperator.Search,
                        value= esh.StringValue(value='Doe')),
                    esh.Comparison(
                        property= esh.Property(property='firstName'),
                        operator= esh.ComparisonOperator.Search,
                        value= esh.StringValue(value='Jane'))
                ]
            )
        expression_json = '''
            {
                "type": "Expression",
                "operator": "AND",
                "items": [
                    {
                        "type": "ScopeComparison",
                        "values": "Person"
                    },
                    {
                        "type": "Comparison",
                        "property": {
                            "type": "Property",
                            "property": "lastName"
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
                            "property": "firstName"
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
        expression = esh.Expression.parse_obj(expression_dict)

        self.assertEqual(expression.to_statement(), "SCOPE:Person AND lastName:Doe AND firstName:Jane")
        self.assertEqual(expression_object.dict(exclude_none=True),expression_dict)

    def test_string_value(self):
        so = esh.EshObject(
            count=True,
            top=1,
            searchQueryFilter=esh.Expression(
                operator=esh.LogicalOperator.AND,
                items= [
                    esh.ScopeComparison(values='Person'),
                    esh.Comparison(
                        property= esh.Property(property='firstName'),
                        operator= esh.ComparisonOperator.Search,
                        value= esh.StringValue(
                            value='Jane',
                            searchOptions=esh.SearchOptions(fuzzinessThreshold=0.7)))]))
        print(so.to_statement())
        self.assertEqual(so.to_statement(),"/$all?$top=1&$count=true&$apply=filter(Search.search(query='SCOPE:Person AND firstName:Jane~0.7'))")

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