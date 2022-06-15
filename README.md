# SAP-samples/repository-template
This default template for SAP Samples repositories includes files for README, LICENSE, and .reuse/dep5. All repositories on github.com/SAP-samples will be created based on this template.

# Containing Files

1. The LICENSE file:
In most cases, the license for SAP sample projects is `Apache 2.0`.

2. The .reuse/dep5 file: 
The [Reuse Tool](https://reuse.software/) must be used for your samples project. You can find the .reuse/dep5 in the project initial. Please replace the parts inside the single angle quotation marks < > by the specific information for your repository.

3. The README.md file (this file):
Please edit this file as it is the primary description file for your project. You can find some placeholder titles for sections below.

# [Title]
<!-- Please include descriptive title -->

<!--- Register repository https://api.reuse.software/register, then add REUSE badge:
[![REUSE status](https://api.reuse.software/badge/github.com/SAP-samples/REPO-NAME)](https://api.reuse.software/info/github.com/SAP-samples/REPO-NAME)
-->

## Description
<!-- Please include SEO-friendly description -->

## Requirements
- Access to an up-to date SAP HANA (on-prem or cloud)
- Install latest version of [Python 3.10](https://www.python.org/downloads/ "downloads")
- [SAP CAP](https://cap.cloud.sap/docs/get-started/), including node.js as described in the "local setup" section
- [Visual Studio Code](https://code.visualstudio.com/download)
- [SAP CDS language support for Visual Studio Code](https://cap.cloud.sap/docs/tools/#add-cds-editor)

Enable Python linting in Visual Studio Code as described [here](https://code.visualstudio.com/docs/python/linting)

In the project folder execute

python3 -m venv .venv

Remark: On windows use "python" instead of "python3"

Activate the virtual environment with

.venv\scripts\activate

Remark: The terminal promt shows a prefix "(.venv)" if the virtual environment is activ.

## Download and Installation

### Download
Clone or download this repository
### Install required packages
Make sure that the virtual environment is active before installing the required packages with

python3 -m pip install -r requirements/core.txt

For development and test installations run additionally

python3 -m pip install -r requirements/development.txt

#### Configuration
Installation will create some HANA DB users and the src/.config.json file. In this file you find the users and passwords created for the installation for debugging purposes

Go to the project folder and run the config script

run pyhton src/config.py with the following parameters

python src/config.py --action install --db-host <<your_hana_host>> --db-port <<your_hana_port>> --db-setup-user <<your HANA admin user>> --db-setup-password <<your HANA admin password>> --db-schema-prefix <<your HANA >>


Uninstall:

python src/config.py --action delete --db-setup-user <<your HANA admin user>> --db-setup-password <<your HANA admin password>>

#### Start server
Active virtual environment in the project folder with .venv\scripts\activate 

Change to the src folder with cd src

For test purposes start the server with uvicorn server:app --reload

For productive use start the server with uvicorn server:app

Server started sucessfully if the message "Application startup complete" is displayed

### Run end-to-end test
Active virtual environment in the project folder with .venv\scripts\activate 
 
python3 tests\test_suite\e2e_service_test.py


## Known Issues
<!-- You may simply state "No known issues. -->

## How to obtain support
[Create an issue](https://github.com/SAP-samples/<repository-name>/issues) in this repository if you find a bug or have questions about the content.
 
For additional support, [ask a question in SAP Community](https://answers.sap.com/questions/ask.html).

## Contributing
If you wish to contribute code, offer fixes or improvements, please send a pull request. Due to legal reasons, contributors will be asked to accept a DCO when they create the first pull request to this project. This happens in an automated fashion during the submission process. SAP uses [the standard DCO text of the Linux Foundation](https://developercertificate.org/).

## License
Copyright (c) 2022 SAP SE or an SAP affiliate company. All rights reserved. This project is licensed under the Apache Software License, version 2.0 except as noted otherwise in the [LICENSE](LICENSE) file.
