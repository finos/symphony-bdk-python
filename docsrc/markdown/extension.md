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
Developers that wish to use these objects are free to implement a set of abstract base classes all suffixed with the `Aware` keyword.

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
The abc `symphony.bdk.core.extension.BdkApiClientFactoryAware` can be used by extensions that need to
use the `ApiClientFactory`: 
```python
class MyBdkExtension(BdkApiClientFactoryAware):
    def __init__(self):
        self._api_client_factory = None
        
    def set_api_client_factory(self, api_client_factory):
        self._api_client_factory = api_client_factory
```

### `BdkAuthenticationAware`
The abc `symphony.bdk.core.extension.BdkAuthenticationAware` can be used by extensions that need to rely on the 
service account authentication session (`AuthSession`), which provides the `sessionToken` and 
`keyManagerToken` that are used to call the Symphony's APIs: 
```python
class MyBdkExtension(BdkAuthenticationAware):
    def __init__(self):
        self._auth_session = None
        
    def set_auth_session(self, auth_session):
        self._auth_session = auth_session
```
