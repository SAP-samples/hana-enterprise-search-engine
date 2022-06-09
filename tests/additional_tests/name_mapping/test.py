import sys
import os
import importlib.util
import json
import argparse

current_path = sys.path[0]
src_path = current_path[:-len('tests\\name_mapping')] + 'src'
sys.path.append(src_path)

spec2 = importlib.util.spec_from_file_location("name_mapping", "src/name_mapping.py")
name_mapping = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(name_mapping)

file_names = [w for w in os.listdir(current_path) if w.endswith('.path.json') and w.startswith(str(3).zfill(2))]

for file_name in file_names:
    file_name_result = file_name[:-len('.path.json')] + '.map.json'
    with open(os.path.join(current_path, file_name), encoding = 'utf-8') as f:
        paths  = json.load(f)
        nm = name_mapping.NameMapping()
        test_res = {'res':[]}
        for path in paths:
            test_res['res'].append(nm.register(path))
        with open(os.path.join(current_path, file_name_result), 'w', encoding = 'utf-8') as fw:
            test_res['ext_tree'] = nm.ext_tree
            json.dump(test_res, fw, indent=4)