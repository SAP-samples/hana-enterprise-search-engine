'''
E2E test cases using the REST API
'''
import os
import json
import argparse
import requests
import sys
from enum import Enum
import importlib

class TestPK:
    ''' Primary key generator for test to get reproducible key values'''
    next_id = {}
    @classmethod
    def get_pk(cls, table_name, subtable_level):
        if not table_name in cls.next_id:
            cls.next_id[table_name] = 0
        res = f'ID:{table_name}:{str(cls.next_id[table_name])}'
        cls.next_id[table_name] += 1
        return res
    @classmethod
    def reset(cls):
        cls.next_id = {}
    @staticmethod
    def get_definition(subtable_level):
        return ('_ID', {'type':'VARCHAR', 'length': 36})

class FileType(Enum):
    '''File types used in test'''
    CDS = 'cds'
    DATA = 'data'
    SEARCH_REQ_ODATA = 'OData search request'
    SEARCH_REQ_OPENAPI = 'OpenAPI search request'
    CSON = 'cson'
    DB = 'db'
    DDL = 'ddl'
    NODES = 'nodes'
    SEARCH_RESP_ODATA_GET = 'OData GET search response'
    SEARCH_RESP_ODATA_POST = 'OData POST search response'
    SEARCH_RESP_OPENAPI = 'OpenAPI search response'
    NONE = ''

class RequestType(Enum):
    GET_ALL_TENANTS = 'get all tenants'
    DELETE_TENANT = 'delete tenant'
    CREATE_TENANT = 'create tenant'
    CREATE_MODEL = 'create model'
    LOAD_DATA = 'load data'

class FileLocation(Enum):
    OUTPUT = 'output'
    REFERENCE = 'reference'

class MessageType(Enum):
    SUCCESS = 'success'
    INFO = 'info'
    TODO = 'todo'
    ERROR = 'error'

def file_name(package_name, test_name, file_type:FileType\
    , location:FileLocation = None):
    root = os.path.join(current_path,package_name, test_name)
    match file_type:
        case FileType.CDS:
            return os.path.join(root, 'model.cds')
        case FileType.DATA:
            return os.path.join(root, 'data.json')
        case FileType.SEARCH_REQ_ODATA:
            return os.path.join(root, 'searchRequestOData.json')
        case FileType.SEARCH_REQ_OPENAPI:
            return os.path.join(root, 'searchRequestOpenAPI.json')
        case FileType.CSON:
            return os.path.join(root, location.value, 'cson.json')
        case FileType.DB:
            return os.path.join(root, location.value, 'db.json')
        case FileType.DDL:
            return os.path.join(root, location.value, 'ddl.txt')
        case FileType.NODES:
            return os.path.join(root, location.value, 'nodes.json')
        case FileType.SEARCH_RESP_ODATA_GET:
            if location == FileLocation.OUTPUT:
                return os.path.join(root, location.value, 'searchODataGET.json')
            elif FileLocation.REFERENCE:
                return os.path.join(root, location.value, 'search.json')
        case FileType.SEARCH_RESP_ODATA_POST:
            if location == FileLocation.OUTPUT:
                return os.path.join(root, location.value, 'searchODataPOST.json')
            elif FileLocation.REFERENCE:
                return os.path.join(root, location.value, 'search.json')
        case FileType.SEARCH_RESP_OPENAPI:
            if location == FileLocation.OUTPUT:
                return os.path.join(root, location.value, 'searchOpenAPI.json')
            elif FileLocation.REFERENCE:
                return os.path.join(root, location.value, 'search.json')


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

def add_message(package_name:str, test_name:str, m_type:MessageType, file_type:FileType|RequestType, text = None):
    full_test_name = f'{package_name}.{test_name}'
    if not full_test_name in test_result[m_type]:
        test_result[m_type][full_test_name] = []
    if text:
        msg = f'{file_type.value}: {text}'
    else:
        msg = f'{file_type.value}'
    test_result[m_type][full_test_name].append(msg)

def check_response_status_code(response, request_type:RequestType):
    if response.status_code == 200:
        add_message(package, test, MessageType.SUCCESS, request_type\
            , 'request returned with HTTP status code 200')
    else:
        add_message(package, test, MessageType.ERROR, request_type\
            , f'request returned with HTTP status code {response.status_code}')

