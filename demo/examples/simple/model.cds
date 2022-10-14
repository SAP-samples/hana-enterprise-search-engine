type Name: String(256);

aspect Identifier {
    key id   : UUID;
}

entity Person: Identifier {
    firstName: Name;
    lastName: Name;
}