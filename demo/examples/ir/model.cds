using {sap.esh.Identifier} from '../../../model/esh';


entity RelTypeCode : Identifier {
    description : String(256)
}


entity Cases : Identifier {
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


entity Person : Identifier {
    firstName         : String;
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
    relCases          : Association to RelCasesPerson;
    @sap.esh.isVirtual
    relObject         : Association to RelPersonObject;
    @sap.esh.isVirtual
    relActivity       : Association to RelActivityPerson;
    @sap.esh.isVirtual
    relLocation       : Association to RelLocationPerson;
    @sap.esh.isVirtual
    relIncident       : Association to RelIncidentPerson;
    @sap.esh.isVirtual
    relLeads          : Association to RelLeadsPerson;
}


entity RelCasesPerson : Identifier {
    cases       : Association to Cases;
    person      : Association to Person;
    relTypeCode : Association to RelTypeCode;
}

entity Object : Identifier {
    entityDesc     : String;
    origin         : String;
    objectCategory : String;
    @sap.esh.isVirtual
    relCases       : Association to RelCasesObject;
    @sap.esh.isVirtual
    relPerson      : Association to RelPersonObject;
    @sap.esh.isVirtual
    relActivity    : Association to RelActivityObject;
    @sap.esh.isVirtual
    relLocation    : Association to RelObjectLocation;
}

entity RelCasesObject : Identifier {
    cases       : Association to Cases;
    object      : Association to Object;
    relTypeCode : Association to RelTypeCode;
}

entity RelPersonObject : Identifier {
    person      : Association to Person;
    object      : Association to Object;
    relTypeCode : Association to RelTypeCode;
}

entity Activity : Identifier {
    entityDesc        : String;
    entityTime        : String;
    origin            : String;
    location          : String;
    activityStartDate : Date;
    activityEndDate   : Date;
    @sap.esh.isVirtual
    relCases          : Association to RelCasesActivity;
    @sap.esh.isVirtual
    relPerson         : Association to RelActivityPerson;
    @sap.esh.isVirtual
    relObject         : Association to RelActivityObject;
}

entity RelCasesActivity : Identifier {
    cases       : Association to Cases;
    activity    : Association to Activity;
    relTypeCode : Association to RelTypeCode;
}

entity RelActivityPerson : Identifier {
    activity    : Association to Activity;
    person      : Association to Person;
    relTypeCode : Association to RelTypeCode;
}


entity RelActivityObject : Identifier {
    activity    : Association to Activity;
    object      : Association to Object;
    relTypeCode : Association to RelTypeCode;
}

entity Location : Identifier {
    entityDesc       : String;
    position         : hana.ST_POINT(4326); //Position
    locationCategory : String;
    houseNumber      : String;
    street           : String;
    city             : String;
    postalCode       : String;
    country          : String;
    locationType     : String;
    @sap.esh.isVirtual
    relObject        : Association to RelObjectLocation;
    @sap.esh.isVirtual
    relPerson        : Association to RelLocationPerson;
    @sap.esh.isVirtual
    relIncidents     : Association to RelIncidentLocation;
}


entity RelObjectLocation : Identifier {
    object      : Association to Object;
    location    : Association to Location;
    relTypeCode : Association to RelTypeCode;
}

entity RelLocationPerson : Identifier {
    location    : Association to Location;
    person      : Association to Person;
    relTypeCode : Association to RelTypeCode;
}

entity Incidents : Identifier {
    entityDesc  : String;
    entityTime  : String;
    position    : hana.ST_POINT; //Position
    location    : String;
    @sap.esh.isVirtual
    relLocation : Association to RelIncidentLocation;
    @sap.esh.isVirtual
    relPerson   : Association to RelIncidentPerson;
    @sap.esh.isVirtual
    relCases    : Association to RelCasesIncident;
}

entity RelIncidentLocation : Identifier {
    incident    : Association to Incidents;
    location    : Association to Location;
    relTypeCode : Association to RelTypeCode;
}

entity RelIncidentPerson : Identifier {
    incident    : Association to Incidents;
    person      : Association to Person;
    relTypeCode : Association to RelTypeCode;

}

entity RelCasesIncident : Identifier {
    cases       : Association to Cases;
    incident    : Association to Incidents;
    relTypeCode : Association to RelTypeCode;
}

entity Leads : Identifier {
    entityDesc  : String;
    entityTime  : String;
    leadSummary : String;
    leadStatus  : String;
    @sap.esh.isVirtual
    relCases    : Association to RelLeadsCases;
    @sap.esh.isVirtual
    relPerson   : Association to RelLeadsPerson;
}

entity RelLeadsCases : Identifier {
    lead        : Association to Leads;
    cases       : Association to Cases;
    relTypeCode : Association to RelTypeCode;
}

entity RelLeadsPerson : Identifier {
    lead        : Association to Leads;
    person      : Association to Person;
    relTypeCode : Association to RelTypeCode;
}
