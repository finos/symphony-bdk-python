# symphony-api-client-python

This is the Symphony BDK for Python to help developing bots and interact with the [Symphony REST APIs](https://developers.symphony.com/restapi/reference).

Legacy Python BDK is located in [legacy](./legacy) folder.

## How to build

We use [poetry](https://python-poetry.org/) in order to manage dependencies, build, run tests and publish.
To install poetry, follow instructions [here](https://python-poetry.org/docs/#installation).

On the first time, run `poetry install`. Then run `poetry build` to build the sdist and wheel packages.
To run the tests, use `poetry run pytest`.
