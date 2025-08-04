# Connection Service

The Connection Service is a component at the service layer of the BDK which aims to cover the Connections part of the [REST API documentation](https://developers.symphony.com/restapi/reference).
More precisely:
* [Get connection](https://rest-api.symphony.com/main/connections/get-connection)
* [List connections](https://rest-api.symphony.com/main/connections/list-connections)
* [Create connection](https://rest-api.symphony.com/main/connections/create-connection)
* [Accept connection](https://rest-api.symphony.com/main/connections/accepted-connection)
* [Reject connection](https://rest-api.symphony.com/main/connections/reject-connection)
* [Remove connection](https://rest-api.symphony.com/main/connections/remove-connection)


## How to use
The central component for the Connection Service is the `ConnectionService` class.
This class exposes the user-friendly service APIs which serve all the services mentioned above 
and is accessible from the `SymphonyBdk` object by calling the `connections()` method:
```python
class ConnectionMain:
    @staticmethod
    async def run():
        bdk_config = BdkConfigLoader.load_from_file("path/to/config.yaml")
        async with SymphonyBdk(bdk_config) as bdk:
            connection_service = bdk.connections()
            user_connections = await connection_service.list_connections()
            print(user_connections)


if __name__ == "__main__":
    asyncio.run(ConnectionMain.run())
```

You can check more examples
[here](https://github.com/finos/symphony-bdk-python/blob/main/examples/services/connection.py)
