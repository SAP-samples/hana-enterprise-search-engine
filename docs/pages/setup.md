---
layout: default
title: "Installation"
nav_order: 2
---

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

# Preconditions
## Preconditions to run the example
- Up-to date SAP HANA (on-prem or cloud)
- Latest version of [Python 3.10](https://www.python.org/downloads/ "download"). Attention: Python 3.11 is not yet supported
- [SAP CAP](https://cap.cloud.sap/docs/get-started/ "getting started")

## Preconditions for development
- [Visual Studio Code](https://code.visualstudio.com/download "download")
- [SAP CDS language support for Visual Studio Code](https://cap.cloud.sap/docs/tools/#add-cds-editor)
- Python linting as described [here](https://code.visualstudio.com/docs/python/linting)


# Installation
## Download example
Clone or download the [repository](https://github.com/SAP-samples/hana-enterprise-search-engine) for example to c:\devpath\hana-enterprise-search-engine. 

## Setup Python environment
Then open a console and change to the download path:
```bat
cd hana-enterprise-search-engine
```

## For Windows:
Create a python virtual environment named .venv:
```bat
c:\devpath\hana-enterprise-search-engine> python -m venv .venv
```

 Activate the python virtual environment:
 ```bat
 c:\devpath\hana-enterprise-search-engine> .venv\scripts\activate
 ```

## For linux:
Create a python virtual environment named .venv:
```bat
./hana-enterprise-search-engine> /bin/python3 -m venv .venv
```

Activate the python virtual environment:
```bat
./hana-enterprise-search-engine> source .venv/bin/activate
```

## For all plattforms:

If the environment is activated correctly, a previx (.venv) is shown in the command line:
```bat
(.venv) c:\devpath\hana-enterprise-search-engine>
```

Install the required Python packages:
```bat
(.venv) c:\devpath\hana-enterprise-search-engine> python -m pip install -r requirements/core.txt
```
Install additional Python packages if this installation is used for development:
```bat
(.venv) c:\devpath\hana-enterprise-search-engine> python -m pip install -r requirements/development.txt
```

## Setup connection to HANA
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
c:\devpath\hana-enterprise-search-engine> python src/config.py --action install --db-host <<your_hana_host>> --db-port <<your_hana_port>> --db-setup-user <<your HANA admin user>> --db-setup-password <<your HANA admin password>> --db-schema-prefix <<your HANA >>

```
The configuration will create some HANA DB users and the src/.config.json file which contains configuration information and users and passwords created for the installation (needed e.g. for debugging purposes). Please do not change the src/.config.json file.

The default settings for the web-server (host 127.0.0.1 and port 8000) can be changed using parameters srv-host and srv-port.


To uninstall run the following command:

```bat
c:\devpath\hana-enterprise-search-engine> python src/config.py --action delete --db-setup-user <<your HANA admin user>> --db-setup-password <<your HANA admin password>>
```
Attention: This will delete ALL data of this installation!

## Start server
Start the server in the console with the activated virtual environment:
```bat
cd hana-enterprise-search-engine

Windows: c:\devpath\hana-enterprise-search-engine> .venv\scripts\activate
Linux:            ./hana-enterprise-search-engine> source .venv/bin/activate

(.venv) c:\devpath\hana-enterprise-search-engine> python src\server.py
```

The message "Application startup complete" indicates a successful server startup.

## Run end-to-end test

```bat
(.venv) c:\devpath\hana-enterprise-search-engine> python tests\packages\run_tests.py
```
The test script prints a success-message in the last output line if all tests are executed successfully.
