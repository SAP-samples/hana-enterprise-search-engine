'''
E2E test cases using the REST API
'''
import os
import json
import argparse
import requests
import sys
from enum import Enum
from copy import deepcopy
class TestType(Enum):
    '''File types used in test'''
    FOLDER_ONLY = 'folder'
    CDS = 'model.cds'
    CSON = 'cson.json'
    DATA = 'data.json'
    SEARCH_REQ_ODATA = 'searchRequestOData.json'
    SEARCH_REQ_OPENAPI = 'searchRequestOpenAPI.json'
    SEARCH_RESP_ODATA_GET = 'ODataGET'
    SEARCH_RESP_ODATA_POST = 'ODataPOST'
    SEARCH_RESP_OPENAPI = 'OpenAPI'
    GET_ALL_TENANTS = 'serviceResponseGetAllTenants.json'
    DELETE_TENANT = 'serviceResponseDeleteTenant.json'
    CREATE_TENANT = 'serviceResponseCreateTenant.json'
    CREATE_MODEL = 'serviceResponseCreateModel.json'
    LOAD_DATA = 'serviceResponseLoadData.json'
    READ_DATA = 'serviceResponseReadData.json'
    DELETE_DATA = 'serviceResponseDeleteData.json'
    NONE = ''



class FileLocation(Enum):
    OUTPUT = 'output'
    REFERENCE = 'reference'

class MessageType(Enum):
    SUCCESS = 'success'
    INFO = 'info'
    TODO = 'todo'
    ERROR = 'error'

def file_name(package_name, test_name, typ:TestType, location:FileLocation = None):
    root = os.path.join(folder_to_use,package_name, test_name)

    if typ == TestType.FOLDER_ONLY:
        res = os.path.join(root, location.value)
    elif typ in (TestType.CDS, TestType.DATA, TestType.SEARCH_REQ_ODATA, TestType.SEARCH_REQ_OPENAPI):
        res = os.path.join(root,  typ.value)
    elif typ in (TestType.SEARCH_RESP_ODATA_GET, TestType.SEARCH_RESP_ODATA_POST, TestType.SEARCH_RESP_OPENAPI):
        if location == FileLocation.OUTPUT:
            res = os.path.join(root, location.value, f'search{typ.value}.json')
        elif FileLocation.REFERENCE:
            res = os.path.join(root, location.value, 'search.json')
    else:
        res = os.path.join(root, location.value, typ.value)
    return res

def round_dict(d, key):
    if key in d:
        d[key] = int(round(d[key], 0))

def round_esh_response(esh_res):
    round_dict(esh_res, '@com.sap.vocabularies.Search.v1.ResponseTime')
    round_dict(esh_res, '@com.sap.vocabularies.Search.v1.SearchTime')
    if '@com.sap.vocabularies.Search.v1.SearchStatistics' in esh_res\
        and 'ConnectorStatistics' in esh_res['@com.sap.vocabularies.Search.v1.SearchStatistics']:
        for c in esh_res['@com.sap.vocabularies.Search.v1.SearchStatistics']['ConnectorStatistics']:
            round_dict(c, '@com.sap.vocabularies.Search.v1.SearchTime')
            round_dict(c, '@com.sap.vocabularies.Search.v1.CPUTime')
    return esh_res

def add_message(package_name:str, test_name:str, m_type:MessageType, file_type:TestType|TestType, text = None):
    full_test_name = f'{package_name}.{test_name}'
    if not full_test_name in test_result[m_type]:
        test_result[m_type][full_test_name] = []
    if text:
        msg = f'{file_type.value}: {text}'
    else:
        msg = f'{file_type.value}'
    test_result[m_type][full_test_name].append(msg)

def check(package_name:str, test_name:str, file_type:TestType|TestType):
    fn_ref = file_name(package_name, test_name, file_type, FileLocation.REFERENCE)
    fn_out = file_name(package_name, test_name, file_type, FileLocation.OUTPUT)
    with open(fn_out, encoding = 'utf-8') as f_out:
        out = f_out.read()
    fn_ref_exists = os.path.exists(fn_ref)
    if fn_ref_exists:
        with open(fn_ref, encoding = 'utf-8') as f_ref:
            ref = f_ref.read()
        if ref == out:
            add_message(package_name, test_name\
                , MessageType.SUCCESS, file_type, 'response and reference are identical')
            return
        else:
            if not args.update_reference:
                add_message(package_name, test_name\
                    , MessageType.ERROR, file_type, 'response and reference are NOT identical')
                return
    with open(fn_ref, 'w', encoding = 'utf-8') as f_ref:
        with open(fn_out, encoding = 'utf-8') as f_out:
            f_ref.write(f_out.read())
            if fn_ref_exists:
                add_message(package_name, test_name, MessageType.INFO, file_type, 'reference updated')
            else:
                add_message(package_name, test_name, MessageType.INFO, file_type, 'reference created')