def check(package_name:str, test_name:str, file_type:FileType):
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
    result_fn = file_name(package_name, test_name, file_type\
        , FileLocation.OUTPUT)
    with open(result_fn, 'w', encoding='utf-8') as fw_res:
        json.dump(result_obj, fw_res, indent=4)
    check(package_name, test_name, file_type)


current_path = sys.path[0]
src_path = current_path[:-len('tests\\packages')] + 'src'
sys.path.append(src_path)

spec1 = importlib.util.spec_from_file_location('sqlcreate', 'src/sqlcreate.py')
sqlcreate = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(sqlcreate)

spec2 = importlib.util.spec_from_file_location('mapping', 'src/mapping.py')
mapping = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(mapping)

parser = argparse.ArgumentParser(description='Runs test cases for mapper')
parser.add_argument('-p', '--package', nargs='?', help='test package name', type=str)
parser.add_argument('-t', '--test', nargs='?', help='test number', type=str)
parser.add_argument('--cds-compile', metavar='cds_compile'\
    , action=argparse.BooleanOptionalAction, default=True\
    , help='compiliation from cds to cson included')
parser.add_argument('--cleanup'\
    , action=argparse.BooleanOptionalAction, default=True\
    , help='delete test tenanat after test execution')
parser.add_argument('--update-reference', metavar='update_reference'\
    , action=argparse.BooleanOptionalAction, default=False\
    , help='update test reference data')
parser.add_argument('--unit-tests', metavar='unit_tests'\
    , action=argparse.BooleanOptionalAction, default=True\
    , help='runs unit tests')
parser.add_argument('--service-tests', metavar='service_tests'\
    , action=argparse.BooleanOptionalAction, default=True\
    , help='runs HTTP-REST service tests')
args = parser.parse_args()

parser.add_argument('--feature', action=argparse.BooleanOptionalAction)

current_path = sys.path[0]
src_path = current_path[:-len('tests')] + 'src'
sys.path.append(src_path)

all_packages = {k:[] for k in next(os.walk(current_path))[1]}
for k in all_packages.keys():
    all_packages[k] = next(os.walk(os.path.join(current_path, k)))[1]

# Check passed arguments
if args.test and not args.package:
    print('Error. Test number provided but no --package')
    exit(-1)
if args.package:
    if args.package in all_packages:
        packages = {args.package:all_packages[args.package]}
    else:
        print(f'Error. Test package {args.package} does not exit')
        exit(-1)
    if args.test:
        if args.test in all_packages[args.package]:
            packages = {args.package:[args.test]}
        else:
            print(f'Test {args.test} does not exist in package {args.package}')
            exit(-1)
else:
    packages = all_packages

with open('src/.config.json', encoding = 'utf-8') as fr:
    config = json.load(fr)
tenant_name = config['deployment']['testTenant']
base_url = f"http://{config['server']['host']}:{config['server']['port']}"

test_result = {}
for msg_typ in MessageType:
    test_result[msg_typ] = {}

