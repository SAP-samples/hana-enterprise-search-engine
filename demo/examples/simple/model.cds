type Name: String(256);

aspect Identifier {
    key id   : UUID;
}

@EnterpriseSearch.enabled: true
entity Person: Identifier {
    @Search.defaultSearchElement: true
    firstName: Name;
    @Search.defaultSearchElement: true
    lastName: Name;
    birthDate: Date;
    @sap.esh.isText
    country: String(80)
}
