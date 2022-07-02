aspect Identifier : {
    key id   : UUID;
    source   : many {
        name : String(4000);
        type : String(4000);
        sid  : String(4000);
    }
}

entity Person : Identifier {
    firstName : String(200);
    lastName  : String(200);
}


entity Organization : Identifier {
    name  : String(2000);
    owner : Association to Person;
}
