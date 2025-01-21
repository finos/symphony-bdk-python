# Connection Service

The Presence Service is a component at the service layer of the BDK which covers the Presence part of the [REST API documentation](https://developers.symphony.com/restapi/reference).
More precisely:
* [Get presence](https://developers.symphony.com/restapi/reference#get-presence)
* [Get All Presence](https://developers.symphony.com/restapi/reference#get-all-presence)
* [Get User Presence](https://developers.symphony.com/restapi/reference#user-presence-v3)
* [External Presence Interest](https://developers.symphony.com/restapi/reference#register-user-presence-interest)
* [Set Presence](https://developers.symphony.com/restapi/reference#set-presence)
* [Create Presence Feed](https://developers.symphony.com/restapi/reference#create-presence-feed)
* [Read Presence Feed](https://developers.symphony.com/restapi/reference#read-presence-feed)
* [Delete Presence Feed](https://developers.symphony.com/restapi/reference#delete-presence-feed)
* [Set Other User's Presence](https://developers.symphony.com/restapi/reference#set-user-presence)


## How to use
The central component for the Presence Service is the `PresenceService` class, it exposes the service APIs endpoints mentioned above.  
The service is accessible from the`SymphonyBdk` object by calling the `presence()` method:

```python
class PresenceMain:
    @staticmethod
    async def run():
        bdk_config = BdkConfigLoader.load_from_file("path/to/config.yaml")
        async with SymphonyBdk(bdk_config) as bdk:
            presence_service = bdk.presence()
            presence = await presence_service.get_presence()
            print(presence)


if __name__ == "__main__":
    asyncio.run(PresenceMain.run())
```