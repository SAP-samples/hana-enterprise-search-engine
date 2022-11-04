using {sap.esh.Identifier} from '../../../model/esh';

@EndUserText.Label : 'Document'
@EnterpriseSearchHana.passThroughAllAnnotations
entity Document {
    key id    : UUID;
        @EndUserText.Label                       : 'Title'
        @Search.fuzzinessThreshold               : 0.85
        // @UI.identification                       : {position : 10}
        title : String(5000);
        @EndUserText.Label                       : 'Text'
        // @UI.multiLineText
        @sap.esh.isText
        // @UI.identification                       : {position : 20}
        @EnterpriseSearch.snippets.enabled
        @EnterpriseSearch.snippets.maximumLength : 800
        text  : LargeBinary;
}
