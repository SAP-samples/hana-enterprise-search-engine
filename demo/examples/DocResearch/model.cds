using {sap.esh.Identifier} from '../../../model/esh';


@EnterpriseSearch.enabled
@EndUserText.Label : 'Document'
@EnterpriseSearchHana.passThroughAllAnnotations
@UI.headerInfo.typeName: 'Document'
@UI.headerInfo.typeNamePlural: 'Documents'
@UI.headerInfo: {
          title: {
            value: 'title',
            url: 'docURL'
          }
        }
entity Document {
    key id        : UUID;
        @UI.Identification                           : [{Position : 10}]
        @EndUserText.Label                           : 'Image'
        @Search.defaultSearchElement                 : false
        @Semantics.imageURL                          : true
        image     : LargeString; //image

        @sap.esh.isText
        @UI.Identification                           : [{Position : 30}]
        @EnterpriseSearch.defaultValueSuggestElement : true
        @EndUserText.Label                           : 'Title'
        @Search.fuzzinessThreshold                   : 0.85
        @Search.defaultSearchElement
        title     : String(5000); //title

        @EndUserText.Label                           : 'Author'
        @sap.esh.isText
        @UI.Identification                           : [{Position : 90}]
        @Search.defaultSearchElement
        @EnterpriseSearch.filteringFacet.default     : true
        author    : String; //author

        @EndUserText.Label                           : 'Text'
        @sap.esh.isText
        @UI.Identification                           : [{Position : 50}]
        @EnterpriseSearch.snippets.enabled
        @EnterpriseSearch.snippets.maximumLength     : 800
        @Search.defaultSearchElement
        @Search.fuzzinessThreshold                   : 0.80
        text      : LargeBinary; //text

        @UI.Identification                           : [{Position : 60}]
        @EndUserText.Label                           : 'Created At'
        @EnterpriseSearch.filteringFacet.default     : true
        createdAt : Date; //createdAt

        @UI.Identification                           : [{Position : 70}]
        @EndUserText.Label                           : 'Changed At'
        @EnterpriseSearch.filteringFacet.default     : true
        changedAt : Date; //changedAt

        @UI.Identification                           : [{Position : 80}]
        @EndUserText.Label                           : 'Document type'
        @Search.defaultSearchElement
        @EnterpriseSearch.filteringFacet.default     : true
        docType   : String(10);

        @UI.Identification                           : [{
            Position : 100,
            url      : 'docURL'
        }]
        @EndUserText.Label                           : 'Document URL'
        @Search.defaultSearchElement
        docURL    : String
}
