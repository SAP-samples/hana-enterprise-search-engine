'''
E2E test cases using the REST API
'''
import os
import json
import argparse
import requests
import time
import sys
import logging
from enum import Enum

class FileType(Enum):
    CDS = 1
    DATA = 2
    SEARCH_REQ_ODATA = 3
    SEARCH_REQ_OPENAPI = 4
    CSON = 5
    DB = 6
    DDL = 7
    NODES = 8
    SEARCH_RESP_ODATA_GET = 9
    SEARCH_RESP_ODATA_POST = 10
    SEARCH_RESP_OPENAPI = 11
    SEARCH_RESP_REFERENCE = 12

class OutputType(Enum):
    NONE = None
    ACTUAL = 'actual-output'
    TARGET = 'target-output'

def file_name(test_package, test, file_type:FileType\
    , output_type:OutputType = OutputType.NONE):
    root = os.path.join(current_path,test_package, test)
    if output_type in [OutputType.ACTUAL, OutputType.TARGET]:
        output_folder = output_type.value
    match file_type:
        case FileType.CDS:
            return os.path.join(root, 'model.cds')
        case FileType.DATA:
            return os.path.join(root, 'model.cds')
        case FileType.SEARCH_REQ_ODATA:
            return os.path.join(root, 'searchRequestOData.txt')
        case FileType.SEARCH_REQ_OPENAPI:
            return os.path.join(root, 'searchRequestOpenAPI.json')
        case FileType.CSON:
            return os.path.join(root, output_folder, 'cson.json')
        case FileType.DB:
            return os.path.join(root, output_folder, 'db.json')
        case FileType.DDL:
            return os.path.join(root, output_folder, 'ddl.txt')
        case FileType.NODES:
            return os.path.join(root, output_folder, 'nodes.json')
        case FileType.SEARCH_RESP_ODATA_GET:
            return os.path.join(root, output_folder, 'searchODataGET.json')
        case FileType.SEARCH_RESP_ODATA_POST:
            return os.path.join(root, output_folder, 'searchODataPOST.json')
        case FileType.SEARCH_RESP_OPENAPI:
            return os.path.join(root, output_folder, 'searchOpenAPI.json')
        case FileType.SEARCH_RESP_REFERENCE:
            return os.path.join(root, output_folder, 'search.json')

def round_dict(d, k):
    if k in d:
        d[k] = int(round(d[k], 0))

def round_esh_response(esh_res):
    round_dict(esh_res, '@com.sap.vocabularies.Search.v1.ResponseTime')
    round_dict(esh_res, '@com.sap.vocabularies.Search.v1.SearchTime')
    if '@com.sap.vocabularies.Search.v1.SearchStatistics' in esh_res\
        and 'ConnectorStatistics' in esh_res['@com.sap.vocabularies.Search.v1.SearchStatistics']:
        for c in esh_res['@com.sap.vocabularies.Search.v1.SearchStatistics']['ConnectorStatistics']:
            round_dict(c, '@com.sap.vocabularies.Search.v1.SearchTime')
            round_dict(c, '@com.sap.vocabularies.Search.v1.CPUTime')
    return esh_res


def check_search_response(ref_obj, test_obj, ref_file_name):
    if ref_obj:
        if ref_obj != test_obj:
            return False
    else:
        with open(os.path.join(folder_path, ref_file_name)\
            , encoding = 'utf-8') as fr:
            json.dump(test_obj, fr, indent = 4)
    return True

def check(test_result, package_name:str, test_name:str, file_type:FileType):
    if args.update_target:
        print(
            f'Updating {file_name(package_name, test_name, file_type, OutputType.TARGET)} '
            f'from {file_name(package_name, test_name, file_type, OutputType.ACTUAL)}')
    else:
        print(
            f'Comparing {file_name(package_name, test_name, file_type, OutputType.ACTUAL)} '
            f'with {file_name(package_name, test_name, file_type, OutputType.TARGET)}')

parser = argparse.ArgumentParser(description='Runs test cases for mapper')
parser.add_argument('-p', '--package', nargs='?', help='test package name', type=str)
parser.add_argument('-t', '--test', nargs='?', help='test number', type=str)
parser.add_argument('--cds-compile', metavar='cds_compile'\
    , action=argparse.BooleanOptionalAction, default=True\
    , help='execution includes compiliation from cds to cson')
