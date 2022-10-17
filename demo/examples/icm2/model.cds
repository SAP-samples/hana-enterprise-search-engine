using {sap.esh.Identifier} from '../../../model/esh';

aspect CodeList : Identifier {
    code        : String(40);
    description : String(256);
}

entity CountryCode : CodeList {}
entity RelTypeCode : CodeList {}

// type Position {
//     coordinate  : hana.ST_POINT;
// }

entity Cases : Identifier {
    entityGuid    : UUID;
    entityId      : String;
    entityType    : String;
    entityDesc    : String;
    entityTime    : String;
    sourcen       : String;
    origin        : String;
    caseType      : String;
    priority      : String;
    status        : String;
    caseCategory  : String;
    caseOwner     : String;
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
    entityGuid        : UUID;
    entityId          : String;
    entityType        : String;
    sourcen           : String;
    origin            : String;
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
    familyName        : String;
    fullName          : String;
    birthName         : String;
    otherName         : String;
    placeOfBirth      : String;
    nationality       : String;
    secondNationality : String;
    additionalRemarks : String;
    city              : String;
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
    cases  : Association to Cases;
    person : Association to Person;
// relationship : Association to Relationship;
}

entity Object : Identifier {
    entityGuid     : UUID;
    entityId       : String;
    entityType     : String;
    entityDesc     : String;
    sourcen        : String;
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
    cases  : Association to Cases;
    object : Association to Object;
// relationship : Association to Relationship;
}

entity RelPersonObject : Identifier {
    person : Association to Person;
    object : Association to Object;
// relationship : Association to Relationship;
}

entity Activity : Identifier {
    entityGuid        : UUID;
    entityId          : String;
    entityType        : String;
    entityDesc        : String;
    entityTime        : String;
    sourcen           : String;
    origin            : String;
    activityType      : String;
    location          : String;
    activityCategory  : String;
    activityOwner     : String;
    activityStartDate : Date;
    activityStartTime : String;
    activityEndDate   : Date;
    activityEndTime   : String;
    activitySummary   : String;
    activityPriority  : String;
    activityStatus    : String;
    @sap.esh.isVirtual
    relCases          : Association to RelCasesActivity;
    @sap.esh.isVirtual
    relPerson         : Association to RelActivityPerson;
    @sap.esh.isVirtual
    relObject         : Association to RelActivityObject;
}

entity RelCasesActivity : Identifier {
    cases    : Association to Cases;
    activity : Association to Activity;
// relationship : Association to Relationship;
};

entity RelActivityPerson : Identifier {
    activity : Association to Activity;
    person   : Association to Person;
// relationship : Association to Relationship;
};


entity RelActivityObject : Identifier {
    activity : Association to Activity;
    object   : Association to Object;
// relationship : Association to Relationship;
};


entity Location : Identifier {
    entityGuid       : UUID;
    entityId         : String;
    entityType       : String;
    entityDesc       : String;
    entityTime       : String;
    position         : hana.ST_POINT(4326); //Position
    sourcen          : String;
    origin           : String;
    locationCategory : String;
    houseNumber      : String;
    street           : String;
    city             : String;
    postalCode       : String;
    country          : String;
    region           : String;
    locationType     : String;
    @sap.esh.isVirtual
    relObject        : Association to RelObjectLocation;
    @sap.esh.isVirtual
    relPerson        : Association to RelLocationPerson;
    @sap.esh.isVirtual
    relIncidents     : Association to RelIncidentLocation;
}


entity RelObjectLocation : Identifier {
    object   : Association to Object;
    location : Association to Location;
// relationship : Association to Relationship;
}

entity RelLocationPerson : Identifier {
    location : Association to Location;
    person   : Association to Person;
// relationship : Association to Relationship;
}

entity Incidents : Identifier {
    entityGuid        : UUID;
    entityId          : String;
    entityType        : String;
    entityDesc        : String;
    entityTime        : String;
    position          : hana.ST_POINT; //Position
    sourcen           : String;
    origin            : String;
    incidentType      : String;
    startDate         : Date;
    endDate           : Date;
    reportedBy        : String;
    location          : String;
    incidentStartTime : String;
    incidentEndTime   : String;
    @sap.esh.isVirtual
    relLocation       : Association to RelIncidentLocation;
    @sap.esh.isVirtual
    relPerson         : Association to RelIncidentPerson;
    @sap.esh.isVirtual
    relCases          : Association to RelCasesIncident;
}

entity RelIncidentLocation : Identifier {
    incident : Association to Incidents;
    location : Association to Location;
// relationship : Association to Relationship;
}

entity RelIncidentPerson : Identifier {
    incident : Association to Incidents;
    person   : Association to Person;
// relationship : Association to Relationship;
}

entity RelCasesIncident : Identifier {
    cases    : Association to Cases;
    incident : Association to Incidents;
// relationship : Association to Relationship;
}

entity Leads : Identifier {
    entityGuid    : UUID;
    entityId      : String;
    entityType    : String;
    entityDesc    : String;
    entityTime    : String;
    sourcen       : String;
    origin        : String;
    leadType      : String;
    leadCategory  : String;
    leadOwner     : String;
    leadStartDate : Date;
    leadStartTime : String;
    leadEndDate   : Date;
    leadEndTime   : String;
    leadSummary   : String;
    leadPriority  : String;
    leadStatus    : String;
    @sap.esh.isVirtual
    relCases      : Association to RelLeadsCases;
    @sap.esh.isVirtual
    relPerson     : Association to RelLeadsPerson;
}

entity RelLeadsCases : Identifier {
    lead  : Association to Leads;
    cases : Association to Cases;
// relationship : Association to Relationship;
}

entity RelLeadsPerson : Identifier {
    lead   : Association to Leads;
    person : Association to Person;
// relationship : Association to Relationship;
}

entity Relationship : Identifier {
    relationshipGuid : UUID;
    sourceRefId      : String;
    targetRefId      : String;
    relTypeCode      : String;
    sourceSystem     : String;
    origin           : String;
// @sap.esh.isVirtual
// relCasesPerson      : Association to RelCasesPerson;
// @sap.esh.isVirtual
// relCasesObject      : Association to RelCasesObject;
// @sap.esh.isVirtual
// relPersonObject     : Association to RelPersonObject;
// @sap.esh.isVirtual
// relCasesActivity    : Association to RelCasesActivity;
// @sap.esh.isVirtual
// relActivityPerson   : Association to RelActivityPerson;
// @sap.esh.isVirtual
// relActivityObject   : Association to RelActivityObject;
// @sap.esh.isVirtual
// relObjectLocation   : Association to RelObjectLocation;
// @sap.esh.isVirtual
// relLocationPerson   : Association to RelLocationPerson;
// @sap.esh.isVirtual
// relIncidentLocation : Association to RelIncidentLocation;
// @sap.esh.isVirtual
// relIncidentPerson   : Association to RelIncidentPerson;
// @sap.esh.isVirtual
// relCasesIncident    : Association to RelCasesIncident;
// @sap.esh.isVirtual
// relLeadsCases       : Association to RelLeadsCases;
// @sap.esh.isVirtual
// relLeadsPerson      : Association to RelLeadsPerson;
}
