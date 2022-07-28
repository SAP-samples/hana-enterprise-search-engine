Python 3.10.5 (tags/v3.10.5:f377153, Jun  6 2022, 16:14:13) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
from hdbcli import dbapi

cur = con.cursor()
cur.execute('create schema kf20220727')
True
cur.execute('set schema kf20220727')
True
cur.execute('create table spatial ( "ID" NVARCHAR(36) PRIMARY KEY, "TESTPROPERTY" ST_GEOMETRY )')
True
cur.execute('insert into spatial values (\'1\', \'ST_GeomFromGeoJSON(\'{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}\', 4326)\')')
Traceback (most recent call last):
  File "<pyshell#6>", line 1, in <module>
    cur.execute('insert into spatial values (\'1\', \'ST_GeomFromGeoJSON(\'{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}\', 4326)\')')
hdbcli.dbapi.ProgrammingError: (257, 'sql syntax error: incorrect syntax near "{": line 1 col 55 (at pos 55)')
cur.execute('insert into spatial values (\'1\', \'ST_GeomFromGeoJSON(\'{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326)\')')
Traceback (most recent call last):
  File "<pyshell#7>", line 1, in <module>
    cur.execute('insert into spatial values (\'1\', \'ST_GeomFromGeoJSON(\'{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326)\')')
hdbcli.dbapi.ProgrammingError: (257, 'sql syntax error: incorrect syntax near "{": line 1 col 55 (at pos 55)')
cur.execute('insert into spatial values (\'1\', null')
Traceback (most recent call last):
  File "<pyshell#8>", line 1, in <module>
    cur.execute('insert into spatial values (\'1\', null')
hdbcli.dbapi.ProgrammingError: (257, 'sql syntax error: line 1 col 34 (at pos 34)')
cur.execute('insert into spatial values (\'1\', null)')
True
cur.execute('insert into spatial values (\'2\', \'ST_GeomFromGeoJSON(\'{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326)\')')
Traceback (most recent call last):
  File "<pyshell#10>", line 1, in <module>
    cur.execute('insert into spatial values (\'2\', \'ST_GeomFromGeoJSON(\'{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326)\')')
hdbcli.dbapi.ProgrammingError: (257, 'sql syntax error: incorrect syntax near "{": line 1 col 55 (at pos 55)')
'insert into spatial values (\'2\', \'ST_GeomFromGeoJSON(\'{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326)\')'[55:]
'"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326)\')'
sql = 'insert into spatial values (\'2\', \'ST_GeomFromGeoJSON(\'{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326)\')'
print(sql)
insert into spatial values ('2', 'ST_GeomFromGeoJSON('{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326)')
sql = 'insert into spatial values (\'2\', \'ST_GeomFromGeoJSON({"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326)\')'
print(sql)
insert into spatial values ('2', 'ST_GeomFromGeoJSON({"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326)')
cur.execute(sql)
Traceback (most recent call last):
  File "<pyshell#16>", line 1, in <module>
    cur.execute(sql)
hdbcli.dbapi.ProgrammingError: (266, 'inconsistent datatype: VARCHAR type is incompatible with ST_GEOMETRY type: line 1 col 34 (at pos 33)')
sql = 'insert into spatial values (\'2\', ST_GeomFromGeoJSON(\'{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326))'

print(sql)
insert into spatial values ('2', ST_GeomFromGeoJSON('{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}, 4326))
cur.execute(sql)
                                                    
Traceback (most recent call last):
  File "<pyshell#20>", line 1, in <module>
    cur.execute(sql)
hdbcli.dbapi.ProgrammingError: (257, 'sql syntax error: unterminated quoted string literal: line 1 col 53 (at pos 53)')
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "LineString", "coordinates": [[1, 2], [5, 7]]}\', 4326).ST_AsText() FROM DUMMY')
                                                    
True
res = cur.fetchone()[0]
                                                    
res
                                                    
'LINESTRING (1 2,5 7)'
type(res)
                                                    
<class 'str'>
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "LineString", "coordinates": [[1, 2], [5, 7]]}\', 4326) FROM DUMMY')
                                                    
