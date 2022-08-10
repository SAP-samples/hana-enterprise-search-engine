import json
import sys
import os
import argparse

parser = argparse.ArgumentParser(description='Check consistency between cson and data')
parser.add_argument('-p', '--package', help='test package name', type=str, required=True)
parser.add_argument('-t', '--test', help='test name', type=str, required=True)

args = parser.parse_args()
package = args.package
test = args.test

test_path = os.path.join(sys.path[0], f'..\\packages\\{package}\\{test}')
fn_data = os.path.join(test_path, 'data.json')
fn_cson = os.path.join(test_path, 'output\\cson.json')

with open(fn_data, encoding = 'utf-8') as f:
    data = json.load(f)
with open(fn_cson, encoding = 'utf-8') as f:
    cson = json.load(f)

all_error_messages = set()

def error(s: str):
    if s not in all_error_messages:
        all_error_messages.add(s)
        print(s)

def verify (cson, path, obj, model):
    if 'type' in model and model['type'][:4] != 'cds.':
        if model['type'] in cson['definitions']:
            model = cson['definitions'][model['type']]
        else:
            error('unknown type {} - {}'.format(model['type'], '.'.join(path)))
            return
    if 'items' in model and not isinstance(obj, list):
        error('array expected - {}'.format('.'.join(path)))
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if 'type' in model and model['type'] == 'cds.Association':
                if k == 'source' and model['target'] in cson['definitions'] \
                    and k in cson['definitions'][model['target']]['elements']:
                    verify(cson, path + [k], v, cson['definitions'][model['target']]['elements'][k])
                elif not (model['target'] in cson['definitions'] \
                    and k in cson['definitions'][model['target']]['elements'] \
                    and 'key' in cson['definitions'][model['target']]['elements'][k] \
                    and cson['definitions'][model['target']]['elements'][k]['key']):
                    error('{} is not key of {} in {}'.format(k, model['target'], '.'.join(path + [k])))
            elif k in model['elements']:
                verify(cson, path + [k], v, model['elements'][k])
            else:
                error('unkown - {}'.format('.'.join(path + [k])))
    if isinstance(obj, list):
        if not 'items' in model:
            error('not an array - {}'.format('.'.join(path)))
        else:
            for o in obj:
                verify(cson, path,o, model['items'])

for object_type, object_list in data.items():
    if object_type not in cson['definitions']:
        error(f'unknown entity - {object_type}')
        continue
    if cson['definitions'][object_type]['kind'] != 'entity':
        error(f'not a CDS entity - {object_type}')
        continue
    for obj in object_list:
        if 'id' in obj:
            error(f'id is reserved property - {object_type}')
            del obj['id']
        verify(cson, [object_type], obj, cson['definitions'][object_type])
