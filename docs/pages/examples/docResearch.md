# Document Research

## Introduction:
This example shows a PoC of how to load PDF documents to the HANA database and how to use enterprise search technology to build specific searches.

## Pre-conditions:

- First of all, the [model.cds](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/main/demo/examples/DocResearch/model.cds) file is created with its attributes and annotations
- Prepare all PDF files and store them in the directory



## Annotations:

### @UI.Identification                       : [{Position : 10}]
- Handles the position of the column in the UI

### @EndUserText.Label                       : 'Specific Column name'
- Handles the column name individually

### @Search.defaultSearchElement             : false
- Defines whether the attributes are searchable (true) or not (false). 

### @Search.fuzzinessThreshold               : 0.85
- Allows fuzziness searches on the attribute 

### @sap.esh.isText
- Defines the attribute as a string text and allows string requests

### @Semantics.imageURL                      : true
- Defines the attribute as an image. The image appears in the UI with help of the type "LargeBinary"

### @EnterpriseSearch.filteringFacet.default : true
- Enables a function in the UI to add specific filters e.g. entering specific date or filtering for dfault values


## Important notebooks
- [setup.ipynb](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/main/demo/notebooks/delete_tenant.ipynb) -    This notebook creates the tenant and deploys the data model
- [delete_tentant](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/main/demo/notebooks/delete_tenant.ipynb) - This notebook deletes the tenant
- [setup_doc](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/main/demo/examples/DocResearch/notebooks/setup_doc.ipynb) -      This notebook prepares the data from PDF and uploads it to the server
- [extern_queries](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/main/demo/examples/DocResearch/notebooks/extern_queries.ipynb) - This notebook shows examples how to build queries


## Special features
__PDF:__

In the model.cds file, the attribute (text) for the PDF file has to have the type "LargeBinary".
The PDF itself must be encoded to base64. After the PDF is encoded, the encoded data can be uploaded to server

__Image:__

The image must also be defined as large binary in the model.cds file. Also the image must be encoded to base64. Before the encoded data is uploaded to the server it must be added the following string at the beginning of the encoded data: 'data:;base64,'












