using {sap.esh.Identifier} from './esh.cds';

entity Organization : Identifier {
    name  : String(4000);
    owner : Association to Person;
}

entity Person : Identifier {
    firstName: String(4000);
    lastName  : String(4000);
}