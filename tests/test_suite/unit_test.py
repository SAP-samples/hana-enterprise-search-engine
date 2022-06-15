'''
Generates tables using mapping.py
'''

import sys
import os
import importlib.util
import json
import argparse

current_path = sys.path[0]
src_path = current_path[:-len('tests\\test_cases')] + 'src'
sys.path.append(src_path)

#PATH = 'tests\\mapping'


spec1 = importlib.util.spec_from_file_location('sqlcreate', 'src/sqlcreate.py')
sqlcreate = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(sqlcreate)

spec2 = importlib.util.spec_from_file_location('mapping', 'src/mapping.py')
mapping = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(mapping)

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

parser = argparse.ArgumentParser(description='Runs test cases for mapper')
parser.add_argument('-f', '--folder', nargs='?', help='folder name')
parser.add_argument('-t', '--test', nargs='?', help='test number')
parser.add_argument('--nocdscompile', help='no cds compiliation', action='store_true')

args = parser.parse_args()

folders = next(os.walk(current_path))[1]

# Check passed arguments
if args.test and not args.folder:
    print('Error. Test number provided but no --folder')
    exit(-1)
if args.folder:
    if args.folder in folders:
        folders = [args.folder]
    else:
        print(f'Error. Folder {args.folder} does not exit')
        exit(-1)
    if args.test:
        selected_cds_file_name = str(args.test).zfill(2) + '.cds'
        selected_cson_file_name = str(args.test).zfill(2) + '.cson.json'
        if not os.path.exists(os.path.join(current_path, args.folder, selected_cds_file_name)):
            print(f'Test number {args.test} does not exist in folder {args.folder}')
            exit(-1)
        if args.nocdscompile:
            if not os.path.exists(os.path.join(current_path, args.folder, selected_cson_file_name)):
                print(f'CSON file does not exist for test number {args.test} does not exist in folder {args.folder}')
                exit(-1)


for folder in folders:
    #if folder != 'basics':
    #    continue
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

    for cson_file_name in cson_file_names:
        #if cson_file_name != '03.cson.json':
        #    continue
        test_name = cson_file_name[:-9]
        nodes_file_name = test_name + 'nodes.json'
        data_file_name = test_name + 'data.json'
        ddl_file_name = test_name + 'ddl.txt'
        db_file_name = test_name + 'db.json'
        with open(os.path.join(folder_path, cson_file_name), encoding = 'utf-8') as f:
            nodes = mapping.cson_to_nodes(json.load(f), TestPK)
            with open(os.path.join(folder_path, nodes_file_name), 'w', encoding = 'utf-8') as fw:
                json.dump(nodes, fw, indent=4)
                print(f'{folder}.{nodes_file_name} - created')
            with open(os.path.join(folder_path, ddl_file_name), 'w', encoding = 'utf-8') as fw:
                ddl = sqlcreate.nodes_to_ddl(nodes, 'TEST')
                sql = ';\n\n'.join(ddl['tables'] + ddl['views'] + [json.dumps(w, indent=4) for w in ddl['eshConfig']])
                fw.write(sql)
                print(f'{folder}.{ddl_file_name} - created')
            full_data_file_name = os.path.join(folder_path, data_file_name)
            if os.path.exists(full_data_file_name):
                PK = TestPK
                PK.reset()
                with open(full_data_file_name, encoding = 'utf-8') as f:
                    db = mapping.objects_to_dml(nodes, json.load(f), PK)
                    with open(os.path.join(folder_path, db_file_name), 'w', encoding = 'utf-8') as fw:
                        json.dump(db, fw, indent=4)
                        print(f'{folder}.{db_file_name} - created')
            else:
                print(f'ERROR: {folder}.{data_file_name} - MISSING')
