# SAP HANA Enterprise Search Engine
[![REUSE status](https://api.reuse.software/badge/github.com/SAP-samples/hana-enterprise-search-engine)](https://api.reuse.software/info/github.com/SAP-samples/hana-enterprise-search-engine)

## Description
This enterprise search engine example program shows how to utilize [SAP HANA Search](https://help.sap.com/docs/SAP_HANA_PLATFORM/691cb949c1034198800afde3e5be6570 "HANA search developer guide") which is part of both, cloud and on-premise shipments, of [SAP HANA DB](https://www.sap.com/products/hana.html). It provides REST-APIs for search and CRUD (create, read, update, delete) to process structured business objects and their relationships. To do so, it maps this business perspective to a technical perspective which is then processed by HANA. [SAP CAP](https://cap.cloud.sap) can be used to model the business objects and their relationships. The example also shows how to use the enterprise search UI which is delivered as part of SAP UI5. Programming language is Python.

![Architecture Overview](/images/hana-enterprise-search-engine.png)

The enterprise search engine provides the following APIs:

| Functionality | HTTP method | URL | URL parameters | Request Body | Response Body | API maturity |
| :-------------: | :-----------: | :----:  | :----:  | :----:    | :----:    | :----:    |
| Create tenant | POST | /v1/tenant/{tenant-id} | - | - | status | \** |
| Get all tenants | GET | /v1/tenant | - | - | tenants | \** |
| Delete tenant | DELETE | /v1/tenant/{tenant-id} | - | - | status | \** |
| Deploy data model | POST | /v1/deploy/{tenant-id} | - | model | status | \** |
| Create data | POST | /v1/data/{tenant-id} | - | objects | identifiers | \** |
| Read data | POST | /v1/read/{tenant-id} | - | identifiers | objects | \** |
| Delete data | POST | /v1/data/{tenant-id} | - | identifiers | - | \** |
| Search (OData format) | GET | /v1/search/{tenant-id}/{esh-version} | query | - | - | \**** |
| Get metadata (OData format) | GET | /v1/search/{tenant-id}/{esh-version}/$metadata | - | - | metadata | \**** |
| Bulk Search (OData format) | POST | /v1/search/{tenant-id}/{esh-version} | - | query | result | \**** |
| Search UI | GET | /v1/searchui/{tenant-id} | query | - | - | \**** |
| Search (new request format) | POST | /v2/search/{tenant-id}/{esh-version} | - | query | result | \* |

API maturity:

\* ... experimental, expect major changes / rework, 

\** ... in development, API changes and bugs expected

\*** ... stable API, good error handling

\**** ... used in production since years

[This](\tests\packages\run_tests.py) test program demonstrates the API usage based on a test example.

## Requirements
- Up-to date SAP HANA (on-prem or cloud)
- Latest version of [Python 3.10](https://www.python.org/downloads/ "download")
- [SAP CAP](https://cap.cloud.sap/docs/get-started/ "getting started")

### Additional requirements for development
- [Visual Studio Code](https://code.visualstudio.com/download "download")
- [SAP CDS language support for Visual Studio Code](https://cap.cloud.sap/docs/tools/#add-cds-editor)
- Python linting as described [here](https://code.visualstudio.com/docs/python/linting)


## Download and Installation
Clone or download this repository for example to c:\devpath\hana-search. 

Then open a console and change to the download path:
```bat
c:\ cd c:\devpath\hana-search
```

Create a python virtual environment named .venv:
```bat
c:\devpath\hana-search> python -m venv .venv
```

Activate the python virtual environment:
```bat
c:\devpath\hana-search> .venv\scripts\activate
```

If the environment is activated correctly, a previx (.venv) is shown in the command line:
```bat
(.venv) c:\devpath\hana-search>
```


Install the required Python packages:
```bat
(.venv) c:\devpath\hana-search> python -m pip install -r requirements/core.txt
```
Install additional Python packages if this installation is used for development:
```bat
(.venv) c:\devpath\hana-search> python -m pip install -r requirements/development.txt
```


### Configuration
An admin-user is needed with the following privileges:
- system privilege CREATE SCHEMA (grantable to other users and roles)
- system privilege USER ADMIN
- object privilege ESH_CONFIG execute (grantable to others)

Configuration is done with the config.py script using the following parameters
- --action install
- --db-host: The HANA host name
- --db-port: The HANA port number
- --db-setup-user: The HANA user name used for setup
- --db-setup-password: The HANA user password for the seup-user. Note: This user-name and passwords are not stored
- --db-schema-prefix: The prefix which is used for the schemas of this installation. To avoid conflicts, there must not be any other schemas on the database starting with this schema prefix.

```bat
c:\devpath\hana-search> python src/config.py --action install --db-host <<your_hana_host>> --db-port <<your_hana_port>> --db-setup-user <<your HANA admin user>> --db-setup-password <<your HANA admin password>> --db-schema-prefix <<your HANA >>

```
The configuration will create some HANA DB users and the src/.config.json file which contains configuration information and users and passwords created for the installation (needed e.g. for debugging purposes). Please do not change the src/.config.json file.

The default settings for the web-server (host 127.0.0.1 and port 8000) can be changed using parameters srv-host and srv-port.


To uninstall run the following command:

```bat
c:\devpath\hana-search> python src/config.py --action delete --db-setup-user <<your HANA admin user>> --db-setup-password <<your HANA admin password>>
```
Attention: This will delete ALL data of this installation!

### Start server
Start the server in the console with the activated virtual environment:
```bat
c:\ cd c:\devpath\hana-search
c:\devpath\hana-search> .venv\scripts\activate
(.venv) c:\devpath\hana-search> python src\server.py
```

The message "Application startup complete" indicates a successful server startup.

### Run end-to-end test

```bat
(.venv) c:\devpath\hana-search> python tests\packages\run_tests.py
```
The test script prints a success-message in the last output line if all tests are executed successfully.


## Known Issues
This is an example application in an early stage of development, so
- don't store personal information because of missing access logging
- don't store sensitive information because there is no access control
- don't use the example application productively because users and passwords generated by config.py are stored plaintext in src/.config.json
- make sure that your system setup (tenent creation, post data model, post data) is completely automated as there is no migration provided between different (minor) versions of this example
- don't expect mature error handling. Use the provided tests as a starting point


## How to obtain support
This is an example application and not supported by SAP. However, you can 
[create an issue](https://github.com/SAP-samples/<repository-name>/issues) in this repository if you find a bug or have questions about the content.
 
For additional support, [ask a question in SAP Community](https://answers.sap.com/questions/ask.html).

## Contributing
If you wish to contribute code, offer fixes or improvements, please send a pull request. Due to legal reasons, contributors will be asked to accept a DCO when they create the first pull request to this project. This happens in an automated fashion during the submission process. SAP uses [the standard DCO text of the Linux Foundation](https://developercertificate.org/).

## Code of Conduct
see [here](CODE_OF_CONDUCT.md)
## License
Copyright (c) 2022 SAP SE or an SAP affiliate company. All rights reserved. This project is licensed under the Apache Software License, version 2.0 except as noted otherwise in the [LICENSE](LICENSE) file.
