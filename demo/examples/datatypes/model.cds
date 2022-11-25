@EnterpriseSearch.enabled
@EndUserText.Label : 'Datatype'
@EnterpriseSearchHana.passThroughAllAnnotations
entity Datatype {
    key id : UUID;
    @UI.Identification                           : [{Position : 10 }]
    @EndUserText.Label                           : 'Binary'
    testBinary                         : Binary(200);
    @UI.Identification                           : [{Position : 20 }]
    @EndUserText.Label                           : 'Boolean'
    testBoolean                        : Boolean;
    @UI.Identification                           : [{Position : 30 }]
    @EndUserText.Label                           : 'Date'
    testDate                           : Date;
    @UI.Identification                           : [{Position : 40 }]
    @EndUserText.Label                           : 'Date Time'
    testDateTime                       : DateTime;
    @UI.Identification                           : [{Position : 50}]
    @EndUserText.Label                           : 'Decimal'
    testDecimal                        : Decimal(20, 10);
    @UI.Identification                           : [{Position : 60}]
    @EndUserText.Label                           : 'Double'
    testDouble                         : Double;
    @UI.Identification                           : [{Position : 70}]
    @EndUserText.Label                           : 'Integer'
    testInt                            : Integer;
    @UI.Identification                           : [{Position : 80}]
    @EndUserText.Label                           : 'Integer 64'
    testInt64                          : Integer64;
    @UI.Identification                           : [{Position : 90}]
    @EndUserText.Label                           : 'Large Binary'
    testLargeBinary                    : LargeBinary;
    @UI.Identification                           : [{Position : 120}]
    @EndUserText.Label                           : 'Large String'
    @esh.type.text
    testLargeString                    : LargeString;
    @UI.Identification                           : [{Position : 130}]
    @EndUserText.Label                           : 'String'
    testString                         : String;
    // @UI.Identification                           : [{Position : 120}]
    testTime                           : Time;
    @UI.Identification                           : [{Position : 100}]
    @EndUserText.Label                           : 'Timestamp'
    testTimeStamp                      : Timestamp;
    @UI.Identification                           : [{Position : 110}]
    @EndUserText.Label                           : 'UUID'
    testUUID                           : UUID;
}

@EnterpriseSearch.enabled
@EndUserText.Label : 'HANA_Datatype'
@EnterpriseSearchHana.passThroughAllAnnotations
entity HanaDatatype{
    key id                                 : UUID;
    @UI.Identification                           : [{Position : 10 }]    
    @EndUserText.Label                           : 'HANA Binary'
    testHanaBinary                     : hana.BINARY(200);
    @UI.Identification                           : [{Position : 20}]
    @EndUserText.Label                           : 'HANA Large binary'
    @esh.type.text
    testHanaBintext                    : LargeBinary;
    @UI.Identification                           : [{Position : 30}]
    @EndUserText.Label                           : 'HANA Clob'
    testHanaClob                       : hana.CLOB;
    @UI.Identification                           : [{Position : 40}]
    @EndUserText.Label                           : 'HANA Real'
    testHanaReal                       : hana.REAL;
    @UI.Identification                           : [{Position : 50}]
    @EndUserText.Label                           : 'HANA Short text'
    @esh.type.text
    testHanaShorttext                  : String;
    @UI.Identification                           : [{Position : 60}]
    @EndUserText.Label                           : 'HANA Small decimal'
    testHanaSmalldecimal               : hana.SMALLDECIMAL;
    @UI.Identification                           : [{Position : 70}]
    @EndUserText.Label                           : 'HANA Small integer'
    testHanaSmallint                   : hana.SMALLINT;
    // @UI.Identification                           : [{Position : 40}]
    @EndUserText.Label                           : 'HANA Geometry'
    testHanaSt_geometry                : hana.ST_GEOMETRY(4326);
    // @UI.Identification                           : [{Position : 45}]
    @EndUserText.Label                           : 'HANA Geometry circular string'
    testHanaSt_geometry_circularstring : hana.ST_GEOMETRY(0);
    // @UI.Identification                           : [{Position : 100}]
    @EndUserText.Label                           : 'HANA Point'
    testHanaSt_point                   : hana.ST_POINT(4326);
    // @UI.Identification                           : [{Position : 110}]
    @EndUserText.Label                           : 'HANA Text'
    @esh.type.text
    testHanaText                       : LargeString;
    @UI.Identification                           : [{Position : 80}]
    @EndUserText.Label                           : 'HANA Tiny integer'
    testHanaTinyint                    : hana.TINYINT;
    @UI.Identification                           : [{Position : 90}]
    @EndUserText.Label                           : 'HANA Var character'
    testHanaVarchar                    : hana.VARCHAR;
    
}