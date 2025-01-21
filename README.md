[![FINOS - Incubating](https://cdn.jsdelivr.net/gh/finos/contrib-toolbox@master/images/badge-incubating.svg)](https://finosfoundation.atlassian.net/wiki/display/FINOS/Incubating)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue)](https://www.python.org/downloads/release/python-3)
[![Pypi](https://img.shields.io/pypi/v/symphony-bdk-python)](https://pypi.org/project/symphony-bdk-python/)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/finos/symphony-bdk-python/build/main)

# Symphony BDK for Python

This is the Symphony BDK for Python to help develop bots and interact with the [Symphony REST APIs](https://developers.symphony.com/restapi/reference).

## Project Overview

Symphony BDK for Python provides tools for building bots and integrating with Symphony APIs. This document outlines its usage, installation, and contribution guidelines.

## Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/docs/#installation)

## Installation Steps

### Option 1: Build from Source
- Install dependencies: `poetry install`
- Build the package: `poetry build`
- Run tests: `poetry run pytest`
- Perform a pylint scan locally: `poetry run pylint <module_name>`
- Generate documentation locally: `cd docsrc && make html`

### Verification
Verify the successful installation by running any of the following commands:
```
poetry --version
```

## External Documents

Refer to the following for additional guidance:
- [Reference Documentation](https://symphony-bdk-python.finos.org/)
- [Getting Started Guide](https://symphony-bdk-python.finos.org/markdown/getting_started.html)

## Roadmap

The next milestone is the [2.5.x](https://github.com/finos/symphony-bdk-python/milestone/6), focused on delivering improvements and bug fixes.

## Contributing

To contribute:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/fooBar`
3. Read the [Contribution Guidelines](CONTRIBUTING.md) and [Community Code of Conduct](https://www.finos.org/code-of-conduct)
4. Commit changes: `git commit -am 'Add some fooBar'`
5. Push changes: `git push origin feature/fooBar`
6. Open a Pull Request.

_NOTE:_ Ensure you have an active Individual Contributor License Agreement (ICLA) or Corporate Contribution License Agreement (CCLA) with FINOS.

For further inquiries, email [help@finos.org](mailto:help@finos.org).


### Updating Generated Code

Python BDK uses [OpenAPITools/openapi-generator](https://github.com/OpenAPITools/openapi-generator/) to generate code. 
To update the generated code, follow these steps:

1. Checkout the latest branch of the fork (e.g., [sym-python-5.5.0](https://github.com/SymphonyPlatformSolutions/openapi-generator/tree/sym-python-5.5.0)).
2. Update the fork source code, review, and merge it.
3. Generate the JAR file in `openapi-generatormodules/openapi-generator-cli/target/openapi-generator-cli.jar`:
   - Use Maven: 
     ```bash
     mvn clean install -Dmaven.test.skip=true && mvn clean package -Dmaven.test.skip=true
     ```
   - Alternatively, use IntelliJ's build button to build the project and generate the JAR file.
4. Copy the JAR file to the Python BDK repository: `symphony-api-client-python/api_client_generation/openapi-generator-cli.jar`.
5. Execute the generation script: 
   ```bash
   ./generate.sh
   ```
6. Commit and push the newly generated code along with the updated JAR file.


## License

Copyright 2021 Symphony LLC

Distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

SPDX-License-Identifier: [Apache-2.0](https://spdx.org/licenses/Apache-2.0).
