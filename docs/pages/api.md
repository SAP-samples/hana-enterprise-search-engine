---
layout: default
title: "APIs"
nav_order: 3
---

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

# Tenants

## Create Tenant

Creates a new tenant. The provided tenant-id needs to be alphanumeric and has a maximal length of 50 characters.

### API Maturity

In development, API changes and bugs expected.

### URL

```http
POST /v1/tenant/{tenant-id}
```

### Example Request

```http
POST {host}:{port}/v1/tenant/hp74CDXIUsikzsuL478ZLroYESIYKvDS
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
{
  "detail": "Tenant 'hp74CDXIUsikzsuL478ZLroYESIYKvDS' successfully created"
}
```

An error is returned when trying to create a tenent which already exists.

### Example Response - Error

```html
HTTP Status Code: 422
content-type: application/json
```

```json
{
  "detail": "Tenant creation failed. Tennant id 'hp74CDXIUsikzsuL478ZLroYESIYKvDS' already exists"
}
```

## Get All Tenants

Returns all tenants.

### API Maturity

In development, API changes and bugs expected.

### URL

```http
GET /v1/tenant
```

### Example Request

```http
GET {host}:{port}/v1/tenant
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
[
  {
    "name": "hp74CDXIUsikzsuL478ZLroYESIYKvDS",
    "createdAt": "2022-11-02T14:09:32.425000"
  }
]
```

## Delete Tenant

Deletes an existing tenant.

Attention: This includes deletion of all data of this tenant as well.

### API Maturity

In development, API changes and bugs expected.

### URL

```http
DELETE /v1/tenant/{tenant-id}
```

### Example Request

```http
DELETE {host}:{port}/v1/tenant/hp74CDXIUsikzsuL478ZLroYESIYKvDS
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
{
  "detail": "Tenant 'hp74CDXIUsikzsuL478ZLroYESIYKvDS' successfully deleted"
}
```

An error is returned when trying to delete a tenent which does not exist.

### Example Response - Error

```html
HTTP Status Code: 404
content-type: application/json
```

```json
{
  "detail": "Tenant deletion failed. Tennant id 'hp74CDXIUsikzsuL478ZLroYESIYKvDS' does not exist"
}
```

# Data Model

## Data Model Consistency Check

Checks the consisteny of the passed data model cson.

This check is executed without creation of any artefacts on the database. This is an optional step which is useful during development. The optional parameter simulate is used to indicate this mode.

### API Maturity

In development, API changes and bugs expected.

### URL

```http
POST /v1/deploy/{tenant-id}
```

### Example Request

```http
POST {host}:{port}/v1/deploy/hp74CDXIUsikzsuL478ZLroYESIYKvDS?simulate=True
Content-Type: application/json
```

```json
{
  "namespace": "example",
  "definitions": {
    "example.Name": {
      "kind": "type",
      "type": "cds.String",
      "length": 256
    },
    "example.Identifier": {
      "kind": "aspect",
      "elements": {
        "id": {
          "key": true,
          "type": "cds.UUID"
        }
      }
    },
    "example.Person": {
      "kind": "entity",
      "includes": [
        "example.Identifier"
      ],
      "elements": {
        "id": {
          "key": true,
          "type": "cds.UUID"
        },
        "firstName": {
          "type": "example.Name",
          "length": 256
        },
        "lastName": {
          "type": "example.Name",
          "length": 256
        }
      }
    }
  },
  "$version": "2.0"
}
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
{
  "detail": "Model is consistent"
}
```

An error is returned if the cson is invalid.

### URL

```http
POST /v1/deploy/{tenant-id}
```

### Example Request

```http
POST {host}:{port}/v1/deploy/hp74CDXIUsikzsuL478ZLroYESIYKvDS?simulate=True
Content-Type: application/json
```

```json
{
  "namespace": "example",
  "definitions": {
    "example.Name": {
      "kind": "type",
      "type": "cds.String",
      "length": 256
    },
    "example.Identifier": {
      "kind": "aspect",
      "elements": {
        "id": {
          "key": true,
          "type": "cds.UUID"
        }
      }
    },
    "example.Person": {
      "kind": "entity",
      "includes": [
        "example.Identifier"
      ],
      "elements": {
        "id": {},
        "firstName": {},
        "lastName": {}
      }
    }
  },
  "$version": "2.0"
}
```

