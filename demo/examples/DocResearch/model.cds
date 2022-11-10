using {sap.esh.Identifier} from '../../../model/esh';


@EnterpriseSearch.enabled
@EndUserText.Label : 'Document'
@EnterpriseSearchHana.passThroughAllAnnotations
entity Document {
    key id        : UUID;
        @sap.esh.isText
        @UI.Identification.Position              : 10
        @EndUserText.Label                       : 'Title'
        @Search.fuzzinessThreshold               : 0.85
        @Search.defaultSearchElement
        title     : String(5000);
        @EndUserText.Label                       : 'Author'
        @sap.esh.isText
        @UI.Identification.Position              : 20
        @Search.defaultSearchElement
        author    : String;

        @EndUserText.Label                       : 'Text'
        @sap.esh.isText
        @UI.Identification.Position              : 30
        @EnterpriseSearch.snippets.enabled
        @EnterpriseSearch.snippets.maximumLength : 800
        @Search.defaultSearchElement
        text      : LargeBinary;

        @UI.Identification.Position              : 40
        @EndUserText.Label                       : 'Created At'
        @EnterpriseSearch.filteringFacet.default : true
        createdAt : Date;

        @UI.Identification.Position              : 50
        @EndUserText.Label                       : 'Changed At'
        @EnterpriseSearch.filteringFacet.default : true
        changedAt : Date;
}
