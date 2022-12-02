# DataLoad documentation

This example is about to demonstrate the "Update" functionality. It should be possible that an existing data set is modified.

# Model
In the [model.cds](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/main/demo/examples/dataLoad/model.cds) there are different entities defined:
- the A-Objects are with source keys
- the B-Objects do not have source keys at all
- the C-Objects and D-Objects are partly with source key

# Notebook
The notebook shows tests with and without source keys.
In terms of procedure, the tests are structured very similarly. The tenant is deleted in the first place. Then the tenant is created, the data model and the data are uploaded. Afterwards, the same data is uploaded again. Here, a 400 status code is intentionally generated, since the same data already exists. Then the data is changed and uploaded again and the data set should be modified. After successfully uploaded data, the tenant is deleted again.