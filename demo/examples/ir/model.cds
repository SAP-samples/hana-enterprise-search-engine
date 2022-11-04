using {sap.esh.Identifier} from '../../../model/esh';

@EnterpriseSearch.enabled : false
entity RelTypeCode : Identifier {
    description : String(256)
}

@Search.defaultSearchElement : true
entity Cases : Identifier {
    @Search.defaultSearchElement : true
    @sap.esh.isText
    entityDesc    : String;
    entityTime    : String;
    caseType      : String;
    priority      : String;
    status        : String;
    caseCategory  : String;
    caseStartDate : Date;
    caseStartTime : String;
    caseEndDate   : Date;
    caseEndTime   : String;
    @sap.esh.isText
    caseSummary   : String;
    @sap.esh.isVirtual
    relPerson     : Association to RelCasesPerson;
    @sap.esh.isVirtual
    relObject     : Association to RelCasesObject;
    @sap.esh.isVirtual
    relActivity   : Association to RelCasesActivity;
    @sap.esh.isVirtual
    relIncident   : Association to RelCasesIncident;
    @sap.esh.isVirtual
    relLeads      : Association to RelLeadsCases;
}

@EnterpriseSearch.enabled : true
entity Person : Identifier {
    @Search.defaultSearchElement : true
    firstName         : String;
    @Search.defaultSearchElement : true
    lastName          : String;
    dob               : String;
    age               : Integer;
    complexion        : String;
    ethnicity         : String;
    height            : Integer;
    gender            : String;
    countryOfBirth    : String;
    country           : String;
    placeOfBirth      : String;
    nationality       : String;
    secondNationality : String;
    additionalRemarks : String;
    @sap.esh.isVirtual
    relCases          : Association to many RelCasesPerson;
    @sap.esh.isVirtual
    relObject         : Association to many RelPersonObject;
    @sap.esh.isVirtual
    relActivity       : Association to many RelActivityPerson;
    @sap.esh.isVirtual
    relLocation       : Association to many RelLocationPerson;
    @sap.esh.isVirtual
    relIncident       : Association to many RelIncidentPerson;
    @sap.esh.isVirtual
    relLeads          : Association to many RelLeadsPerson;
}

@EnterpriseSearch.enabled : false
entity RelCasesPerson : Identifier {
    cases       : Association to Cases;
    person      : Association to Person;
    relTypeCode : Association to RelTypeCode;
}

entity Object : Identifier {
    @sap.esh.isText
    entityDesc     : String;
    origin         : String;
    objectCategory : String;
    @sap.esh.isVirtual
    relCases       : Association to RelCasesObject;
    @sap.esh.isVirtual
    relPerson      : Association to many RelPersonObject;
    @sap.esh.isVirtual
    relActivity    : Association to RelActivityObject;
    @sap.esh.isVirtual
    relLocation    : Association to RelObjectLocation;
}

@EnterpriseSearch.enabled : false
entity RelCasesObject : Identifier {
    cases       : Association to Cases;
    object      : Association to Object;
    relTypeCode : Association to RelTypeCode;
}

@EnterpriseSearch.enabled : false
entity RelPersonObject : Identifier {
    person      : Association to many Person;
    object      : Association to many Object;
    relTypeCode : Association to RelTypeCode;
}

entity Activity : Identifier {
    @sap.esh.isText
    entityDesc        : String;
    entityTime        : String;
    origin            : String;
    location          : String;
    activityStartDate : Date;
    activityEndDate   : Date;
    @sap.esh.isVirtual
    relCases          : Association to RelCasesActivity;
    @sap.esh.isVirtual
    relPerson         : Association to many RelActivityPerson;
    @sap.esh.isVirtual
    relObject         : Association to RelActivityObject;
}

@EnterpriseSearch.enabled : false
entity RelCasesActivity : Identifier {
    cases       : Association to Cases;
    activity    : Association to Activity;
    relTypeCode : Association to RelTypeCode;
}

@EnterpriseSearch.enabled : false
entity RelActivityPerson : Identifier {
    activity    : Association to Activity;
    person      : Association to Person;
    relTypeCode : Association to RelTypeCode;
}

@EnterpriseSearch.enabled : false
entity RelActivityObject : Identifier {
    activity    : Association to Activity;
    object      : Association to Object;
    relTypeCode : Association to RelTypeCode;
}

@EnterpriseSearch.enabled : true
entity Location : Identifier {
    @sap.esh.isText
    entityDesc       : String;
    position         : hana.ST_POINT(4326); //Position
    locationCategory : String;
    houseNumber      : String;
    street           : String;
    city             : String;
    @Search.defaultSearchElement : true
    postalCode       : String;
    country          : String;
    locationType     : String;
    @sap.esh.isVirtual
    relObject        : Association to RelObjectLocation;
    @sap.esh.isVirtual
    relPerson        : Association to many RelLocationPerson;
    @sap.esh.isVirtual
    relIncidents     : Association to RelIncidentLocation;
}

@EnterpriseSearch.enabled : false
entity RelObjectLocation : Identifier {
    object      : Association to Object;
    location    : Association to Location;
    relTypeCode : Association to RelTypeCode;
}

@EnterpriseSearch.enabled : false
entity RelLocationPerson : Identifier {
    location    : Association to Location;
    person      : Association to Person;
    relTypeCode : Association to RelTypeCode;
}

entity Incidents : Identifier {
    @sap.esh.isText
    entityDesc  : String;
    entityTime  : String;
    position    : hana.ST_POINT; //Position
    @sap.esh.isText
    location    : String;
    @sap.esh.isVirtual
    relLocation : Association to RelIncidentLocation;
    @sap.esh.isVirtual
    relPerson   : Association to many RelIncidentPerson;
    @sap.esh.isVirtual
    relCases    : Association to RelCasesIncident;
}

@EnterpriseSearch.enabled : false
entity RelIncidentLocation : Identifier {
    incident    : Association to Incidents;
    location    : Association to Location;
    relTypeCode : Association to RelTypeCode;
}

@EnterpriseSearch.enabled : false
entity RelIncidentPerson : Identifier {
    incident    : Association to Incidents;
    person      : Association to Person;
    relTypeCode : Association to RelTypeCode;

}

@EnterpriseSearch.enabled : false
entity RelCasesIncident : Identifier {
    cases       : Association to Cases;
    incident    : Association to Incidents;
    relTypeCode : Association to RelTypeCode;
}

entity Leads : Identifier {
    @sap.esh.isText
    entityDesc  : String;
    entityTime  : String;
    @sap.esh.isText
    leadSummary : String;
    leadStatus  : String;
    @sap.esh.isVirtual
    relCases    : Association to RelLeadsCases;
    @sap.esh.isVirtual
    relPerson   : Association to many RelLeadsPerson;
}

@EnterpriseSearch.enabled : false
entity RelLeadsCases : Identifier {
    lead        : Association to Leads;
    cases       : Association to Cases;
    relTypeCode : Association to RelTypeCode;
}

@EnterpriseSearch.enabled : false
entity RelLeadsPerson : Identifier {
    lead        : Association to Leads;
    person      : Association to Person;
    relTypeCode : Association to RelTypeCode;
}
