""" CRUD Database Operations"""
import json
import base64
from hdbcli.dbapi import Error as HDBException

from db_connection_pool import (DBBulkProcessing, DBConnection)
import server_globals as glob
from constants import (CONCURRENT_CONNECTIONS, TYPES_B64_ENCODE, TYPES_SPATIAL,
                       DBUserType)
import convert


class CrudException(Exception):
    """ Exception in CRUD """


def get_table_sequence(mapping, table_sequence, current_table):
    for prop in current_table['columns'].values():
        if 'rel' in prop and prop['rel']['type'] == 'containment':
            next_table = mapping['tables'][prop['rel']['table_name']]
            get_table_sequence(mapping, table_sequence, next_table)
    table_sequence.append(current_table)


def value_int_to_ext(typ, value):
    if typ in TYPES_B64_ENCODE:
        return base64.encodebytes(value).decode('utf-8')
    elif typ in TYPES_SPATIAL:
        return json.loads(value)
    return value


def add_value(column, obj, path, value):
    if value is None:
        return
    if len(path) == 1:
        if 'type' in column:
            obj[path[0]] = value_int_to_ext(column['type'], value)
        else:
            obj[path[0]] = value
    else:
        if not path[0] in obj:
            obj[path[0]] = {}
        add_value(column, obj[path[0]], path[1:], value)

