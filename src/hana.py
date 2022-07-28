"""Conversions from and to binary format"""
import struct
import json

def geojson_to_bin(geojson):
    match geojson['type']:
        case 'Point':
            return b'\x01\x01\x00\x00\x00'\
                + struct.pack("d", geojson['coordinates'][0])\
                + struct.pack("d", geojson['coordinates'][1])
        case _:
            raise NotImplementedError
