aspect BusinessObject {}
aspect RelationshipObject {}

aspect CodeList {
    description : String(256);
}

entity CountryCode : CodeList {}
entity OrganizationType : CodeList {}
entity PersonOrganizationRelationshipType: CodeList {}

type Address {
    country     : Association to CountryCode;
    postalCode  : String(100);
    city        : String(100);
    street      : String(100);
    houseNumber : String(100);
}

entity Person : BusinessObject {
    firstName : String(256);
    lastName  : String(256);
    address   : Address;
    organizations: Association to many RelPersonOrganization;
}

entity Organization : BusinessObject {
    name             : String(256);
    address          : Address;
    organizationType : Association to OrganizationType;
    persons: Association to many RelPersonOrganization;
}

entity RelPersonOrganization : RelationshipObject {
    person       : Association to Person;
    organization : Association to Organization;
    personOrganizationRelationshipType: Association to PersonOrganizationRelationshipType;
}