parser.add_argument('--cleanup'\
    , action=argparse.BooleanOptionalAction, default=True\
    , help='cleanup after test execution')
parser.add_argument('--update-reference', metavar='update_reference'\
    , action=argparse.BooleanOptionalAction, default=False\
    , help='update target reference data')
args = parser.parse_args()

parser.add_argument('--feature', action=argparse.BooleanOptionalAction)

current_path = sys.path[0]
src_path = current_path[:-len('tests')] + 'src'
sys.path.append(src_path)

all_test_packages = {k:[] for k in next(os.walk(current_path))[1]}
for k in all_test_packages.keys():
    all_test_packages[k] = next(os.walk(os.path.join(current_path, k)))[1]

# Check passed arguments
if args.test and not args.package:
    print('Error. Test number provided but no --package')
    exit(-1)
if args.package:
    if args.package in all_test_packages:
        test_packages = {args.package:all_test_packages[args.package]}
    else:
        print(f'Error. Test package {args.package} does not exit')
        exit(-1)
    if args.test:
        if args.test in all_test_packages[args.package]:
            test_packages = {args.package:[args.test]}
        else:
            print(f'Test {args.test} does not exist in package {args.folder}')
            exit(-1)
else:
    test_packages = all_test_packages

with open('src/.config.json', encoding = 'utf-8') as fr:
    config = json.load(fr)
tenant_name = config['deployment']['testTenant']
base_url = f"http://{config['server']['host']}:{config['server']['port']}"

test_result = {'info':[], 'error':[]}

for test_package, tests in test_packages.items():
    for test in tests:
        if not os.path.exists(file_name(test_package, test, FileType.CDS)):
            test_result['error'].append(f'CDS-File missing for {test_package}.{test}')
        if args.cds_compile\
            or not os.path.exists(file_name(test_package, test, FileType.CSON)):
            command_line_statement = (
                f'cds compile {file_name(test_package, test, FileType.CDS)}'
                f' --to json > {file_name(test_package, test, FileType.CSON, OutputType.ACTUAL)}')
            print(command_line_statement)
            print('1')
            os.system(command_line_statement)
            print('2')
            test_result['info'].append(f'{test_package}.{test}: Compiled CDS-File to CSON')
            #check(test_result, test_package, test, FileType.CSON)


for k, v in test_result.items():
    print (k)
    for l in v:
        print(f'\t{l}')



