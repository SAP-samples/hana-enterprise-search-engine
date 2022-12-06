using {sap.esh.Identifier} from '../../../model/esh';

entity AOrganization : Identifier {
    name  : String(4000);
    @sap.esh.isVirtual
    relPerson : Association to ARelOrgPerson;
}

entity APerson : Identifier {
    firstName: String(4000);
    lastName  : String(4000);
    @sap.esh.isVirtual
    relOrganization: Association to ARelOrgPerson;
}

entity ARelOrgPerson: Identifier {
    person: Association to APerson;
    organization: Association to AOrganization;
}


entity BOrganization {
    key id: UUID;
    name  : String(4000);
    @sap.esh.isVirtual
    relPerson : Association to BRelOrgPerson;
}

entity BPerson {
    key id: UUID;
    firstName: String(4000);
    lastName  : String(4000);
    @sap.esh.isVirtual
    relOrganization: Association to BRelOrgPerson;
}

entity BRelOrgPerson{
    key id: UUID;
    person: Association to BPerson;
    organization: Association to BOrganization;
}

entity COrganization : Identifier {
    name  : String(4000);
    @sap.esh.isVirtual
    relPerson : Association to CRelOrgPerson;
}

entity CPerson  : Identifier{
    firstName: String(4000);
    lastName  : String(4000);
    @sap.esh.isVirtual
    relOrganization: Association to CRelOrgPerson;
}

entity CRelOrgPerson {
    key id: UUID;
    person: Association to CPerson;
    organization: Association to COrganization;
}


entity DOrganization {
    key id: UUID;
    name  : String(4000);
    @sap.esh.isVirtual
    relPerson : Association to DRelOrgPerson;
}

entity DPerson {
    key id: UUID;
    firstName: String(4000);
    lastName  : String(4000);
    @sap.esh.isVirtual
    relOrganization: Association to DRelOrgPerson;
}

entity DRelOrgPerson : Identifier{
    person: Association to DPerson;
    organization: Association to DOrganization;
}
