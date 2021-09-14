[![FINOS - Incubating](https://cdn.jsdelivr.net/gh/finos/contrib-toolbox@master/images/badge-incubating.svg)](https://finosfoundation.atlassian.net/wiki/display/FINOS/Incubating)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue)](https://www.python.org/downloads/release/python-3)
[![Pypi](https://img.shields.io/pypi/v/symphony-bdk-python)](https://pypi.org/project/symphony-bdk-python/)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/finos/symphony-bdk-python/build/main)

# Symphony BDK for Python

This is the Symphony BDK for Python to help develop bots and interact with the [Symphony REST APIs](https://developers.symphony.com/restapi/reference).

## Installation and getting started
The [reference documentation](https://symphony-bdk-python.finos.org/) includes detailed
installation instructions as well as a comprehensive
[getting started](https://symphony-bdk-python.finos.org/markdown/getting_started.html)
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

## Roadmap

Our next milestone is the [2.0.x](https://github.com/finos/symphony-bdk-python/milestone/1) one.
It will only consist in delivering the next improvements of the BDK.


## Contributing
In order to get in touch with the project team, please open a [GitHub Issue](https://github.com/finos/symphony-bdk-python/issues).
Alternatively, you can email/subscribe to [symphony@finos.org](https://groups.google.com/a/finos.org/g/symphony).

1. Fork it
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Read our [contribution guidelines](CONTRIBUTING.md) and [Community Code of Conduct](https://www.finos.org/code-of-conduct)
4. Commit your changes (`git commit -am 'Add some fooBar'`)
5. Push to the branch (`git push origin feature/fooBar`)
6. Create a new Pull Request

_NOTE:_ Commits and pull requests to FINOS repositories will only be accepted from those contributors with an active,
executed Individual Contributor License Agreement (ICLA) with FINOS OR who are covered under an existing and active
Corporate Contribution License Agreement (CCLA) executed with FINOS.
Commits from individuals not covered under an ICLA or CCLA will be flagged and blocked by the FINOS Clabot tool.
Please note that some CCLAs require individuals/employees to be explicitly named on the CCLA.

*Need an ICLA? Unsure if you are covered under an existing CCLA? Email [help@finos.org](mailto:help@finos.org)*

## License
Copyright 2021 Symphony LLC

Distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

SPDX-License-Identifier: [Apache-2.0](https://spdx.org/licenses/Apache-2.0)