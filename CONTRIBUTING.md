# How to contribute

If you found a bug or issue, please ensure the bug was not already reported by searching in
[GitHub issues](https://github.com/SymphonyPlatformSolutions/symphony-api-client-python/issues).
If you are unable to find an open issue addressing the problem, open a new one.
Be sure to include a title and clear description, the SDK version, and a code sample demonstrating the issue.

If you open a PR to fix any issue, please reference the ticket in the PR title.
A [Symphony SDK team](https://github.com/orgs/SymphonyPlatformSolutions/teams/symphony-sdk/members) member
will have to approve before it is merged and eventually released.

## Module and package structure

Source code is divided into three main packages:
* [sym_api_client_python](sym_api_client_python) which contains the SDK source code;
* [tests](tests) which contains unit tests;
* [examples](examples) which contains code samples illustrating SDK basic usage.

## Testing

Unit tests should be added or updated each time a PR is submitted.

## Coding guidelines

The guidelines outlined in [PEP 8](https://www.python.org/dev/peps/pep-0008/) should be followed on any code update.

## Documentation

Public classes and methods should be properly documented using javadoc. Main features should be documented using
[Markdown](https://daringfireball.net/projects/markdown/) under the [docs folder](docs)
and exemplified with runnable code under the [examples package](examples).
