import unittest
import json
import esh_client
import esh_objects
import request_mapping

class TestRequestMapping(unittest.TestCase):

    def test_request_mapping(self):
        test_query = esh_client.EshObject()
        test_query.top = 23
        test_query.scope = ["Document"]
        test_query.searchQueryFilter = esh_client.Expression(items=[
            esh_client.Comparison(
                property=esh_client.Property(property=["title"]),
                operator=esh_client.ComparisonOperator.Search,
                value=esh_client.StringValue(value="First Document")
            )
        ])
        testEsh = esh_client.EshRequest(query=test_query)

        model_mapping_json = '''
            {
                "tables": {
                    "ENTITY/DOCUMENT": {
                    "external_path": [
                        "Document"
                    ],
                    "level": 0,
                    "annotations": {
                        "@EndUserText.Label": "Document",
                        "@EnterpriseSearchHana.passThroughAllAnnotations": true
                    },
                    "pk": "ID",
                    "columns": {
                        "ID": {
                        "type": "NVARCHAR",
                        "length": 36,
                        "external_path": [
                            "id"
                        ]
                        },
                        "TITLE": {
                        "length": 5000,
                        "type": "NVARCHAR",
                        "annotations": {
                            "@EndUserText.Label": "Title",
                            "@Search.fuzzinessThreshold": 0.85,
                            "@UI.identification.position": 10
                        },
                        "external_path": [
                            "title"
                        ]
                        },
                        "TEXT": {
                        "type": "BLOB",
                        "annotations": {
                            "@EndUserText.Label": "Text",
                            "@UI.multiLineText": true,
                            "@sap.esh.isText": true,
                            "@UI.identification.position": 20,
                            "@EnterpriseSearch.snippets.enabled": true,
                            "@EnterpriseSearch.snippets.maximumLength": 800,
                            "@Semantics.text": true
                        },
                        "external_path": [
                            "text"
                        ]
                        }
                    },
                    "table_name": "ENTITY/DOCUMENT"
                    }
                },
                "entities": {
                    "Document": {
                        "elements": {
                            "id": {
                            "column_name": "ID"
                            },
                            "title": {
                            "column_name": "TITLE"
                            },
                            "text": {
                            "column_name": "TEXT"
                            }
                        },
                    "table_name": "ENTITY/DOCUMENT"
                    }
                }
            }
        '''
        test_model_dict = json.loads(model_mapping_json)
        test_schema_name = "TEST_Schema"

        mapped_rule_set = request_mapping.map_request_to_rule_set(test_schema_name, test_model_dict, testEsh)
        print(json.dumps(mapped_rule_set.dict(exclude_none=True), indent=2))

        search_rule_set_query= esh_objects.generate_search_rule_set_query(mapped_rule_set)
        print(esh_objects.convert_search_rule_set_query_to_string(search_rule_set_query))

        test_json = '''{
            "parameters": [
                {
                "name": {
                    "type": "Property",
                    "property": ["title"]
                },
                "value": {
                        "type": "StringValue",
                        "value": "Document"
                    }
                }
            ],
            "query": {
                "top": 10,
                "skip": 0,
                "scope": [
                    "Document"
                ],
                "select": [
                {
                    "type": "Property",
                    "property": ["title"]
                }
                ]
            },
            "rules": [
                {
                "name": "myRule1",
                "columns": [
                    {
                    "name": {
                    "type": "Property",
                    "property": ["title"]
                },
                    "minFuzziness": 0.71,
                    "ifMissingAction": "skipRule"
                    }
                ]
                },
                {
                "name": "myRule2",
                "columns": [
                    {
                    "name": {
                    "type": "Property",
                    "property": ["text"]
                },
                    "minFuzziness": 0.84,
                    "ifMissingAction": "skipRule"
                    }
                ]
                }
            ]
        }'''

        test_esh_request = esh_client.EshRequest.parse_obj(json.loads(test_json))
        
        test_mapping_rule_set = request_mapping.map_request_to_rule_set(test_schema_name, test_model_dict, test_esh_request)
        test_search_rule_set_query = esh_objects.generate_search_rule_set_query(test_mapping_rule_set)
        test_search_rule_set_query_string = esh_objects.convert_search_rule_set_query_to_string(test_search_rule_set_query)

        print(test_search_rule_set_query_string)


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
        self.assertEqual(request_mapping.get_view_column_name(["address", "name"]), "ADDRESS_NAME")
        self.assertEqual(request_mapping.get_view_column_name(["contacts", "contactname"]), "CONTACTS_CONTACTNAME")
        self.assertEqual(request_mapping.get_view_column_name(["contacts", "contactinfo", "group"]), "CONTACTS_CONTACTINFO_GROUP")
        self.assertEqual(request_mapping.get_view_column_name(["tags"]), "TAGS")

        self.assertEqual(request_mapping.get_view_column_name_ex(json.loads(mapping_rule_set_definition), "example.Person", ["firstName"]), "FIRSTNAME")
        self.assertEqual(request_mapping.get_view_column_name_ex(json.loads(mapping_rule_set_definition), "example.Person", ["address","city"]), "ADDRESS_CITY")

if __name__ == '__main__':
    unittest.main()