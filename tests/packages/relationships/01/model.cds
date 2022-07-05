using {sap.esh.Identifier} from './esh';

entity Organization : Identifier {
    name  : String(4000);
    @sap.esh.isVirtual
    relPerson : Association to RelOrgPerson;
}

entity Person : Identifier {
    firstName: String(4000);
    lastName  : String(4000);
    @sap.esh.isVirtual
    relOrganization: Association to RelOrgPerson;
}

entity RelOrgPerson: Identifier {
    person: Association to Person;
    organization: Association to Organization;
    type:  Association to TypeRelOrgPerson;
}

entity TypeRelOrgPerson {
    key code: String(80);
    description: String(4000);
}