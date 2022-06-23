namespace example;

@EndUserText.Label: 'Person'
entity Person {
    @EndUserText.Label: 'First Name'
    @Search.fuzzinessThreshold: 0.85
    firstName: String(256);
    @EndUserText.Label: 'Last Name'
    @Search.fuzzinessThreshold: 0.85
    lastName: String(256);
}