True
res = cur.fetchone()[0]
                                                    
type(res)
                                                    
<class 'memoryview'>
sql = f'insert into spatial ("ID" NVARCHAR, "TESTPROPERTY") values (?, ?)'
                                                    
cur.executemany(sql, [('3', None)])
                                                    
Traceback (most recent call last):
  File "<pyshell#29>", line 1, in <module>
    cur.executemany(sql, [('3', None)])
hdbcli.dbapi.ProgrammingError: (257, 'sql syntax error: incorrect syntax near "NVARCHAR": line 1 col 27 (at pos 27)')
sql = f'insert into spatial ("ID", "TESTPROPERTY") values (?, ?)'
                                                    
cur.executemany(sql, [('3', None)])
                                                    
(1,)
cur.execute('select * from spatial')
                                                    
True
print(cur.fetchall())
                                                    
[('1', None), ('3', None)]
type(res)
                                                    
<class 'memoryview'>
cur.executemany(sql, [('2', res)])
                                                    
(1,)
cur.execute('select * from spatial')
                                                    
True
print(cur.fetchall())
                                                    
[('1', None), ('3', None), ('2', <memory at 0x000002233EACFAC0>)]
cur.execute('select ID, TESTPROPERTY.ST_AsGeoJSON() from spatial')
                                                    
True
print(cur.fetchall())
                                                    
[('1', None), ('3', None), ('2', '{"type": "LineString", "coordinates": [[1, 2], [5, 7]]}')]
str(res)
                                                    
'<memory at 0x000002233EACFA00>'
res.encode('utf-8')
                                                    
Traceback (most recent call last):
  File "<pyshell#41>", line 1, in <module>
    res.encode('utf-8')
AttributeError: 'memoryview' object has no attribute 'encode'
res.itemsize
                                                    
1
res.hex
                                                    
<built-in method hex of memoryview object at 0x000002233EACFA00>
res.hex()
                                                    
'010200000002000000000000000000f03f000000000000004000000000000014400000000000001c40'
res.tobytes()
                                                    
b'\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x1c@'
res.hex().decode('utf-8')
                                                    
Traceback (most recent call last):
  File "<pyshell#46>", line 1, in <module>
    res.hex().decode('utf-8')
AttributeError: 'str' object has no attribute 'decode'. Did you mean: 'encode'?
res.tobytes().decode('utf-8')
                                                    
Traceback (most recent call last):
  File "<pyshell#47>", line 1, in <module>
    res.tobytes().decode('utf-8')
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf0 in position 15: invalid continuation byte
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "LineString", "coordinates": [[1, 2], [5, 7]]}\', 4326) FROM DUMMY')
                                                    
True
res = cur.fetchone()[0]
                                                    
res.hex()
                                                    
'010200000002000000000000000000f03f000000000000004000000000000014400000000000001c40'
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "LineString", "coordinates": [[2, 2], [5, 7]]}\', 4326) FROM DUMMY')
                                                    
True
res = cur.fetchone()[0]
                                                    
res.hex()
                                                    
'0102000000020000000000000000000040000000000000004000000000000014400000000000001c40'
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "LineString", "coordinates": [[1, 2], [5, 7], [5, 7]]}\', 4326) FROM DUMMY')
                                                    
True
cur.fetchone()[0].hex()
                                                    
'010200000003000000000000000000f03f000000000000004000000000000014400000000000001c4000000000000014400000000000001c40'
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}\', 4326) FROM DUMMY')
                                                    
True
cur.fetchone()[0].hex()
                                                    
'010200000002000000793073cb58ceff3f000000000000004000000000000014400000000000001c40'
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "Point", "coordinates": [1, 2]]}\', 4326) FROM DUMMY')
                                                    
