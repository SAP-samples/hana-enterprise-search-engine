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

    async def write_data(self, objects, write_mode: convert.WriteMode):
        with DBBulkProcessing(glob.connection_pools[DBUserType.DATA_WRITE], CONCURRENT_CONNECTIONS) as db_bulk:
            try:
                res = await self._write_data(db_bulk, objects, write_mode)
                await db_bulk.commit()
            except HDBException as e:
                await db_bulk.rollback()
                raise CrudException(f'Data Error: {e.errortext}') from e
        return res


    async def update_data(self, objects):
        with DBBulkProcessing(glob.connection_pools[DBUserType.DATA_WRITE], CONCURRENT_CONNECTIONS) as db_bulk:
            try:
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
            dml = convert.objects_to_dml(self.mapping, objects, write_mode, self.id_generator)
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
            if not isinstance(obj_list, list):
                raise CrudException('provide list of objects per object type')
            if object_type not in self.mapping['entities']:
                raise CrudException(f'unknown object type {object_type}')
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
