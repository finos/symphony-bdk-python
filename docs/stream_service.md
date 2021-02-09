# Stream Service

The Stream Service is a component at the service layer of the BDK which aims to cover the Streams part of the [REST API documentation](https://developers.symphony.com/restapi/reference#messages-v4).
More precisely:
* [Get stream information](https://developers.symphony.com/restapi/reference#stream-info-v2)
* [Add a member to an existing room](https://developers.symphony.com/restapi/reference#add-member)
* [Remove a member from a room](https://developers.symphony.com/restapi/reference#remove-member)
* [Share third-party content](https://developers.symphony.com/restapi/reference#share-v3)
* [Promote user to room owner](https://developers.symphony.com/restapi/reference#promote-owner)
* [Demote owner to room participant](https://developers.symphony.com/restapi/reference#demote-owner)
* [Create IM or MIM](https://developers.symphony.com/restapi/reference#create-im-or-mim)
* [Create IM or MIM non-inclusive](https://developers.symphony.com/restapi/reference#create-im-or-mim-admin)
* [Create room](https://developers.symphony.com/restapi/reference#create-room-v3)
* [Search for rooms](https://developers.symphony.com/restapi/reference#search-rooms-v3)
* [Get room information](https://developers.symphony.com/restapi/reference#room-info-v3)
* [Deactivate or reactivate a room](https://developers.symphony.com/restapi/reference#de-or-re-activate-room)
* [Update a room](https://developers.symphony.com/restapi/reference#update-room-v3)
* [List streams](https://developers.symphony.com/restapi/reference#list-streams-for-enterprise-v2)
* [List user streams](https://developers.symphony.com/restapi/reference#list-user-streams)
* [List stream members](https://developers.symphony.com/restapi/reference#stream-members)
* [List room members](https://developers.symphony.com/restapi/reference#room-members)


## How to use
The central component for the Message Service is the `StreamService` class.
This class exposes the user-friendly service APIs which serve all the services mentioned above 
and is accessible from the `SymphonyBdk` object by calling the `streams()` method:
```python
class StreamMain:

    @staticmethod
    async def run():
        stream_id_1 = "stream-id-1"

        bdk_config = BdkConfigLoader.load_from_file("path/to/config.yaml")

        async with SymphonyBdk(bdk_config) as bdk:
            stream_service = bdk.streams()
            stream = await stream_service.get_stream("stream_id")


if __name__ == "__main__":
    asyncio.run(MessageMain.run())
```

You can check more examples [here](../examples/core/service/stream_main.py)