Traceback (most recent call last):
  File "<pyshell#58>", line 1, in <module>
    cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "Point", "coordinates": [1, 2]]}\', 4326) FROM DUMMY')
hdbcli.dbapi.Error: (669, 'spatial error: exception 1601839: Expected further object members or the object-end at line 1, column 40\n at "st_geomfromgeojson" function (at pos 7) ')
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "Point", "coordinates": [1, 2]}\', 4326) FROM DUMMY')
                                                    
True
cur.fetchone()[0].hex()
                                                    
'0101000000000000000000f03f0000000000000040'
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "Point", "coordinates": [0, 0]}\', 4326) FROM DUMMY')
                                                    
True

cur.fetchone()[0].hex()
                                                    
'010100000000000000000000000000000000000000'
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "Point", "coordinates": [0, 0]}\', 0) FROM DUMMY')
                                                    
True

cur.fetchone()[0].hex()
                                                    
'010100000000000000000000000000000000000000'
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "Point", "coordinates": [1, 0]}\', 0) FROM DUMMY')
                                                    
True
cur.fetchone()[0].hex()
                                                    
'0101000000000000000000f03f0000000000000000'
struct.pack("B", 65).hex()
                                                    
Traceback (most recent call last):
  File "<pyshell#67>", line 1, in <module>
    struct.pack("B", 65).hex()
NameError: name 'struct' is not defined
import struct
struct.pack("B", 65).hex()
'41'
struct.pack("B", 1).hex()
'01'
struct.pack("H", 256).hex()
'0001'
struct.pack("H", 1).hex()
'0100'
struct.pack("H", 257).hex()
'0101'
struct.pack("H", 255).hex()
'ff00'
struct.pack("H", 257).hex()
'0101'
def point(x,y):
    return struct.pack("d", x) + struct.pack("d", y)

struct.pack("H", 257)
b'\x01\x01'
def point(x,y):
    return b'\x01\x01' + struct.pack("d", x) + struct.pack("d", y)

point(1,0)
b'\x01\x01\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00'
point(1,0).hex()
'0101000000000000f03f0000000000000000'
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "Point", "coordinates": [1, 0]}\', 0) FROM DUMMY')
True
ref = cur.fetchone()[0]
ref == point(1,0).hex()
False
ref.hex()
'0101000000000000000000f03f0000000000000000'
point(1,0).hex()
'0101000000000000f03f0000000000000000'
def point(x,y):
    return b'\x01\x01\x00\x00\x00' + struct.pack("d", x) + struct.pack("d", y)

