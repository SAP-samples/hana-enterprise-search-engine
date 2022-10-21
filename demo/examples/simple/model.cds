type Name: String(256);

aspect Identifier {
    key id   : UUID;
}

entity Person: Identifier {
    @Search.defaultSearchElement: true
    @Search.fuzzinessThreshold: 0.8
    @EnterpriseSearch.searchOptions: 'similarCalculationMode=substringsearch'
    @sql.append: 'FUZZY SEARCH INDEX ON'
    firstName: Name;
    @Search.defaultSearchElement: true
    @Search.fuzzinessThreshold: 0.8
    @EnterpriseSearch.searchOptions: 'similarCalculationMode=substringsearch'
    @sql.append: 'FUZZY SEARCH INDEX ON'
    lastName: Name;
    birthDate: Date;
    @EnterpriseSearch.filteringFacet.default: true
    nationality: String(80)
}
