# Connection Service

The Connection Service is a component at the service layer of the BDK which aims to cover the Connections part of the [REST API documentation](https://developers.symphony.com/restapi/reference).
More precisely:
* [Get connection](https://developers.symphony.com/restapi/reference#get-connection)
* [List connections](https://developers.symphony.com/restapi/reference#list-connections)
* [Create connection](https://developers.symphony.com/restapi/reference#create-connection)
* [Accept connection](https://developers.symphony.com/restapi/reference#accepted-connection)
* [Reject connection](https://developers.symphony.com/restapi/reference#reject-connection)
* [Remove connection](https://developers.symphony.com/restapi/reference#remove-connection)


## How to use
The central component for the Message Service is the `ConnectionService` class.
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
[here](https://github.com/SymphonyPlatformSolutions/symphony-api-client-python/blob/2.0/examples/connection.py)