def process_search_result(package_name, test_name, file_type, response_obj):
    result_obj = [round_esh_response(w) for w in response_obj]
    mask_uuid(result_obj, 'ID')
    result_fn = file_name(package_name, test_name, file_type\
        , FileLocation.OUTPUT)
    with open(result_fn, 'w', encoding='utf-8') as fw_res:
        json.dump(result_obj, fw_res, indent=4)
    check(package_name, test_name, file_type)

def mask_uuid(obj, key_name):
    if isinstance(obj, list):
        for o in obj:
            mask_uuid(o, key_name)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict) or isinstance(v, list):
                mask_uuid(v, key_name)
            elif k == key_name and len(v) == 36:
                obj[k] = "".join([ '*'\
                     if c.isalnum() else c for c in obj[k] ])

def process_service_response(package_name, test_name, requst_type: TestType, response):
    result = {'statusCode': response.status_code}
    r = response.json()
    if requst_type in (TestType.LOAD_DATA, TestType.READ_DATA):
        for obj_typ, obj_list in r.items():
            for obj in obj_list:
                mask_uuid(obj, 'id')
    result['body'] = r
    fn = file_name(package_name, test_name, requst_type, FileLocation.OUTPUT)
    with open(fn, 'w', encoding='utf-8') as fw:
        json.dump(result, fw, indent=4)
    check(package_name, test_name, requst_type)


current_path = sys.path[0]
src_path = current_path + '\\..\\..\\src'

parser = argparse.ArgumentParser(description='Runs test cases for mapper')
parser.add_argument('-f', '--folder', nargs='?', help='test package folder', type=str)
parser.add_argument('-p', '--package', nargs='?', help='test package name', type=str)
parser.add_argument('-t', '--test', nargs='?', help='test name', type=str)
parser.add_argument('--cds-compile', metavar='cds_compile'\
    , action=argparse.BooleanOptionalAction, default=True\
    , help='compiliation from cds to cson included')
parser.add_argument('--cleanup'\
    , action=argparse.BooleanOptionalAction, default=True\
    , help='delete test tenanat after test execution')
parser.add_argument('--update-reference', metavar='update_reference'\
    , action=argparse.BooleanOptionalAction, default=False\
    , help='update test reference data')
parser.add_argument('--service-tests', metavar='service_tests'\
    , action=argparse.BooleanOptionalAction, default=False\
    , help='runs HTTP-REST service tests')


args = parser.parse_args()

if args.folder:
    folder_to_use = args.folder
else:
    folder_to_use = current_path + '\\..\\packages'

all_packages = {k:[] for k in next(os.walk(folder_to_use))[1]}
for k in all_packages.keys():
    all_packages[k] = next(os.walk(os.path.join(folder_to_use, k)))[1]

# Check passed arguments
if args.test and not args.package:
    print('Error. Test number provided but no --package')
    exit(-1)
if args.package:
    if args.package in all_packages:
        packages = {args.package:all_packages[args.package]}
    else:
        print(f'Error. Test package {args.package} does not exist')
        exit(-1)
    if args.test:
        if args.test in all_packages[args.package]:
            packages = {args.package:[args.test]}
        else:
            print(f'Test {args.test} does not exist in package {args.package}')
            exit(-1)
else:
    packages = all_packages


with open(os.path.join(src_path, '.config.json'), encoding = 'utf-8') as fr:
    config = json.load(fr)
tenant_name = config['deployment']['testTenant']
base_url = f"http://{config['server']['host']}:{config['server']['port']}"

test_result = {}
for msg_typ in MessageType:
    test_result[msg_typ] = {}

