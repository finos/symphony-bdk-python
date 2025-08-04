# Signal Service

The Signal Service is a component at the service layer of the BDK which aims to cover the Signal part of the [REST API documentation](https://developers.symphony.com/restapi/reference).
More precisely:
* [List signals](https://rest-api.symphony.com/main/signals/list-signals)
* [Get a signal](https://rest-api.symphony.com/main/signals/get-signal)
* [Create a signal](https://rest-api.symphony.com/main/signals/create-signal)
* [Update a signal](https://rest-api.symphony.com/main/signals/update-signal)
* [Delete a signal](https://rest-api.symphony.com/main/signals/delete-signal)
* [Subscribe Signal](https://rest-api.symphony.com/main/signals/subscribe-signal)
* [Unsubscribe Signal](https://rest-api.symphony.com/main/signals/unsubscribe-signal)
* [Subscribers](https://rest-api.symphony.com/main/signals/subscribers)


## How to use
The central component for the Signal Service is the `SignalService` class.
This class exposes the user-friendly service APIs which serve all the services mentioned above
and is accessible from the `SymphonyBdk` object by calling the `signals()` method:
```python
class ApplicationMain:
    @staticmethod
    async def run():
        bdk_config = BdkConfigLoader.load_from_file("path/to/config.yaml")
        async with SymphonyBdk(bdk_config) as bdk:
            signal_service = bdk.signals()
            signal_list = await signal_service.list_signals()
            print(signal_list)


if __name__ == "__main__":
    asyncio.run(ApplicationMain.run())
```
