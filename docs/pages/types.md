---
layout: default
title: "Data Types"
nav_order: 4
---

For examples for the usage of different data types see the [datatypes test folder](../../tests/packages/datatypes/).

| CDS Type | Arguments / Remarks	| Example Value | HANA SQL Type |
| ---  |  --- |  --- |  --- | 
| UUID | an opaque 36-characters string <sup>(1)</sup> | "be071623-8699-4106-b6fa-8e3cb04c261e" | NVARCHAR(36) |
| Boolean |  | true |  BOOLEAN |
| Integer |  | 1337 | INTEGER |
| Integer64 |  | 1337 | BIGINT |
| Decimal | ( precision, scale ) <sup>(2)</sup> | 15.2 | DECIMAL |
| Double |  | 15.2 | DOUBLE |
| Date |  | "2021-06-27" | DATE |
| Time |  | "07:59:59" | TIME |
| DateTime | sec precision | "2021-06-27T14:52:23Z" | SECONDDATE |
| Timestamp | 0.1 µs precision <sup>(3)</sup> | "2021-06-27T14:52:23.123Z" | TIMESTAMP |
| String | ( length ) <sup>(4)</sup> | "hello world" | NVARCHAR |
| Binary | ( length ) <sup>(4)</sup> | "w/VIQA==" <sup>(7) | VARBINARY |
| LargeBinary |  | "w/VIQA==" <sup>(7)</sup> | BLOB |
| LargeString |  | "hello world" | NCLOB |
| hana.SMALLINT |  | 256 | SMALLINT | 
| hana.TINYINT |  | 255 | TINYINT | 
| hana.SMALLDECIMAL | | 3.1 | SMALLDECIMAL | 
| hana.REAL | | 3.1 | REAL | 
| hana.VARCHAR | ( length ) | "hello world"  | VARCHAR |
| hana.CLOB | |  "hello world" | CLOB |
| hana.BINARY | ( length )  | "w/VIQA==" <sup>(7)</sup> | BINARY |
| hana.ST_POINT | ( srid ) <sup>(5)</sup> | [30.0, 10.0] |  ST_POINT |
| hana.ST_GEOMETRY | ( srid ) <sup>(5)</sup> |{"type": "Polygon", "coordinates": [[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]]}<sup>(6)</sup> |  ST_GEOMETRY |
| String  | with annotation @esh.type.text | "hello world"  | SHORTTEXT |
| LargeString | with annotation @esh.type.text |  "hello world" | TEXT |
| LargeBinary | with annotation @esh.type.text | "w/VIQA==" <sup>(7) | BINTEXT |

Remarks
<sup>(1)</sup> At runtime, UUIDs are treated as opaque values and are, for example, not converted to lower case on input. UUIDs generated in the application are [RFC 4122](https://tools.ietf.org/html/rfc4122)-compliant. See [Don’t Interpret UUIDs!](https://cap.cloud.sap/docs/guides/domain-models#dont-interpret-uuids) for details.

<sup>(2)</sup> precision is the number of total digits (the sum of whole digits and fractional digits). Scale is the number of fractional digits. If a property is defined as Decimal(5, 4) for example, the numbers 3.14, 3.1415, 3.141592 are stored in the column as 3.1400, 3.1415, 3.1415, retaining the specified precision(5) and scale(4).

<sup>(3)</sup> Up to 7 digits of fractional seconds; if a data is given with higher precision truncation may occur

<sup>(4)</sup> Argument length is optional → use options cds.cdsc.defaultStringLength and cds.cdsc.defaultBinaryLength to control the project-specific default length used for OData and SQL backends. If not set, the global default length 5000 is used for SQL backends.

<sup>(5)</sup> Optional, default: 4326

<sup>(6)</sup> In [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON)-format. See also IETF-[RFC 7946](https://datatracker.ietf.org/doc/html/rfc7946)

<sup>(7)</sup> string with base-64 encoded binary information

<sup>sources</sup> consolidated information from [CDS types](https://cap.cloud.sap/docs/cds/types), [HANA types](https://cap.cloud.sap/docs/advanced/hana#hana-types), [HANA numeric data types](https://help.sap.com/docs/HANA_SERVICE_CF/7c78579ce9b14a669c1f3295b0d8ca16/4ee2f261e9c44003807d08ccc2e249ac.html?locale=en-US), [SAP HANA SQL reference guide](https://help.sap.com/docs/HANA_SERVICE_CF/7c78579ce9b14a669c1f3295b0d8ca16/20a1569875191014b507cf392724b7eb.html?locale=en-US)
