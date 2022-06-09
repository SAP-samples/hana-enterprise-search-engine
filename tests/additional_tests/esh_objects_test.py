'''
import sys
current_path = sys.path[0]
src_path = current_path[:-len('tests\\mapping')] + 'src'
sys.path.append(src_path)
'''
import json
import importlib.util

spec1 = importlib.util.spec_from_file_location("sqlcreate", "src/esh_objects.py")
esh = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(esh)

import esh_objects as esh

'''
json_body={
    'top': 10,
    'count': True,
    'whyfound': True,
    'select': ["id", "name"],
    'estimate': True,
    'wherefound': True,
    'facetlimit': 4,
    'facets': ["city", "land"],
    'filteredgroupby': False,
    'orderby': [
            {
                "key": "city",
                "order": "ASC"
            },
            {
                "key": "language",
                "order": "DESC"
            },
            {
                "key": "land"
            }
        ],
    'searchQueryFilter': {esh.Constants.type: 'Expression', 'items' : [{esh.Constants.type: 'ScopeComparison', 'values': ['S1']},{esh.Constants.type: 'Expression', 'items' :[{'type': 'StringValue', 'value': "nenene"},{'type': 'StringValue', 'value': "dadadad"}], 'operator': 'OR'}, {'type': 'StringValue', 'value': "aaa"},{'type': 'StringValue', 'value': "bbb"}], 'operator': "AND"},
    'odataFilter': {esh.Constants.type: 'Expression', 'items' : [{esh.Constants.type: 'Comparison','property':  {esh.Constants.type:'Property', 'property':"flag"}, 'operator': ' eq ', 'value': { esh.Constants.type: 'StringValue', 'value': 'ACTIVE','is_single_quoted': True}}], 'operator': ""}
    }
    # n1'apply': {esh.Constants.type: 'Expression', 'items' : [{esh.Constants.type: 'ScopeComparison', 'values': ['S1']},{'type': 'StringValue', 'value': "aaa"},{'type': 'StringValue', 'value': "bbb"},{esh.Constants.type: 'Comparison', 'property': {esh.Constants.type:'property', 'property':"pr_language"}, 'operator': ':EQ:', 'value': { esh.Constants.type: 'StringValue', 'value': 'Python'}}], 'operator': "AND"}
    #        'apply': {esh.Constants.type: 'Expression', 'items':[{esh.Constants.type: 'ScopeComparison', 'values': ['S1']},{esh.Constants.type: 'Comparison', 'property': 'type', 'operator': ':EQ:', 'value': { esh.Constants.type: 'StringValue', 'value': 'Python'}},{esh.Constants.type: 'Expression', 'items':[{esh.Constants.type: 'NumberValue', 'value': 34},{esh.Constants.type: 'StringValue', 'value': 'hhhhh'},{esh.Constants.type: 'StringValue', 'value': 'wwwwwww'}], 'operator': "OR"}], 'operator': "AND"}


es_objects = esh.IESSearchOptions(json_body)
print(es_objects.to_statement())
#print(json.dumps(es_objects.searchQueryFilter.to_dict(), indent=4))
print(json.dumps(es_objects.to_dict(), indent=4))
assert(es_objects.to_statement() == "/$all?$top=10&$count=true&$apply=filter(Search.search(query='SCOPE:S1 AND (nenene OR dadadad) AND aaa AND bbb')) and flag eq 'ACTIVE'&whyfound=true&$select=id,name&$orderby=city ASC,language DESC,land&estimate=true&wherefound=true&facetlimit=4&facets=city,land&filteredgroupby=false")

'''

phrase_definition = {'phrase': "heidelberg", Constants.search_options: {Constants.fuzzinessThreshold:0.5,Constants.weight:0.9,Constants.fuzzySearchOptions:"search=typeahead"}}
phrase = Phrase(phrase_definition)
assert(phrase.to_statement() == '"heidelberg"~0.5[search=typeahead]^0.9')

phrase = esh.Phrase({})