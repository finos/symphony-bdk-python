# Extension Model

> The BDK Extension Mechanism is still an experimental feature, contracts might be subject to **breaking changes**
> in following versions.

## Overview

The Extension API is available through the module `symphony.bdk.core.extension` but other modules might be required
depending on what your extension needs to use.

## Registering Extensions

Extensions are registered _programmatically_ via the `ExtensionService`:

```python
 async with SymphonyBdk(config) as bdk:
    extension_service = bdk.extensions()
    extension_service.register(MyExtensionType)
```

## Service Provider Extension

A _Service Provider_ extension is a specific type of extension loaded on demand when calling the
`ExtensionService#service(MyExtensionType)` method.

To make your extension _Service Provider_, your extension definition must implement the method `get_service(self)`:

```python
# The Service implementation class.
class MyBdkExtensionService:
    def say_hello(self, name):
        print(f"Hello, {name}!")


# The Extension definition class.
class MyBdkExtension:
    def __init__(self):
        self._service = MyBdkExtensionService()

    def get_service(self):
        return self._service


# Usage example.
async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        extension_service = bdk.extensions()
        extension_service.register(MyBdkExtensionService)

        service = extension_service.service(MyBdkExtensionService)
        service.say_hello("Symphony")


asyncio.run(run())
```

## BDK Aware Extensions

The BDK Extension Model allows extensions to access to some core objects such as the configuration or the api clients.
Developers that wish to use these objects are free to implement a set of abstract base classes all suffixed with
the `Aware` keyword.

If an extension do not extend one of `Aware` classes but implements the corresponding method, the latter will be used as
the `ExtensionService` uses duck typing internally.

### `BdkConfigAware`

The abc `symphony.bdk.core.extension.BdkConfigAware` allows extensions to read the `BdkConfig`:

```python
class MyBdkExtension(BdkConfigAware):
    def __init__(self):
        self._config = None

    def set_config(self, config):
        self._config = config
```

### `BdkApiClientFactoryAware`

The abc `symphony.bdk.core.extension.BdkApiClientFactoryAware` can be used by extensions that need to use
the `ApiClientFactory`:

```python
class MyBdkExtension(BdkApiClientFactoryAware):
    def __init__(self):
        self._api_client_factory = None

    def set_api_client_factory(self, api_client_factory):
        self._api_client_factory = api_client_factory
```

### `BdkAuthenticationAware`

The abc `symphony.bdk.core.extension.BdkAuthenticationAware` can be used by extensions that need to rely on the service
account authentication session (`AuthSession`), which provides the `sessionToken` and
`keyManagerToken` that are used to call the Symphony's APIs:

```python
class MyBdkExtension(BdkAuthenticationAware):
    def __init__(self):
        self._auth_session = None

    def set_auth_session(self, auth_session):
        self._auth_session = auth_session
```

## Retry

In order to leverage the retry mechanism your service class should have the field `self._retry_config` of type
`BdkRetryConfig` and each function that needs a retry mechanism can use the `@retry` decorator. This decorator will
reuse the config declared in `self._retry_config`. 

The default retry mechanism is defined here: [`refresh_session_if_unauthorized`](../_autosummary/symphony.bdk.core.retry.strategy.refresh_session_if_unauthorized.html).
It retries on connection errors (more precisely `ClientConnectionError` and `TimeoutError`) and
on the following HTTP status codes:
* 401
* 429
* codes greater than or equal to 500.

In case of unauthorized, it will call `await self._auth_session.refresh()` before retrying.

Following is a sample code to show how it can be used:
```python
from symphony.bdk.core.extension import BdkExtensionServiceProvider, BdkAuthenticationAware, BdkConfigAware
from symphony.bdk.core.retry import retry

class MyExtension(BdkConfigAware, BdkAuthenticationAware, BdkExtensionServiceProvider):
    def __init__(self):
        self._config = None
        self._auth_session = None

    def set_config(self, config):
        self._config = config

    def set_bot_session(self, auth_session):
        self._auth_session = auth_session

    def get_service(self):
        return MyService(self._config.retry, self._auth_session)


class MyService:
    def __init__(self, retry_config, auth_session):
        self._retry_config = retry_config  # used by the @retry decorator
        self._auth_session = auth_session  # default retry logic will call refresh on self._auth_session

    @retry
    async def my_service_method(self):
        pass  # do stuff which will be retried
```

Retry conditions and mechanism can be customized as follows:
```python
async def my_retry_mechanism(retry_state):
    """Function used by the retry decorator to check if a function call has to be retried.

    :param retry_state: current retry state, of type RetryCallState: https://tenacity.readthedocs.io/en/latest/#retrycallstate
    :return: True if we want to retry, False otherwise
    """
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()  # exception that lead to the failure 
        if condition_on_exception(exception):
            # do stuff to recover the exception
            # method args can be accessed as follows: retry_state.args
            return True  # return True to retry the function
    return False  # return False to not retry and make function call fail

class MyService:
    def __init__(self, retry_config, auth_session):
        self._retry_config = retry_config  # used by the @retry decorator
        self._auth_session = auth_session  # default retry logic will call refresh on self._auth_session

    @retry(retry=my_retry_mechanism)
    async def my_service_method(self):
        pass  # do stuff which will be retried
```