### Example Response - Error

```html
HTTP Status Code: 422
content-type: application/json
```

```json
{
  "detail": [
    {
      "loc": [
        "definitions",
        "example.Person",
        "elements"
      ],
      "msg": "an entity must have exactly one key-element"
    },
    {
      "loc": [
        "definitions",
        "example.Person",
        "elements",
        "id"
      ],
      "msg": "empty"
    },
    {
      "loc": [
        "definitions",
        "example.Person",
        "elements",
        "firstName"
      ],
      "msg": "empty"
    },
    {
      "loc": [
        "definitions",
        "example.Person",
        "elements",
        "lastName"
      ],
      "msg": "empty"
    }
  ]
}
```

## Deploy Data Model

Deploys the data model which includes the creation of tables, views and default search configuration on the database.

### API Maturity

In development, API changes and bugs expected.

### URL

```http
POST /v1/deploy/{tenant-id}
```

### Example Request

```http
POST {host}:{port}/v1/deploy/hp74CDXIUsikzsuL478ZLroYESIYKvDS
Content-Type: application/json
```

```json
{
  "namespace": "example",
  "definitions": {
    "example.Name": {
      "kind": "type",
      "type": "cds.String",
      "length": 256
    },
    "example.Identifier": {
      "kind": "aspect",
      "elements": {
        "id": {
          "key": true,
          "type": "cds.UUID"
        }
      }
    },
    "example.Person": {
      "kind": "entity",
      "includes": [
        "example.Identifier"
      ],
      "elements": {
        "id": {
          "key": true,
          "type": "cds.UUID"
        },
        "firstName": {
          "type": "example.Name",
          "length": 256
        },
        "lastName": {
          "type": "example.Name",
          "length": 256
        }
      }
    }
  },
  "$version": "2.0"
}
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
{
  "detail": "Model successfully deployed"
}
```

An error is returned if the cson is invalid. This is the same error which is returned in the simulation mode.

### URL

```http
POST /v1/deploy/{tenant-id}
```

### Example Request

```http
POST {host}:{port}/v1/deploy/hp74CDXIUsikzsuL478ZLroYESIYKvDS
Content-Type: application/json
```

```json
{
  "namespace": "example",
  "definitions": {
    "example.Name": {
      "kind": "type",
      "type": "cds.String",
      "length": 256
    },
    "example.Identifier": {
      "kind": "aspect",
      "elements": {
        "id": {
          "key": true,
          "type": "cds.UUID"
        }
      }
    },
    "example.Person": {
      "kind": "entity",
      "includes": [
        "example.Identifier"
      ],
      "elements": {
        "id": {},
        "firstName": {},
        "lastName": {}
      }
    }
  },
  "$version": "2.0"
}
```

### Example Response - Error

```html
HTTP Status Code: 422
content-type: application/json
```

```json
{
  "detail": [
    {
      "loc": [
        "definitions",
        "example.Person",
        "elements"
      ],
      "msg": "an entity must have exactly one key-element"
    },
    {
      "loc": [
        "definitions",
        "example.Person",
        "elements",
        "id"
      ],
      "msg": "empty"
    },
    {
      "loc": [
        "definitions",
        "example.Person",
        "elements",
        "firstName"
      ],
      "msg": "empty"
    },
    {
      "loc": [
        "definitions",
        "example.Person",
        "elements",
        "lastName"
      ],
      "msg": "empty"
    }
  ]
}
```

# Data

## Load Data

The input is a json with a dictionary of object types containing a list of objects of this object type. The structure of the passed objects need to correspond to the data model deployed before.

The response is a json with a dictionary of object types containing a list of object ids which list-index corresponds to the input-list.

### API Maturity

In development, API changes and bugs expected.

### URL

```http
POST /v1/data/{tenant-id}
```

### Example Request

```http
POST {host}:{port}/v1/data/hp74CDXIUsikzsuL478ZLroYESIYKvDS
Content-Type: application/json
```

```json
{
  "example.Person": [
    {
      "firstName": "John",
      "lastName": "Doe"
    },
    {
      "lastName": "Doe",
      "firstName": "Jane"
    }
  ]
}
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
{
  "example.Person": [
    {
      "id": "98ab4efb-5aaf-11ed-a56d-98fa9b3c3838"
    },
    {
      "id": "98ab4efc-5aaf-11ed-b9ee-98fa9b3c3838"
    }
  ]
}
```

