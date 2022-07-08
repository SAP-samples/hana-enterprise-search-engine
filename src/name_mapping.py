"""Mapping between external arbitrary names and internel names with restricted length and ODATA-compatibility"""
from uuid import uuid4
from hashlib import sha256


class NameMapping():
    """Mapping between external arbitrary names and internel names with restricted length and ODATA-compatibility"""
    def __init__(self, max_length = 127) -> None:
        self.ext_tree: dict = {}
        self.int: set = set()
        self.max_length = max_length
    def register(self, ext_path:list, type_prefix = '', definition = {}, extt:dict = None, depth = 0,\
        int_name_prefix:str = '', ext_path_prefix:list = []) -> str:
        ext_tree = extt if extt else self.ext_tree
        next_step_ext = ext_path[0]
        if 'contains' not in ext_tree:
            ext_tree['contains'] = {}
        if not next_step_ext in ext_tree['contains']:
            internal = type_prefix + self.new_int_name(next_step_ext, depth, int_name_prefix, ext_path_prefix)
            ext_tree['contains'][next_step_ext] = {'int': internal}
        if definition and len(ext_path) == 1:
            ext_tree['contains'][next_step_ext]['definition'] = definition    
                
        if len(ext_path) > 1:
            return self.register(ext_path[1:], type_prefix, definition, ext_tree['contains'][next_step_ext],\
                depth + 1, ext_tree['contains'][next_step_ext]['int'], ext_path_prefix + [next_step_ext])
        return ext_tree['contains'][next_step_ext]['int'], ext_tree['contains'][next_step_ext]

    @staticmethod
    def normalize_v1(s):
        s = ''.join(c for c in s if c.isalnum())
        if s and s[0].isnumeric():
            return chr(65 + int(s[0])) + s[1:].upper()[:20]
        else: return s.upper()[:20]


    def add_name(self, int_name_prefix, next_step_name):
        if len(int_name_prefix) + len(next_step_name) >= 99:
            name = int_name_prefix[:99 - len(next_step_name)] + '_' + next_step_name
        elif int_name_prefix:
            name = int_name_prefix + '_' + next_step_name
        else:
            name = next_step_name
        if name not in self.int:
            self.int.add(name)
            return name
        return ''

    def new_int_name(self, next_step_ext, depth: int, int_name_prefix: str, ext_path_prefix: list) -> str:
        # simple mapping rule
        if len(int_name_prefix) <= 80:
            name = self.add_name(int_name_prefix, NameMapping.normalize_v1(next_step_ext))
            if name:
                return name
        # hash
        ext_name_concat = '_'.join(ext_path_prefix + [next_step_ext])
        name = self.add_name(int_name_prefix, 'H' + sha256(ext_name_concat.encode('utf-8')).hexdigest().upper())
        if name:
            return name
        # uuid if hash collision
        return self.add_name(int_name_prefix, str(uuid4()).upper())