for package, tests in packages.items():
    for test in tests:
        print(f'Test {package}.{test} started')
        if not os.path.exists(file_name(package, test, TestType.CDS)):
            add_message(package, test, MessageType.ERROR, TestType.CDS, 'missing')
            continue
        if not os.path.exists(file_name(package, test, TestType.FOLDER_ONLY, FileLocation.OUTPUT)):
            os.mkdir(file_name(package, test, TestType.FOLDER_ONLY, FileLocation.OUTPUT))
            add_message(package, test, MessageType.INFO, TestType.FOLDER_ONLY, 'output folder created')
        if not os.path.exists(file_name(package, test, TestType.FOLDER_ONLY, FileLocation.REFERENCE)):
            os.mkdir(file_name(package, test, TestType.FOLDER_ONLY, FileLocation.REFERENCE))
            add_message(package, test, MessageType.INFO, TestType.FOLDER_ONLY, 'reference folder created')
        if args.cds_compile\
            or not os.path.exists(file_name(package, test, TestType.CSON, FileLocation.OUTPUT)):
            command_line_statement = (
                f'cds compile {file_name(package, test, TestType.CDS)}'
                f' --to json > {file_name(package, test, TestType.CSON, FileLocation.OUTPUT)}')
            print(command_line_statement)
            os.system(command_line_statement)
            cson_file_name = file_name(package, test, TestType.CSON, FileLocation.OUTPUT)
            with open(cson_file_name, encoding = 'utf-8') as fr:
                cson = json.load(fr)
            del cson['meta']
            with open(cson_file_name, 'w', encoding = 'utf-8') as fw:
                json.dump(cson, fw, indent = 4)
            add_message(package, test, MessageType.INFO, TestType.CDS, 'compiled')
        check(package, test, TestType.CSON)
        with open(file_name(package, test, TestType.CSON, FileLocation.OUTPUT), encoding='utf-8') as f:
            cson = json.load(f)
        data_exist = os.path.exists(file_name(package, test, TestType.DATA))
        if data_exist:
            with open(file_name(package, test, TestType.DATA), encoding='utf-8') as f:
                data = json.load(f)
        else:
            add_message(package, test, MessageType.TODO, TestType.DATA, 'missing')
        if args.service_tests:
            r = requests.get(f'{base_url}/v1/tenant')
            process_service_response(package, test, TestType.GET_ALL_TENANTS, r)
            if [w for w in r.json() if w['name'] == tenant_name]:
                r = requests.delete(f'{base_url}/v1/tenant/{tenant_name}')
                process_service_response(package, test, TestType.DELETE_TENANT, r)
            r = requests.post(f'{base_url}/v1/tenant/{tenant_name}')
            process_service_response(package, test, TestType.CREATE_TENANT, r)
            r = requests.post(f'{base_url}/v1/deploy/{tenant_name}', json=cson)
            process_service_response(package, test, TestType.CREATE_MODEL, r)
            object_ids = None
            if data_exist:
                with open(file_name(package, test, TestType.DATA), encoding='utf-8') as f:
                    data = json.load(f)
                r = requests.post(f'{base_url}/v1/data/{tenant_name}', json=data)
                process_service_response(package, test, TestType.LOAD_DATA, r)
                if r.status_code == 200:
                    ids = r.json()
                    if ids:
                        object_ids = deepcopy(ids)
                        r = requests.post(f'{base_url}/v1/read/{tenant_name}', json= ids)
                        process_service_response(package, test, TestType.READ_DATA, r)
            # OpenAPI
            query_fn = file_name(package, test, TestType.SEARCH_REQ_OPENAPI)
            if os.path.exists(query_fn):
                with open(query_fn, encoding = 'utf-8') as f:
                    query_obj = json.load(f)
                url = f'{base_url}/v2/search/{tenant_name}/latest'
                r = requests.post(url, json=query_obj)
                process_search_result(package, test\
                    , TestType.SEARCH_RESP_OPENAPI, r.json())
            else:
                add_message(package, test, MessageType.TODO\
                    , TestType.SEARCH_REQ_OPENAPI, 'does not exist')
            # OData
            query_fn = file_name(package, test, TestType.SEARCH_REQ_ODATA)
            if os.path.exists(query_fn):
                with open(query_fn, encoding = 'utf-8') as f:
                    query_obj = json.load(f)
                # POST
                url = f'{base_url}/v1/search/{tenant_name}/latest'
                r = requests.post(url, json=query_obj)
                process_search_result(package, test, TestType.SEARCH_RESP_ODATA_POST, r.json())
                # GET
                res_obj = []
                for query_item in query_obj:
                    r = requests.get(f'{base_url}/v1/search/{tenant_name}/latest/{query_item}')
                    res_obj.append(r.json())
                process_search_result(package, test, TestType.SEARCH_RESP_ODATA_GET, res_obj)
            else:
                add_message(package, test, MessageType.TODO\
                    , TestType.SEARCH_REQ_ODATA, 'does not exist')
            if object_ids:
                r = requests.delete(f'{base_url}/v1/data/{tenant_name}', json= object_ids)
                process_service_response(package, test, TestType.DELETE_DATA, r)

        print(f'Test {package}.{test} finished')
        if args.service_tests and args.cleanup:
            r = requests.delete(f'{base_url}/v1/tenant/{tenant_name}')
            process_service_response(package, test, TestType.DELETE_TENANT, r)
        elif data_exist:
            with open(file_name(package, test, TestType.DATA), encoding='utf-8') as f:
                data = json.load(f)
            r = requests.post(f'{base_url}/v1/data/{tenant_name}', json=data)


for msg_type, v1 in test_result.items():
    if len(v1) != 0:
        print (f'Detailed results of type "{msg_type.value}":')
    for full_name, messages in v1.items():
        if messages:
            print(f'\t{full_name}')
        for message in messages:
            print(f'\t\t{message}')

if len(test_result[MessageType.ERROR].items()) == 0:
    print('SUCCESS: All tests successfully finished')
else:
    print('ERROR: Errors found')