'''
for test_set in test_sets:
    if args.test:
        tests = str(args.test).zfill(2)
    else:
        file_names = set(os.listdir(folder_path))

    # use cds compiler to convert cds files to cson files
    if not args.nocdscompile:
        for file_name in file_names:
            if file_name.endswith('.cds'):
                cds_file_name = file_name
                cson_file_name = cds_file_name[:-4] + '.cson.json'
                full_cds_file_name = os.path.join(folder_path, cds_file_name)
                full_cson_file_name = os.path.join(folder_path, cson_file_name)
                command_line_statement = f'cds compile {full_cds_file_name} --to json > {full_cson_file_name}'
                print(command_line_statement)
                os.system(command_line_statement)

next(os.walk('.'))[1]
'''
'''
    folder_path = os.path.join(current_path, folder)
    if args.test:
        file_names = set([str(args.test).zfill(2) + '.cds'])
    else:
        file_names = set(os.listdir(folder_path))
    # use cds compiler to convert cds files to cson files
    if not args.nocdscompile:
        for file_name in file_names:
            if file_name.endswith('.cds'):
                cds_file_name = file_name
                cson_file_name = cds_file_name[:-4] + '.cson.json'
                full_cds_file_name = os.path.join(folder_path, cds_file_name)
                full_cson_file_name = os.path.join(folder_path, cson_file_name)
                command_line_statement = f'cds compile {full_cds_file_name} --to json > {full_cson_file_name}'
                print(command_line_statement)
                os.system(command_line_statement)

    if args.test:
        cson_file_names = [selected_cson_file_name]
    else:
        cson_file_names = [w for w in os.listdir(folder_path) if w.endswith('.cson.json')]

    try:
        for cson_file_name in cson_file_names:
            test_name = cson_file_name[:-10]
            data_file_name = test_name + '.data.json'
            openapi_search_request_file_name = test_name + '.searchRequestOpenAPI.json'
            openapi_search_response_file_name = test_name + '.searchResponseOpenAPI.json'
            odata_search_request_file_name = test_name + '.searchRequestOData.txt'
            odata_search_response_file_name_post = test_name + '.searchResponseODataPOST.json'
            odata_search_response_file_name_get = test_name + '.searchResponseODataGET.json'
            reference_search_response_file_name = test_name + '.searchResponseReference.json'
            if os.path.exists(os.path.join(folder_path, openapi_search_request_file_name)):
                with open(os.path.join(folder_path, openapi_search_request_file_name), encoding = 'utf-8') as f:
                    openapi_search_request = json.load(f)
            else:
                openapi_search_request = None
            if os.path.exists(os.path.join(folder_path, odata_search_request_file_name)):
                with open(os.path.join(folder_path, odata_search_request_file_name), encoding = 'utf-8') as f:
                    odata_search_request = [w for w in f.read().split('\n') if w.strip() != '']
            else:
                odata_search_request = None
            if os.path.exists(os.path.join(folder_path, data_file_name)):
                with open(os.path.join(folder_path, cson_file_name), encoding = 'utf-8') as f:
                    cson = json.load(f)
                with open(os.path.join(folder_path, data_file_name), encoding = 'utf-8') as f:
                    data = json.load(f)
                res = []
                r = requests.delete(f'{base_url}/v1/tenant/{tenant_name}')
                ts = time.time()
                r = requests.post(f'{base_url}/v1/tenant/{tenant_name}')
                res.append(r.status_code)
                r = requests.post(f'{base_url}/v1/deploy/{tenant_name}', json=cson)
                res.append(r.status_code)

                r = requests.post(f'{base_url}/v1/data/{tenant_name}', json=data)
                res.append(r.status_code)
    
                ref_search_resp_file_name = os.path.join(folder_path, reference_search_response_file_name)
                if os.path.exists(ref_search_resp_file_name):
                    with open(ref_search_resp_file_name, encoding = 'utf-8') as fr:
                        reference_search_response = json.load(fr)
                else:
                    reference_search_response = None
                if openapi_search_request:
                    tstart = time.time()
                    r = requests.post(f'{base_url}/v1/search/{tenant_name}', json=openapi_search_request)
                    #print(time.time() - tstart)
                    res.append(r.status_code)
                    with open(os.path.join(folder_path, openapi_search_response_file_name), 'w',\
                        encoding = 'utf-8') as fw:
                        search_response = [round_esh_response(w) for w in r.json()]
                        json.dump(search_response, fw, indent=4)
                    if not check_search_response(reference_search_response, search_response, ref_search_resp_file_name):
                        res.append('wrong OpenAPI search response')
                if odata_search_request:
                    # GET
                    tstart = time.time()
                    search_response = []
                    for search_request in odata_search_request:
                        r = requests.get(f'{base_url}/sap/es/odata/{tenant_name}/latest/{search_request}')
                        search_response.append(r.json())
                        res.append(r.status_code)
                    #print(time.time() - tstart)
                    with open(os.path.join(folder_path, odata_search_response_file_name_get), 'w',\
                        encoding = 'utf-8') as fw:
                        search_response = [round_esh_response(w) for w in search_response]
                        json.dump(search_response, fw, indent=4)
                    if not check_search_response(reference_search_response, search_response, ref_search_resp_file_name):
                        res.append('wrong OData GET search response')
                    # POST
                    tstart = time.time()
                    r = requests.post(f'{base_url}/sap/es/odata/{tenant_name}/latest'\
                        , json=odata_search_request)
                    #print(time.time() - tstart)
                    res.append(r.status_code)
                    with open(os.path.join(folder_path, odata_search_response_file_name_post), 'w',\
                        encoding = 'utf-8') as fw:
                        search_response = [round_esh_response(w) for w in r.json()]
                        json.dump(search_response, fw, indent=4)
                    if not check_search_response(reference_search_response, search_response, ref_search_resp_file_name):
                        res.append('wrong OData POST search response')
                if not args.nocleanup:
                    r = requests.delete(f'{base_url}/v1/tenant/{tenant_name}')
                    res.append(r.status_code)
                trun = round((time.time() - ts), 1)
                if set(res) == set([200]):
                    print(f'Test {folder}.{test_name} sucessfully executed in {trun} s')
                else:
                    res_str = ', '.join([str(w) for w in res])
                    print(f'Test {folder}.{test_name} failed with (HTTP) codes {res_str} in {trun} s')
    except requests.exceptions.ConnectionError as e:
        logging.error('Connection error. Server might not be running')
'''