for package, tests in packages.items():
    for test in tests:
        print(f'Test {package}.{test} started')
        if not os.path.exists(file_name(package, test, FileType.CDS)):
            add_message(package, test, MessageType.ERROR, FileType.CDS, 'missing')
            continue
        if args.cds_compile\
            or not os.path.exists(file_name(package, test, FileType.CSON, FileLocation.OUTPUT)):
            command_line_statement = (
                f'cds compile {file_name(package, test, FileType.CDS)}'
                f' --to json > {file_name(package, test, FileType.CSON, FileLocation.OUTPUT)}')
            print(command_line_statement)
            os.system(command_line_statement)
            add_message(package, test, MessageType.INFO, FileType.CDS, 'compiled')
        check(package, test, FileType.CSON)
        with open(file_name(package, test, FileType.CSON, FileLocation.OUTPUT), encoding='utf-8') as f:
            cson = json.load(f)
        if args.unit_tests:
            nodes = mapping.cson_to_nodes(cson, TestPK)
            fn = file_name(package, test, FileType.NODES, FileLocation.OUTPUT)
            with open(fn, 'w', encoding='utf-8') as fw:
                json.dump(nodes, fw, indent=4)
            check(package, test, FileType.NODES)
            ddl = sqlcreate.nodes_to_ddl(nodes, 'TEST')
            sql = ';\n\n'.join(ddl['tables'] + ddl['views'] + [json.dumps(w, indent=4) for w in ddl['eshConfig']])
            fn = file_name(package, test, FileType.DDL, FileLocation.OUTPUT)
            with open(fn, 'w', encoding='utf-8') as fw:
                fw.write(sql)
            check(package, test, FileType.DDL)
        if not os.path.exists(file_name(package, test, FileType.DATA)):
            add_message(package, test, MessageType.TODO, FileType.DATA, 'missing')
            continue
        with open(file_name(package, test, FileType.DATA), encoding='utf-8') as f:
            data = json.load(f)
        if args.unit_tests:
            fn = file_name(package, test, FileType.DB, FileLocation.OUTPUT)
            PK = TestPK
            PK.reset()
            db = mapping.objects_to_dml(nodes, data, PK)
            with open(fn, 'w', encoding='utf-8') as fw:
                json.dump(db, fw, indent=4)
            check(package, test, FileType.DB)
        if args.service_tests:
            r = requests.get(f'{base_url}/v1/tenant')
            check_response_status_code(r, RequestType.GET_ALL_TENANTS)
            if [w for w in r.json() if w['name'] == tenant_name]:
                r = requests.delete(f'{base_url}/v1/tenant/{tenant_name}')
                check_response_status_code(r, RequestType.DELETE_TENANT)
            r = requests.post(f'{base_url}/v1/tenant/{tenant_name}')
            check_response_status_code(r, RequestType.CREATE_TENANT)
            r = requests.post(f'{base_url}/v1/deploy/{tenant_name}', json=cson)
            check_response_status_code(r, RequestType.CREATE_MODEL)
            r = requests.post(f'{base_url}/v1/data/{tenant_name}', json=data)
            check_response_status_code(r, RequestType.LOAD_DATA)
            # OpenAPI
            query_fn = file_name(package, test, FileType.SEARCH_REQ_OPENAPI)
            if os.path.exists(query_fn):
                with open(query_fn, encoding = 'utf-8') as f:
                    query_obj = json.load(f)
                url = f'{base_url}/v1/search/{tenant_name}'
                r = requests.post(url, json=query_obj)
                check_response_status_code(r, FileType.SEARCH_RESP_OPENAPI)
                process_search_result(package, test\
                    , FileType.SEARCH_RESP_OPENAPI, r.json())
            else:
                add_message(package, test, MessageType.TODO\
                    , FileType.SEARCH_REQ_OPENAPI, 'does not exit')
            # OData
            query_fn = file_name(package, test, FileType.SEARCH_REQ_ODATA)
            if os.path.exists(query_fn):
                with open(query_fn, encoding = 'utf-8') as f:
                    query_obj = json.load(f)
                # POST
                url = f'{base_url}/sap/es/odata/{tenant_name}/latest'
                r = requests.post(url, json=query_obj)
                check_response_status_code(r, FileType.SEARCH_RESP_ODATA_POST)
                process_search_result(package, test, FileType.SEARCH_RESP_ODATA_POST, r.json())
                # GET
                res_obj = []
                for query_item in query_obj:
                    r = requests.get(f'{base_url}/sap/es/odata/{tenant_name}/latest/{query_item}')
                    res_obj.append(r.json())
                    check_response_status_code(r, FileType.SEARCH_RESP_ODATA_GET)
                process_search_result(package, test, FileType.SEARCH_RESP_ODATA_GET, res_obj)
            else:
                add_message(package, test, MessageType.TODO\
                    , FileType.SEARCH_REQ_ODATA, 'does not exit')
        print(f'Test {package}.{test} finished')
        if args.service_tests and args.cleanup:
            r = requests.delete(f'{base_url}/v1/tenant/{tenant_name}')
            check_response_status_code(r, RequestType.DELETE_TENANT)

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