An error is returned if the tenant does not exist.

### Example Response - Error

```html
HTTP Status Code: 404
content-type: application/json
```

```json
{
  "detail": "Tennant id 'hp74CDXIUsikzsuL478ZLroYESIYKvDS' does not exist"
}
```

## Read Data

The input is a json with a dictionary of object types containing a list of objects ids. The format corresponds exactly with the result of load data.

### API Maturity

In development, API changes and bugs expected.

### URL

```http
POST /v1/read/{tenant-id}
```

### Example Request

```http
POST {host}:{port}/v1/read/hp74CDXIUsikzsuL478ZLroYESIYKvDS
Content-Type: application/json
```

```json
{
  "example.Person": [
    {
      "id": "99b8c203-5aaf-11ed-9bd3-98fa9b3c3838"
    },
    {
      "id": "99b8c204-5aaf-11ed-a92f-98fa9b3c3838"
    }
  ]
}
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
{
  "example.Person": [
    {
      "id": "99b8c203-5aaf-11ed-9bd3-98fa9b3c3838",
      "firstName": "John",
      "lastName": "Doe"
    },
    {
      "id": "99b8c204-5aaf-11ed-a92f-98fa9b3c3838",
      "firstName": "Jane",
      "lastName": "Doe"
    }
  ]
}
```

## Delete Data

The input is a json with a dictionary of object types containing a list of objects ids. The format corresponds exactly with the result of load data or read data.

### API Maturity

In development, API changes and bugs expected.

### URL

```http
DELETE /v1/data/{tenant-id}
```

### Example Request

```http
DELETE {host}:{port}/v1/data/hp74CDXIUsikzsuL478ZLroYESIYKvDS
Content-Type: application/json
```

```json
{
  "example.Person": [
    {
      "id": "99b8c203-5aaf-11ed-9bd3-98fa9b3c3838"
    },
    {
      "id": "99b8c204-5aaf-11ed-a92f-98fa9b3c3838"
    }
  ]
}
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
null
```

# Search

## Enterprise Search using OData-Format

