using {sap.esh.Identifier} from '../../../model/esh';

@EndUserText.Label : 'Document'
@EnterpriseSearchHana.passThroughAllAnnotations
entity Document {
    key id        : UUID;
        @sap.esh.isText
        @EnduserText.Label                       : 'Title'
        @Search.fuzzinessThreshold               : 0.85
        // @UI.dentification                       : {position : 10}
        title     : String(5000);
        @EnduserText.Label                       : 'Text'
        // @UI.multiLineText
        @sap.esh.isText
        // @UI.identification                       : {position : 20}
        @EnterpriseSearch.snippets.enabled
        @EnterpriseSearch.snippets.maximumLength : 800
        text      : LargeBinary;
        @EnterpriseSearch.filteringFacet.default : true
        createdAt : Date;
        @EnterpriseSearch.filteringFacet.default : true
        changedAt : Date;
}
