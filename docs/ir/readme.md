Documentation of an example how to use the enterprise search HANA technology
---------------------------------------------------------------------------------------------------------------------------------------
# Introduction
---------------------------------------------------------------------------------------------------------------------------------------
Here it is tested the search engine and as basis to test, it is used the data from SAP ICM. This example is called "investigative 
research" (shortcut: IR). It is shown how it is possible to search for queries with the enterprise search technology on HANA. 
Also it is shown that complex queries can be built on an ICM data model. The objective of this example is that the key-user gets a 
feeling of how to use this technology wihtin its business processes. In general in this example there are queries where search 
scenarios are built. For example it is searched for persons and their locations or for persons and their cases or just for persons.
---------------------------------------------------------------------------------------------------------------------------------------
# Data Model
---------------------------------------------------------------------------------------------------------------------------------------
The data itself is example data (no real person related data). Some attributes of the entities are modified and not 
all attributes are exactly the same as ICM. The following points show which files have to be built for a successful data model:

1. It is built a CDS file which is representing the tables and their relations to each other
2. It is built the JSON file which contains the data. This data is related to the structure and relationships of the CDS file
3. For starting building queries it is mandatory to have these two files. Without these files it is not possible to build queries

---------------------------------------------------------------------------------------------------------------------------------------
# Pre-Conditions
---------------------------------------------------------------------------------------------------------------------------------------
Following process should be executed firstly to create a tenant:
-> Setup.ipynb (For deletion of tenant use delete_tenant.ipynb)

Please consider the following notes to test the queries:
1. Configure your server configuration (.config.json) and then start server.py before you start executing the queries
2. Begin always with "Initialize" within the notebook
3. If you add some queries it is possible that something is not going to run well. Please inform us in case of questions.

---------------------------------------------------------------------------------------------------------------------------------------
# Files/Objects
---------------------------------------------------------------------------------------------------------------------------------------
Relevant notebooks:
-> simple_searches.ipynb: Shows simple requests on entities 
-> fuzzy_searches.ipynb: Shows incomplete parameter searches
-> complex_relation_searches.ipynb: Shows complex searches in several entities
-> geo_searches.ipynb: Shows locations/coordinates searches with the result of latitude and longitude

Relevant files:
-> icm2.model.json -> generated JSON File for creating tenant
-> data.json -> JSON File with relevant data according to structure and relationship
-> model.cds -> CDS file with entities and relationships

---------------------------------------------------------------------------------------------------------------------------------------
# Notebooks description
---------------------------------------------------------------------------------------------------------------------------------------
simple_searches.ipynb:
This notebook demonstrates basic queries e.g. search for a name, name AND age, age less than 30, name with wildcard(*), etc. It serves
to get a feeling how the queries works. There are different condition attributes which can be used e.g. "equals", "notequals",
case-(in)sensitive, etc.

fuzzy_searches.ipynb:
These queries shows incomplete search statements. When user wants to search for the name "Kennedy" but searches for "Kenne" then the 
program searches for the best matches in the database. It is possible to configure how high should be the percentage of the match. 

complex_relation_searches.ipynb:
This example is about the relations between the entities and the complexity of the queries. It is going to be demonstrated that queries
can be built also for several objects (e.g. search for persons location)

geo_searches.ipynb:
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
# Cases
# Person
# Object
# Activity
# Location
# Incidents
# Leads

Please have a look on the file "model.cds" for detailed information regarding attributes and relationships.
Also a class diagram is existing. Please have a look on "icm_model.drawio".

---------------------------------------------------------------------------------------------------------------------------------------
# Scenario/example
---------------------------------------------------------------------------------------------------------------------------------------
Example:
•A witness reports that a known criminal was sneaking around a car dealership and for that an incident record is created. 
•A detective comes to the conclusion  that this incident  might be related to a crime and thus creates a lead and assigns the incident  
with the previous information.  He also assigns to the lead an unknown  suspect –together with all the information  he got about this 
person -and the location  of the car dealer. He collects other elements for the investigation  like the records of further 
interrogations  or a script for further interviews.
•The detective updates the description  of the suspect as a result of e.g. further interviews.
•Detective creates a follow-up  activity  in order to record the visit to the car dealership.
•It becomes clear for the detective, that the unknown  person is a known criminal.
•The detective merges the record of the unknown  suspect with  the record of the known criminal.
•The Data Quality  Manager reviews  the result of the merging.