class CRUD():
    """ DB-Operations for Create, Cread, Update, Delete """
    def __init__(self,ctx) -> None:
        self.mapping = ctx['mapping']
        self.schema_name = ctx['schema_name']
        #self.tenant_id = ctx['tenant_id']
        self.id_generator = ctx['id_generator']

    def _extract_object_keys(self, objects):
        obj_key_idx = {}
        obj_keys = {'id':{}, 'source':{}}
        for object_type, obj_list in objects.items():
            obj_key_idx[object_type] = {}
            if not isinstance(obj_list, list):
                raise CrudException('provide list of objects per object type')
            if not object_type in self.mapping['entities']:
                raise CrudException(f'Unknown object type {object_type}')
            anchor_table = self.mapping['tables'][self.mapping['entities'][object_type]['table_name']]
            if anchor_table['columns'][anchor_table['pk']]['external_path'][0] != 'id':
                continue
            for obj in obj_list:
                if 'id' in obj:
                    if obj['id'] in obj_key_idx[object_type]:
                        raise CrudException(f'{object_type} has duplicate ids {obj["id"]}')
                    obj_key_idx[object_type][obj['id']] = obj
                    if object_type not in obj_keys['id']:
                        obj_keys['id'][object_type] = []
                    obj_keys['id'][object_type].append(obj['id'])
                if 'source' in obj:
                    if not isinstance(obj['source'], list):
                        raise CrudException('Source property must be an array')
                    for source in obj['source']:
                        if not isinstance(source, dict):
                            raise CrudException('Source property must be an array of dicts')
                        source_key = (source['name'], source['type'], source['sid'])
                        if source_key in obj_key_idx[object_type]:
                            raise CrudException(f'{object_type} has duplicate source key {source_key}')
                        obj_key_idx[object_type][source_key] = obj
                    if 'id' not in obj:
                        if object_type not in obj_keys['source']:
                            obj_keys['source'][object_type] = []
                        obj_keys['source'][object_type].append(source_key)
                elif 'id' not in obj:
                    obj['id'] = self.id_generator.get_id('', 0)

        return obj_key_idx, obj_keys

    '''
    async def _classify_ids(self, ids_sql, ids_promise, obj_keys_used):
        ids_new = {}
        ids_on_db = {}
        if ids_sql:
            provided_ids = await ids_promise
            for i, (object_type, oids) in enumerate(obj_keys_used.items()):
                in_msg = set(oids)
                on_db = set([w[0] for w in provided_ids[i]])
                new = in_msg - on_db
                if new:
                    ids_new[object_type] = new
                if on_db:
                    ids_on_db[object_type] = on_db
        return (ids_new, ids_on_db)


    async def _classify_keys(self, sources_sql, sources_promise, obj_keys_used):
        sources_new = {}
        sources_on_db = {}
        if sources_sql:
            provided_sources = await sources_promise
            for i, (object_type, source_keys) in enumerate(obj_keys_used.items()):
                in_msg = set(source_keys)
                on_db = {(w[1], w[2], w[3]):w[0] for w in provided_sources[i]}
                new = in_msg - set(on_db)
                if new:
                    sources_new[object_type] = new
                if on_db:
                    sources_on_db[object_type] = on_db
        return (sources_new, sources_on_db)
'''

    async def _classify(self, key_sql, key_promise, access_func):
        new_keys = {}
        keys_on_db = {}
        if key_sql:
            keys_fetched = await key_promise
            for i, (object_type, ks) in enumerate(key_sql.items()):
                #for i, (object_type, requested_keys) in enumerate(obj_keys_used.items()):
                #in_msg = set(requested_keys)
                on_db = access_func(keys_fetched[i])
                new = ks['keys'] - set(on_db)
                if new:
                    new_keys[object_type] = new
                if on_db:
                    keys_on_db[object_type] = on_db
        return (new_keys, keys_on_db)



    def _process_associations(self, obj_key_idx, entity, obj, unknown_objects):
        #if 'table_name' in entity and not ('elements' in entity or 'items' in entity):
        #    return
        if isinstance(obj, dict):
            if not ('elements' in entity and entity['elements'] or 'items' in entity):
                return
            associations = {}
            for k, v in obj.items():
                if not k in entity['elements']:
                    raise CrudException(f'Unknown property {k}')
                prop = entity['elements'][k]
                if 'definition' in prop and 'type' in prop['definition'] and prop['definition']['type'] == 'cds.Association':
                    if 'target_pk' in prop['definition'] and prop['definition']['target_pk'] == 'id' and \
                        not ('isVirtual' in prop['definition'] and prop['definition']['isVirtual']):
                        object_type = prop['definition']['target']
                        if 'id' in v:
                            if object_type in obj_key_idx and v['id'] in obj_key_idx[object_type]:
                                associations[k] = obj_key_idx[object_type][v['id']]
                            else:
                                do = {'id':v['id']}
                                if 'id' not in unknown_objects:
                                    unknown_objects['id'] = {}
                                if object_type not in unknown_objects['id']:
                                    unknown_objects['id'][object_type] = {}
                                unknown_objects['id'][object_type][v['id']] = do
                                associations[k] = do
                        elif 'source' in v:
                            if not (isinstance(v['source'], list) and len(v['source']) == 1):
                                raise CrudException(f'Property {k} is association. Source property must be list of length 1')
                            source_key = (v['source'][0]['name'], v['source'][0]['type'], v['source'][0]['sid'])
                            if object_type in obj_key_idx and source_key in obj_key_idx[object_type]:
                                associations[k] = obj_key_idx[object_type][source_key]
                            else:
                                do = {'source':v['source']}
                                if 'source' not in unknown_objects:
                                    unknown_objects['source'] = {}
                                if object_type not in unknown_objects['source']:
                                    unknown_objects['source'][object_type] = {}
                                unknown_objects['source'][object_type][source_key] = do
                                associations[k] = do
                        else:
                            raise CrudException(f'Property {k} is association. Needs either "id":str or "source":[] to establish foreign key')
                else:
                    self._process_associations(\
                        obj_key_idx, entity['elements'][k], v, unknown_objects)
            for k, v in associations.items():
                obj[k] = v
        elif isinstance(obj, list):
            if not 'items' in entity:
                raise CrudException(f'list expected, {str.dumps(obj)} found')
            for o in obj:
                self._process_associations(obj_key_idx, entity['items'], o, unknown_objects)

    async def _id_preprocessing(self, db_bulk, objects, write_mode: convert.WriteMode):
        obj_key_idx, obj_keys = self._extract_object_keys(objects)
        unknown_objects = {}
        for object_type, obj_list in objects.items():
            for obj in obj_list:
                self._process_associations(\
                    obj_key_idx, self.mapping['entities'][object_type], obj, unknown_objects)

        provided_ids_sql = {}
        for object_type, oids in obj_keys['id'].items():
            if oids:
                table_name = self.mapping['entities'][object_type]['table_name']
                keys = set(oids)
                ids_str = ', '.join([f"'{str(w)}'" for w in keys])
                provided_ids_sql[object_type] = {'keys': keys, 'sql':
                    f'select "ID" from "{self.schema_name}"."{table_name}" where "ID" in ({ids_str})'}
        provided_ids_promise = db_bulk.execute_fetchall([w['sql'] for w in provided_ids_sql.values()])\
            if provided_ids_sql else None

        provided_sources_sql = {}
        for object_type, source_list in obj_keys['source'].items():
            table_name = self.mapping['entities'][object_type]['elements']['source']['items']['table_name']
            keys = set(source_list)
            where_clause = ' OR '.join(\
            [f'("NAME" = \'{name}\' and "TYPE" = \'{type}\' and "SID" = \'{sid}\')' for name, type, sid in source_list])
            provided_sources_sql[object_type] = {'keys': keys, 'sql':
                f'select "_ID", "NAME", "TYPE", "SID" from "{self.schema_name}"."{table_name}" where {where_clause}'}
        provided_sources_promise = db_bulk.execute_fetchall([w['sql'] for w in provided_sources_sql.values()])\
            if provided_sources_sql else None

        unknown_ids_sql = {}
        if 'id' in unknown_objects:
            for object_type, v in unknown_objects['id'].items():
                table_name = self.mapping['entities'][object_type]['table_name']
                keys = set(v.keys())
                ids_str = ', '.join([f"'{str(w)}'" for w in keys])
                unknown_ids_sql[object_type] = {'keys': keys, 'sql':
                    f'select "ID" from "{self.schema_name}"."{table_name}" where "ID" in ({ids_str})'}
        unknown_ids_promise = db_bulk.execute_fetchall([w['sql'] for w in unknown_ids_sql.values()])\
            if unknown_ids_sql else None

        unknown_sources_sql = {}
        if 'source' in unknown_objects:
            for object_type, v in unknown_objects['source'].items():
                table_name = self.mapping['entities'][object_type]['elements']['source']['items']['table_name']
                keys = set(v.keys())
                where_clause = ' OR '.join(\
                [f'("NAME" = \'{name}\' and "TYPE" = \'{type}\' and "SID" = \'{sid}\')' for name, type, sid in keys])
                unknown_sources_sql[object_type] = {'keys': keys, 'sql':
                    f'select "_ID", "NAME", "TYPE", "SID" from "{self.schema_name}"."{table_name}" where {where_clause}'}
        unknown_sources_promise = db_bulk.execute_fetchall([w['sql'] for w in unknown_sources_sql.values()])\
            if unknown_sources_sql else None
        provided_ids_new, provided_ids_on_db = await\
            self._classify(provided_ids_sql, provided_ids_promise,\
                lambda a : set([w[0] for w in a]))
        provided_sources_new, provided_sources_on_db = await\
            self._classify(provided_sources_sql, provided_sources_promise,\
                lambda a : {(w[1], w[2], w[3]):w[0] for w in a})
        unknown_ids_new, unknown_ids_on_db = await\
            self._classify(unknown_ids_sql, unknown_ids_promise,\
                lambda a : set([w[0] for w in a]))
        unknown_sources_new, unkown_sources_on_db = await\
            self._classify(unknown_sources_sql, unknown_sources_promise,\
                lambda a : {(w[1], w[2], w[3]):w[0] for w in a})
        if provided_sources_new:
            for object_type, keys in provided_sources_new.items():
                for source_key in keys:
                    obj_key_idx[object_type][source_key]['id'] = self.id_generator.get_id('', 0)
        if unkown_sources_on_db:
            for object_type, keys in unkown_sources_on_db.items():
                for source_key, oid in keys.items():
                    unknown_objects['source'][object_type][source_key]['id'] = oid
        if unknown_ids_on_db:
            for object_type, keys in unknown_ids_on_db.items():
                for oid in keys:
                    unknown_objects['id'][object_type][oid]['id'] = oid
        if write_mode == convert.WriteMode.CREATE:
            if provided_ids_on_db:
                err = {}
                for object_type, v in provided_ids_on_db.items():
                    if not object_type in err:
                        err[object_type] = []
                    for oid in v:
                        err[object_type].append({'id':oid})
                s = json.dumps(err)
                raise CrudException(f'Objects already exist: {s}')
            if provided_sources_on_db:
                err = {}
                for object_type, v in provided_sources_on_db.items():
                    if not object_type in err:
                        err[object_type] = []
                    for (name, typ, sid), oid in v.items():
                        err[object_type].append({'id':oid, 'source':[{'name':name, 'type': typ, 'sid': sid}]})
                s = json.dumps(err)
                raise CrudException(f'Objects already exist: {s}')
        if unknown_ids_new:
            err = {}
            for object_type, v in unknown_ids_new.items():
                if not object_type in err:
                    err[object_type] = []
                for oid in v:
                    err[object_type].append({'id':oid})
            s = json.dumps(err)
            raise CrudException(f'Associated object does not exist: {s}')
        if unknown_sources_new:
            err = {}
            for object_type, v in unknown_sources_new.items():
                if not object_type in err:
                    err[object_type] = []
                for (name, typ, sid), oid in v.items():
                    err[object_type].append({'id':oid, 'source':[{'name':name, 'type': typ, 'sid': sid}]})
            s = json.dumps(err)
            raise CrudException(f'Associated object does not exist: {s}')
        return (provided_ids_new, provided_ids_on_db, provided_sources_new, provided_sources_on_db,\
            unknown_ids_new, unknown_ids_on_db, unknown_sources_new, unkown_sources_on_db)

    async def write_data(self, objects, write_mode: convert.WriteMode):
        with DBBulkProcessing(glob.connection_pools[DBUserType.DATA_WRITE], CONCURRENT_CONNECTIONS) as db_bulk:
            try:
                await self._id_preprocessing(db_bulk, objects, write_mode)
                res = await self._write_data(db_bulk, objects, write_mode)
                await db_bulk.commit()
            except HDBException as e:
                await db_bulk.rollback()
                raise CrudException(f'Data Error: {e.errortext}') from e
        return res


    async def update_data(self, objects):
        with DBBulkProcessing(glob.connection_pools[DBUserType.DATA_WRITE], CONCURRENT_CONNECTIONS) as db_bulk:
            try:
                await self._id_preprocessing(db_bulk, objects, convert.WriteMode.UPDATE)
                res = await self._update_data(db_bulk, objects)
                await db_bulk.commit()
            except HDBException as e:
                await db_bulk.rollback()
                raise CrudException(f'Data Error: {e.errortext}') from e
        return res


    async def delete_data(self, objects):
        with DBBulkProcessing(glob.connection_pools[DBUserType.DATA_WRITE], CONCURRENT_CONNECTIONS) as db_bulk:
            try:
                res = await self._delete_data(db_bulk, objects)
                await db_bulk.commit()
            except HDBException as e:
                await db_bulk.rollback()
                raise CrudException(f'Data Error: {e.errortext}') from e
        return res


    async def _write_data(self, db_bulk, objects, write_mode: convert.WriteMode):
        try:
            dml = convert.objects_to_dml(self.mapping, objects, write_mode, self.id_generator, True)
        except convert.DataException as e:
            raise CrudException(str(e)) from e

        operations = []
        for table_name, v in dml['inserts'].items():
            column_names = ','.join([f'"{k}"' for k in v['columns'].keys()])
            cp = []
            table = self.mapping['tables'][table_name]
            for column_name in v['columns'].keys():
                if table['columns'][column_name]['type'] in TYPES_SPATIAL:
                    srid = table['columns'][column_name]['srid']
                    cp.append(f'ST_GeomFromGeoJSON(?, {srid})')
                else:
                    cp.append('?')
            column_placeholders = ','.join(cp)
            sql = f'insert into "{self.schema_name}"."{table_name}" ({column_names}) values ({column_placeholders})'
            operations.append((sql, v['rows']))

        await db_bulk.executemany(operations)
        response = {}
        for object_type, obj_list in objects.items():
            root_table = self.mapping['tables'][self.mapping['entities']
                                        [object_type]['table_name']]
            key_property = root_table['columns'][root_table['pk']
                                                ]['external_path'][0]
            for obj in obj_list:
                res = {}
                if key_property in obj:
                    res[key_property] = obj[key_property]
                if 'source' in obj:
                    res['source'] = obj['source']
                if res:
                    if not object_type in response:
                        response[object_type] = []
                    response[object_type].append(res)
        return response


    async def read_data(self, objects, type_annotation):
        with DBConnection(glob.connection_pools[DBUserType.DATA_READ]) as db:
            response = {}
            for object_type, obj_list in objects.items():
                if not isinstance(obj_list, list):
                    raise CrudException('provide list of objects per object type')
                if object_type not in self.mapping['entities']:
                    raise CrudException(f'unknown object type {object_type}')
                root_table = self.mapping['tables'][self.mapping['entities']
                                            [object_type]['table_name']]
                ids = []
                primary_key_property_name = \
                    root_table['columns'][root_table['pk']]['external_path'][0]
                table_sequence = []
                get_table_sequence(self.mapping, table_sequence, root_table)
                for obj in obj_list:
                    if not primary_key_property_name in obj:
                        raise CrudException(
                            f'primary key {primary_key_property_name} not found')
                    ids.append(obj[primary_key_property_name])
                id_list = ', '.join([f"'{w}'" for w in ids])
                all_objects = {}

                for table in table_sequence:
                    all_objects[table['table_name']] = {}
                    sql = table['sql']['select'].format(
                        schema_name=self.schema_name, id_list=id_list)
                    db.cur.execute(sql)
                    if '_VALUE' in table['columns']:
                        for row in db.cur:
                            key, _, val_int = row
                            value = value_int_to_ext(
                                table['columns']['_VALUE']['type'], val_int)
                            if key in all_objects[table['table_name']]:
                                all_objects[table['table_name']][key].append(value)
                            else:
                                all_objects[table['table_name']][key] = [value]
                    else:
                        for row in db.cur:
                            i = 0
                            if table['level'] == 0 and type_annotation:
                                res_obj = {'@type': object_type}
                            else:
                                res_obj = {}
                            for prop_name, prop in table['columns'].items():
                                if prop_name == table['pk']:
                                    sub_obj_key = row[i]
                                    if table['level'] == 0:
                                        res_key = row[i]
                                        add_value(prop, res_obj,
                                                prop['external_path'], row[i])
                                elif table['level'] > 0 and prop_name == table['pkParent']:
                                    res_key = row[i]
                                elif 'isVirtual' in prop and prop['isVirtual']:
                                    if prop['rel']['type'] == 'containment':
                                        if sub_obj_key in all_objects[prop['rel']['table_name']]:
                                            sub_obj = all_objects[prop['rel']
                                                                ['table_name']][sub_obj_key]
                                            add_value(
                                                prop, res_obj, prop['external_path'], sub_obj)
                                    continue
                                elif 'rel' in prop and prop['rel']['type'] == 'association':
                                    rel_table = self.mapping['tables'][prop['rel']
                                                                ['table_name']]
                                    path = prop['external_path']\
                                        + rel_table['columns'][rel_table['pk']]['external_path']
                                    add_value(prop, res_obj, path, row[i])
                                else:
                                    add_value(prop, res_obj,
                                            prop['external_path'], row[i])
                                i += 1
                            if table['level'] > 0:
                                if not res_key in all_objects[table['table_name']]:
                                    all_objects[table['table_name']][res_key] = []
                                all_objects[table['table_name']
                                            ][res_key].append(res_obj)
                            else:
                                all_objects[table['table_name']][res_key] = res_obj
                response[object_type] = []
                for i in ids:
                    response[object_type].append(
                        all_objects[root_table['table_name']][i])
        return response


    async def _update_data(self, db_bulk, objects):
        all_ids = {}
        select_ids_sqls = []
        read_source_sql = {}
        for object_type, obj_list in objects.items():
            if not isinstance(obj_list, list):
                raise CrudException('provide list of objects per object type')
            if object_type not in self.mapping['entities']:
                raise CrudException(f'unknown object type {object_type}')
            has_source_ids = 'source' in self.mapping['entities'][object_type]['elements']
            source_ids = []
            root_table = self.mapping['tables'][self.mapping['entities']
                                        [object_type]['table_name']]
            ids = []
            primary_key_property_name = \
                root_table['columns'][root_table['pk']]['external_path'][0]
            for obj in obj_list:
                if not primary_key_property_name in obj:
                    raise CrudException(
                        f'Data Error: {primary_key_property_name} missing in {object_type}')
                ids.append(obj[primary_key_property_name])
                if has_source_ids and 'source' not in obj:
                    source_ids.append(obj[primary_key_property_name])
            if source_ids:
                table_name = self.mapping['entities'][object_type]['elements']['source']['items']['table_name']
                column_name = '_ID'
                ids_str = ', '.join([f"'{str(w)}'" for w in source_ids])
                read_source_sql[object_type] = \
                    f'select "{column_name}", "NAME", "TYPE", "SID" from "{self.schema_name}"."{table_name}" where "{column_name}" in ({ids_str})'
            if len(ids) != len(set(ids)):
                raise CrudException(
                    f'Data Error: duplicates detected for {object_type}')
            table_name = root_table['table_name']
            column_name = root_table['pk']
            ids_str = ', '.join([f"'{str(w)}'" for w in ids])
            select_ids_sqls.append(
                f'select "{column_name}" from "{self.schema_name}"."{table_name}" where "{column_name}" in ({ids_str})')
            all_ids[object_type] = ids

        all_db_ids = await db_bulk.execute_fetchall(select_ids_sqls)
        if read_source_sql:
            all_sources = await db_bulk.execute_fetchall([w for w in read_source_sql.values()])

        for i, (object_type, ids) in enumerate(all_ids.items()):
            db_ids = [w[0] for w in all_db_ids[i]]
            if len(ids) != len(db_ids):
                missing_ids = ', '.join([str(w)
                                        for w in list(set(ids) - set(db_ids))])
                raise CrudException(
                    f'Data Error: {object_type} {missing_ids} cannot be updated because they do not exist')

        if read_source_sql:
            source_objects = {}
            for i, object_type in enumerate(read_source_sql.keys()):
                if all_sources[i]:
                    source_objects[object_type] = {}
                    for oid, name, typ, sid in all_sources[i]:
                        src = {'name': name, 'type': typ, 'sid': sid}
                        if oid in source_objects[object_type]:
                            source_objects[object_type][oid].append(src)
                        else:
                            source_objects[object_type][oid] = [src]
            for object_type, obj_list in objects.items():
                if object_type in source_objects:
                    for obj in obj_list:
                        if obj['id'] in source_objects[object_type]:
                            obj['source'] = source_objects[object_type][obj['id']]

        await self._delete_data(db_bulk, objects)
        await db_bulk.commit()
        return await self._write_data(db_bulk, objects, convert.WriteMode.UPDATE)


    async def _delete_data(self, db_bulk, objects):
        sqls = []
        for object_type, obj_list in objects.items():
            if not isinstance(obj_list, list):
                raise CrudException('provide list of objects per object type')
            if object_type not in self.mapping['entities']:
                raise CrudException(f'unknown object type {object_type}')
            root_table = self.mapping['tables'][self.mapping['entities']
                                        [object_type]['table_name']]
            ids = []
            primary_key_property_name = \
                root_table['columns'][root_table['pk']]['external_path'][0]
            table_sequence = []
            get_table_sequence(self.mapping, table_sequence, root_table)
            for obj in obj_list:
                if not primary_key_property_name in obj:
                    raise CrudException(
                        f'primary key {primary_key_property_name} not found')
                ids.append(obj[primary_key_property_name])
            id_list = ', '.join([f"'{w}'" for w in ids])

            for table in table_sequence:
                sqls.append(table['sql']['delete'].format(
                    schema_name=self.schema_name, id_list=id_list))
        if sqls:
            await db_bulk.execute(sqls)
        return None
