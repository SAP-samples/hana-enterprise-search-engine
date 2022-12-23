import unittest
import json
import db_search

class TestStringMethods(unittest.TestCase):


    mapping_rule_set_definition= '''{
        "entities": {
            "example.Person": {
                "elements": {
                    "firstName": {
                        "column_name": "FIRSTNAME"
                    },
                    "lastName": {
                        "column_name": "LASTNAME"
                    },
                    "address": {
                        "elements": {
                            "name": {
                                "column_name": "ADDRESS_NAME"
                            },
                            "type": {
                                "column_name": "ADDRESS_TYPE"
                            },
                            "sid": {
                                "column_name": "ADDRESS_SID"
                            },
                            "city": {
                                "column_name": "ADDRESS_CITY"
                            }
                        }
                    },
                    "contacts": {
                        "items": {
                            "elements": {
                                "contactname": {
                                    "column_name": "CONTACTNAME"
                                },
                                "contactinfo": {
                                    "elements": {
                                        "group": {
                                            "column_name": "CONTACTINFO_GROUP"
                                        }
                                    }
                                }
                            },
                        "table_name": "ENTITY/EXAMPLEPERSON_CONTACTS"
                        }
                    },
                    "tags": {
                        "items": {
                            "elements": {},
                            "table_name": "ENTITY/DATATYPE_TAGS",
                            "column_name": "_VALUE"
                        }
                    }
                }
            }
            }
        }
    '''


    def test_phrase(self):
        # cv = db_search._get_column_view(json.loads(self.mapping_rule_set_definition), "example.Person", "PLCSCHEMA", ["firstName"])
        # print(cv.column_name_by_path(["firstName"]))
        self.assertEqual("a", "a")
        
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