More information about enterprise search requests can be found in the section [federated Full-Text Search with Built-In Procedure sys.esh_search()](https://help.sap.com/docs/SAP_HANA_PLATFORM/691cb949c1034198800afde3e5be6570/bff7cffd72074c6e80d4c21279f5a521.html?locale=en-US) of the HANA search developer guide.

### API Maturity

Used in production since years.

### URL

```http
GET /v1/search/{tenant-id}/{esh-version}/
```

### Example Request

```http
GET {host}:{port}/v1/search/hp74CDXIUsikzsuL478ZLroYESIYKvDS/latest/$all?$top=10&$count=true&$apply=filter(Search.search(query='SCOPE:EXAMPLEPERSON%20John%20Doe'))&whyfound=true&$select=FIRSTNAME,LASTNAME&$orderby=LASTNAME%20ASC&estimate=true&wherefound=true
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
{
  "value": [
    {
      "@com.sap.vocabularies.Search.v1.Ranking": 1,
      "@com.sap.vocabularies.Search.v1.WhereFound": "<TERM>Doe</TERM><FOUND>LASTNAME</FOUND><TERM>John</TERM><FOUND>FIRSTNAME</FOUND>",
      "@com.sap.vocabularies.Search.v1.WhyFound": {
        "FIRSTNAME": [
          "<b>John</b>"
        ],
        "LASTNAME": [
          "<b>Doe</b>"
        ]
      },
      "@odata.context": "$metadata#EXAMPLEPERSON",
      "FIRSTNAME": "John",
      "LASTNAME": "Doe"
    }
  ],
  "@odata.count": 1,
  "@com.sap.vocabularies.Search.v1.ResponseTime": 0.193131998,
  "@com.sap.vocabularies.Search.v1.SearchTime": 0.0894810035,
  "@com.sap.vocabularies.Search.v1.SearchStatistics": {
    "ConnectorStatistics": [
      {
        "OdataID": "EXAMPLEPERSON",
        "StatusCode": 200,
        "@com.sap.vocabularies.Search.v1.SearchTime": 0.0894810035,
        "@com.sap.vocabularies.Search.v1.CPUTime": 0.0899429991
      }
    ],
    "StatusCode": 200
  }
}
```

The standard OData $metadata call is also available.

It returns the metadata information of the model in XML-format.

### URL

```http
GET /v1/search/{tenant-id}/{esh-version}/$metadata
```

### Example Request

```http
GET {host}:{port}/v1/search/hp74CDXIUsikzsuL478ZLroYESIYKvDS/latest/$metadata
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/xml
```

```xml
<?xml version="1.0" ?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="esh">
      <EntityType Name="EXAMPLEPERSONType">
        <Annotation Term="Search.searchable" Bool="true"/>
        <Annotation Term="EnterpriseSearch.enabled" Bool="true"/>
        <Annotation Term="EnterpriseSearch.hidden" Bool="false"/>
        <Key>
          <PropertyRef Name="ID"/>
        </Key>
        <Property Name="FIRSTNAME" Type="Edm.String" MaxLength="256">
          <Annotation Term="Search.defaultSearchElement" Bool="true"/>
          <Annotation Term="EnterpriseSearchHana.isSortable" Bool="true"/>
          <Annotation Term="UI.identification">
            <Collection>
              <Record>
                <PropertyValue Property="position" Int="10"/>
              </Record>
            </Collection>
          </Annotation>
          <Annotation Term="SAP.Common.Label" String="FIRSTNAME"/>
        </Property>
        <Property Name="ID" Type="Edm.String" MaxLength="36">
          <Annotation Term="EnterpriseSearch.key" Bool="true"/>
          <Annotation Term="EnterpriseSearchHana.isSortable" Bool="true"/>
          <Annotation Term="UI.hidden" Bool="true"/>
          <Annotation Term="SAP.Common.Label" String="ID"/>
        </Property>
        <Property Name="LASTNAME" Type="Edm.String" MaxLength="256">
          <Annotation Term="Search.defaultSearchElement" Bool="true"/>
          <Annotation Term="EnterpriseSearchHana.isSortable" Bool="true"/>
          <Annotation Term="UI.identification">
            <Collection>
              <Record>
                <PropertyValue Property="position" Int="20"/>
              </Record>
            </Collection>
          </Annotation>
          <Annotation Term="SAP.Common.Label" String="LASTNAME"/>
        </Property>
      </EntityType>
      <EntityContainer Name="esh">
        <EntitySet Name="EXAMPLEPERSON" EntityType="esh.EXAMPLEPERSONType">
          <Annotation String="EXAMPLEPERSON" Term="SAP.Common.Label"/>
        </EntitySet>
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>

```

## Enterprise Search using OData-Format (Bulk)

The request is a json-list of enterprise search requests as described above.

### API Maturity

Used in production since years.

### URL

```http
POST /v1/search/{tenant-id}/{esh-version}
```

### Example Request

```http
POST {host}:{port}/v1/search/hp74CDXIUsikzsuL478ZLroYESIYKvDS/latest
Content-Type: application/json
```

```json
[
  "$all?$top=10&$count=true&$apply=filter(Search.search(query='SCOPE:EXAMPLEPERSON John Doe'))&whyfound=true&$select=FIRSTNAME,LASTNAME&$orderby=LASTNAME ASC&estimate=true&wherefound=true",
  "$all?$top=10&$count=true&$apply=filter(Search.search(query='SCOPE:EXAMPLEPERSON AND (John AND Doe) AND aaa AND bbb'))&whyfound=true&$select=FIRSTNAME,LASTNAME&$orderby=LASTNAME ASC&estimate=true&wherefound=true"
]
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
[
  {
    "value": [
      {
        "@com.sap.vocabularies.Search.v1.Ranking": 1,
        "@com.sap.vocabularies.Search.v1.WhereFound": "<TERM>Doe</TERM><FOUND>LASTNAME</FOUND><TERM>John</TERM><FOUND>FIRSTNAME</FOUND>",
        "@com.sap.vocabularies.Search.v1.WhyFound": {
          "FIRSTNAME": [
            "<b>John</b>"
          ],
          "LASTNAME": [
            "<b>Doe</b>"
          ]
        },
        "@odata.context": "$metadata#EXAMPLEPERSON",
        "FIRSTNAME": "John",
        "LASTNAME": "Doe"
      }
    ],
    "@odata.count": 1,
    "@com.sap.vocabularies.Search.v1.ResponseTime": 0.127348005,
    "@com.sap.vocabularies.Search.v1.SearchTime": 0.0223789997,
    "@com.sap.vocabularies.Search.v1.SearchStatistics": {
      "ConnectorStatistics": [
        {
          "OdataID": "EXAMPLEPERSON",
          "StatusCode": 200,
          "@com.sap.vocabularies.Search.v1.SearchTime": 0.0223789997,
          "@com.sap.vocabularies.Search.v1.CPUTime": 0.0243660006
        }
      ],
      "StatusCode": 200
    }
  },
  {
    "value": [],
    "@odata.count": 0,
    "@com.sap.vocabularies.Search.v1.ResponseTime": 0.126947,
    "@com.sap.vocabularies.Search.v1.SearchTime": 0.0223699994,
    "@com.sap.vocabularies.Search.v1.SearchStatistics": {
      "ConnectorStatistics": [
        {
          "OdataID": "EXAMPLEPERSON",
          "StatusCode": 200,
          "@com.sap.vocabularies.Search.v1.SearchTime": 0.0223699994,
          "@com.sap.vocabularies.Search.v1.CPUTime": 0.0295979995
        }
      ],
      "StatusCode": 200
    }
  }
]
```

## OpenAPI API for search (Bulk)

This is a new API with additional features. It will evolve during the next months. Expect incompatible changes.

### API Maturity

Experimental, expect major changes / rework.

### URL

```http
POST /v1/query/{tenant-id}/{esh-version}
```

### Example Request

```http
POST {host}:{port}/v1/query/hp74CDXIUsikzsuL478ZLroYESIYKvDS/latest
Content-Type: application/json
```

```json
[
  {
    "type": "EshObject",
    "top": 10,
    "count": true,
    "scope": [
      "example.Person"
    ],
    "searchQueryFilter": {
      "type": "Expression",
      "operator": "AND",
      "items": [
        {
          "type": "StringValue",
          "value": "John"
        },
        {
          "type": "StringValue",
          "value": "Doe"
        }
      ]
    },
    "whyfound": true,
    "orderby": [
      {
        "type": "OrderBy",
        "key": {
          "type": "Property",
          "property": [
            "lastName"
          ]
        }
      }
    ],
    "estimate": true,
    "wherefound": true
  },
  {
    "type": "EshObject",
    "top": 10,
    "count": true,
    "scope": [
      "example.Person"
    ],
    "searchQueryFilter": {
      "type": "Expression",
      "operator": "AND",
      "items": [
        {
          "type": "Expression",
          "operator": "AND",
          "items": [
            {
              "type": "StringValue",
              "value": "John"
            },
            {
              "type": "StringValue",
              "value": "Doe"
            }
          ]
        },
        {
          "type": "StringValue",
          "value": "aaa"
        },
        {
          "type": "StringValue",
          "value": "bbb"
        }
      ]
    },
    "whyfound": true,
    "orderby": [
      {
        "type": "OrderBy",
        "key": {
          "type": "Property",
          "property": [
            "lastName"
          ]
        }
      }
    ],
    "estimate": true,
    "wherefound": true
  }
]
```

### Example Response - Success

```html
HTTP Status Code: 200
content-type: application/json
```

```json
[
  {
    "value": [
      {
        "@com.sap.vocabularies.Search.v1.Ranking": 1,
        "@com.sap.vocabularies.Search.v1.WhyFound": [
          {
            "found": [
              "firstName"
            ],
            "term": [
              "<b>John</b>"
            ]
          },
          {
            "found": [
              "lastName"
            ],
            "term": [
              "<b>Doe</b>"
            ]
          }
        ],
        "@type": "example.Person",
        "id": "99d4c249-5aaf-11ed-9710-98fa9b3c3838",
        "firstName": "John",
        "lastName": "Doe"
      }
    ],
    "@odata.count": 1
  },
  {
    "value": [],
    "@odata.count": 0
  }
]
```

## Enterprise Search UI

This request starts the standard SAP enterprise search UI.

### API Maturity

Used in production since years.

### URL

```http
GET /v1/searchui/{tenant-id}
```

### Example Request

```http
GET {host}:{port}/v1/searchui/hp74CDXIUsikzsuL478ZLroYESIYKvDS
```