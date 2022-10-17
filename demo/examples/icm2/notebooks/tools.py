''' common methods and classes for notebooks'''
import json
import os
import sys

class StopExecution(Exception):
    def _render_traceback_(self):
        pass

def print_response(r):
    if 'detail' in r.json():
        if r.status_code == 200:
            status = 'Success'
        else:
            status = 'Error'
        print(f'{status}: {r.json()["detail"]}')
    else:
        print(r.json())

def get_base_url():
    config_file = os.path.join(sys.path[-1], 'shared', '.config.json')
    with open(config_file, encoding='utf-8') as f:
        config = json.load(f)
    return  f"http://{config['server']['host']}:{config['server']['port']}"

def get_root_path():
    return sys.path[0]
