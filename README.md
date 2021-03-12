[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue)](https://www.python.org/downloads/release/python-3)
[![Pypi](https://img.shields.io/badge/pypi-2.0b0-green)](https://pypi.org/project/sym-api-client-python/2.0b0/)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/SymphonyPlatformSolutions/symphony-api-client-python/build/2.0)

# Symphony BDK for Python

This is the Symphony BDK for Python to help develop bots and interact with the [Symphony REST APIs](https://developers.symphony.com/restapi/reference).

Legacy Python BDK is located in [legacy](./legacy) folder.

## Installation and getting started
The [reference documentation](https://symphonyplatformsolutions.github.io/symphony-api-client-python/) includes detailed
installation instructions as well as a comprehensive
[getting started](https://symphonyplatformsolutions.github.io/symphony-api-client-python/markdown/getting_started.html)
guide.

## Build from source

The Symphony BDK uses and requires Python 3.8 or higher. Be sure you have it installed before going further.

We use [poetry](https://python-poetry.org/) in order to manage dependencies, build, run tests and publish.
To install poetry, follow instructions [here](https://python-poetry.org/docs/#installation).

On the first time, run `poetry install`. Then run `poetry build` to build the sdist and wheel packages.
To run the tests, use `poetry run pytest`.

It is possible to run pylint scan locally (on a specific file or package) executing the following command:
`poetry run pylint <module_name>`.

To generate locally the Sphinx documentation, run: `cd docsrc && make html`.

## Contributing

If you want to contribute, please check the [contributing guidelines](CONTRIBUTING.md).