ref == point(1,0).hex()
False
ref.hex()
'0101000000000000000000f03f0000000000000000'
point(1,0).hex()
'0101000000000000000000f03f0000000000000000'
ref.hex() == point(1,0).hex()
True
ref == point(1,0)
True
sql = f'insert into spatial ("ID", "TESTPROPERTY") values (?, new ST_GeomFromGeoJSON(?))'
cur.executemany(sql, [('10', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}')])
Traceback (most recent call last):
  File "<pyshell#97>", line 1, in <module>
    cur.executemany(sql, [('10', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}')])
hdbcli.dbapi.ProgrammingError: (257, 'sql syntax error: incorrect syntax near "ST_GeomFromGeoJSON": line 1 col 59 (at pos 59)')
sql = f'insert into spatial ("ID", "TESTPROPERTY") values (?, new ST_GeomFromGeoJSON(?, 4326))'
cur.executemany(sql, [('10', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}')])
Traceback (most recent call last):
  File "<pyshell#99>", line 1, in <module>
    cur.executemany(sql, [('10', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}')])
hdbcli.dbapi.ProgrammingError: (257, 'sql syntax error: incorrect syntax near "ST_GeomFromGeoJSON": line 1 col 59 (at pos 59)')
cur.execute('SELECT ST_GeomFromGeoJSON(\'{"type": "Point", "coordinates": [0, 0]}\', 4326) FROM DUMMY')
True
sql = f'insert into spatial ("ID", "TESTPROPERTY") values (?, ST_GeomFromGeoJSON(?, 4326))'
cur.executemany(sql, [('10', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}')])
Traceback (most recent call last):
  File "<pyshell#102>", line 1, in <module>
    cur.executemany(sql, [('10', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}')])
hdbcli.dbapi.Error: (669, "spatial error: exception 1620501: The geometry's SRID (4326) does not match the column's SRID (0) at column 'TESTPROPERTY'\n")
sql = f'insert into spatial ("ID", "TESTPROPERTY") values (?, ST_GeomFromGeoJSON(?, 0))'
cur.executemany(sql, [('10', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}')])
(1,)
cur.execute('select * from spatial')
True
print(cur.fetchall())
[('1', None), ('3', None), ('2', <memory at 0x000002233EACFB80>), ('10', <memory at 0x000002233EACFC40>)]
cur.execute('select ID, TESTPROPERTY.ST_AsGeoJSON() from spatial')
True
print(cur.fetchall())
[('1', None), ('3', None), ('2', '{"type": "LineString", "coordinates": [[1, 2], [5, 7]]}'), ('10', '{"type": "LineString", "coordinates": [[1.987878, 2], [5, 7]]}')]
sql = f'insert into spatial ("ID", "TESTPROPERTY") values (?, ST_GeomFromGeoJSON(?))'
cur.executemany(sql, [('11', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}')])
Traceback (most recent call last):
  File "<pyshell#110>", line 1, in <module>
    cur.executemany(sql, [('11', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}')])
hdbcli.dbapi.ProgrammingError: (316, 'wrong number of arguments in function invocation: st_geomfromgeojson() has wrong number of arguments: line 1 col 55 (at pos 54)')
sql = f'insert into spatial ("ID", "TESTPROPERTY") values (?, ST_GeomFromGeoJSON(?, ?))'
cur.executemany(sql, [('12', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}'), 0])
Traceback (most recent call last):
  File "<pyshell#112>", line 1, in <module>
    cur.executemany(sql, [('12', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}'), 0])
hdbcli.dbapi.ProgrammingError: (0, 'A tuple, a list or a dictionary is allowed in the sequence(tuple, list) of parameters.')
cur.executemany(sql, [('12', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}', 0)])
(1,)
cur.executemany(sql, [('13', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}', 4326)])
Traceback (most recent call last):
  File "<pyshell#114>", line 1, in <module>
    cur.executemany(sql, [('13', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}', 4326)])
hdbcli.dbapi.Error: (669, "spatial error: exception 1620501: The geometry's SRID (4326) does not match the column's SRID (0) at column 'TESTPROPERTY'\n")
cur.executemany(sql, [('14', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}', null)])
Traceback (most recent call last):
  File "<pyshell#115>", line 1, in <module>
    cur.executemany(sql, [('14', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}', null)])
NameError: name 'null' is not defined
cur.execute('drop table spatial')
True
cur.execute('create table spatial ( "ID" NVARCHAR(36) PRIMARY KEY, "TESTPROPERTY" ST_GEOMETRY(4326) )')
True
cur.executemany(sql, [('1', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}', 0)])
Traceback (most recent call last):
  File "<pyshell#118>", line 1, in <module>
    cur.executemany(sql, [('1', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}', 0)])
hdbcli.dbapi.Error: (669, "spatial error: exception 1620501: The geometry's SRID (0) does not match the column's SRID (4326) at column 'TESTPROPERTY'\n")
cur.executemany(sql, [('1', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}', 4326)])
(1,)
cur.execute('select * from spatial')
True
cur.execute('select ID, TESTPROPERTY.ST_AsGeoJSON() from spatial')
True
print(cur.fetchall())
[('1', '{"type": "LineString", "coordinates": [[1.98787765, 2], [5, 7]]}')]
