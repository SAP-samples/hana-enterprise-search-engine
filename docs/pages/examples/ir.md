---
layout: default
title: "Investigative Research"
nav_order: 2
parent: Examples
---

Documentation of an example how to use the enterprise search HANA technology

---------------------------------------------------------------------------------------------------------------------------------------
# Introduction
---------------------------------------------------------------------------------------------------------------------------------------

Here the search engine is tested and data from SAP ICM is used as basis. This example is called "investigative  research" 
(shortcut: IR). The example is shown the possiblity to build queries with the HANA enterprise search. Simple as well as complex queries 
are shown. The objective of this example is that the key-user gets a feeling of how to use this technology wihtin its business 
processes. Furthermore the searches are built in a kind of scenarios. Entity links are shown, such as person attributes, that have a 
connection to a location. This results in a scenario when a person's location is searched for.

---------------------------------------------------------------------------------------------------------------------------------------
# Data Model
---------------------------------------------------------------------------------------------------------------------------------------

The data itself is example data (no real person related data). Some attributes of the entities are modified and not 
all attributes are exactly the same as ICM. The following points show which files are relevant for a successful data model:

1. The CDS file is shown the tables and their relations to each other
2. The JSON file which contains the data itself. The data is related to the structure and relationships of the CDS file
3. For starting building queries it is mandatory to have these two files. Without these files it is not possible to build queries

---------------------------------------------------------------------------------------------------------------------------------------
# Pre-Conditions
---------------------------------------------------------------------------------------------------------------------------------------

Following process should be executed firstly to create a tenant:
- [Setup.ipynb(https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/demo/notebooks/setup.ipynb)] (For deletion of tenant use [delete_tenant.ipynb](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/demo/notebooks/delete_tenant.ipynb))

Please consider the following notes to test the queries:
1. Configure your server configuration (.config.json) and then start server.py before you start executing the queries
2. Begin always with "Initialize" within the notebook
3. There is a possibility that some queries will not work. Please let us know if you encounter any errors

---------------------------------------------------------------------------------------------------------------------------------------
# Files/Objects
---------------------------------------------------------------------------------------------------------------------------------------

Relevant notebooks:
- [simple_searches.ipynb]: Shows simple requests on entities 
- [fuzzy_searches.ipynb]: Shows incomplete parameter searches
- [complex_relation_searches.ipynb]: Shows complex searches in several entities
- [geo_searches.ipynb]: Shows locations/coordinates searches with the result of latitude and longitude

Relevant files:
- icm2.model.json -> generated JSON File for creating tenant
- data.json -> JSON File with relevant data according to structure and relationship
- model.cds -> CDS file with entities and relationships

---------------------------------------------------------------------------------------------------------------------------------------
# Notebooks description
---------------------------------------------------------------------------------------------------------------------------------------

- simple_searches.ipynb:

    This notebook demonstrates basic queries e.g. search for a name, name AND age, age less than 30, name with wildcard(*), etc. It serves
    to get a feeling how the queries works. There are different condition attributes which can be used e.g. "equals", "notequals",
    case-(in)sensitive, etc.

- fuzzy_searches.ipynb:

    These queries shows incomplete search statements. When user wants to search for the name "Kennedy" but searches for "Kenne" then the 
    program searches for the best matches in the database. You can configure how high should be the percentage of the match. 
    For example you can configure the number 0.5 for 50 percent of match.

- complex_relation_searches.ipynb:

    This example is about the relations between the entities and the complexity of the queries. It will be demonstrated that queries
    can be built also for several objects (e.g. search for persons location). Entity cross queries are presented.
    Important notes: If you want to search for a text, but you only know a few words, you can use the "doEshEscape=True" function.
    If you want to search for explicit text, then you can use the "isPhrase=True" function. For an exact example see notebook.

- geo_searches.ipynb:

    This notebook contains queries about to figure out locations with(in) coordinates. It can be searched for exact coordinates or coordinates
    which are in a radius. Therefore, it has to be defined a polygon. 
    The attribute conditions :WITHIN:, :COVERED_BY: and :INTERSECTS: are available and are internally mapped to the SQL functions ST_Within, 
    ST_CoveredBy, and ST_Intersects. 
    It should be considered that the first Polygon point is also the last Polygon point so that the rectangle can be closed e.g.
    location:COVERED_BY:POLYGON((13.4 52.5, 13.5 52.5, 13.5 52.6, 13.4 52.6, 13.4 52.5)) 


---------------------------------------------------------------------------------------------------------------------------------------
# Entities and model
---------------------------------------------------------------------------------------------------------------------------------------
Following entities are created:
- [Cases](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/demo/examples/ir/model.cds?plain=1#L9)
- [Person](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/demo/examples/ir/model.cds?plain=1#L37)
- [Object](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/demo/examples/ir/model.cds?plain=1#L75)
- [Activity](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/demo/examples/ir/model.cds?plain=1#L104)
- [Location](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/demo/examples/ir/model.cds?plain=1#L142)
- [Incidents](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/demo/examples/ir/model.cds?plain=1#L176)
- [Leads](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/demo/examples/ir/model.cds?plain=1#L213)

Please have a look on the file "[model.cds](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/demo/examples/ir/model.cds)" for detailed information regarding attributes and relationships.
Also a class diagram is existing. Please have a look on "[ir_model.png](https://github.com/SAP-samples/hana-enterprise-search-engine/blob/dev/docs/images/examples/ir/ir_model.png)".

---------------------------------------------------------------------------------------------------------------------------------------
# Scenario/example
---------------------------------------------------------------------------------------------------------------------------------------
Example:
- Search for a witness who reported the the "Threat of violence Kennedy Gomez"
- A detective comes to the conclusion  that this incident  might be related to a crime and thus creates a lead and assigns the incident  
with the previous information.  He also assigns to the lead an unknown  suspect –together with all the information  he got about this 
person -and the location  of the criminial. He collects other elements for the investigation  like the records of further 
interrogations  or a script for further interviews.
- The detective updates the description  of the suspect as a result of e.g. further interviews.
- Detective creates a follow-up  activity  in order to record the phone intercept of J Kennedy and B Ramage.
- It becomes clear for the detective, that the unknown  person is a known criminal.
- The detective merges the record of the unknown  suspect with  the record of the known criminal.
- The Data Quality  Manager reviews  the result of the merging.



