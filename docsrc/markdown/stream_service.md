# Stream Service

The Stream Service is a component at the service layer of the BDK which aims to cover the Streams part of the [REST API documentation](https://developers.symphony.com/restapi/reference#messages-v4).
More precisely:
* [Get stream information](https://rest-api.symphony.com/main/streams-conversations/all-streams-endpoints/stream-info-v2)
* [Add a member to an existing room](https://rest-api.symphony.com/main/streams-conversations/room-endpoints/add-member)
* [Remove a member from a room](https://rest-api.symphony.com/main/streams-conversations/room-endpoints/remove-member)
* [Share third-party content](https://rest-api.symphony.com/main/streams-conversations/all-streams-endpoints/share-v3)
* [Promote user to room owner](https://rest-api.symphony.com/main/streams-conversations/room-endpoints/promote-owner)
* [Demote owner to room participant](https://rest-api.symphony.com/main/streams-conversations/room-endpoints/demote-owner)
* [Create IM or MIM](https://rest-api.symphony.com/main/streams-conversations/im-mim-endpoints/create-im-or-mim)
* [Create IM or MIM non-inclusive](https://rest-api.symphony.com/main/streams-conversations/im-mim-endpoints/create-im-or-mim-admin)
* [Update IM or MIM](https://rest-api.symphony.com/main/streams-conversations/im-mim-endpoints/update-im)
* [Get IM information](https://rest-api.symphony.com/main/streams-conversations/im-mim-endpoints/im-info)
* [Create room](https://rest-api.symphony.com/main/streams-conversations/room-endpoints/create-room-v3)
* [Search for rooms](https://rest-api.symphony.com/main/streams-conversations/room-endpoints/search-rooms-v3)
* [Get room information](https://rest-api.symphony.com/main/streams-conversations/room-endpoints/room-info-v3)
* [Deactivate or reactivate a room](https://rest-api.symphony.com/main/streams-conversations/room-endpoints/de-or-re-activate-room)
* [Update a room](https://rest-api.symphony.com/main/streams-conversations/room-endpoints/update-room-v3)
* [List streams](https://rest-api.symphony.com/main/streams-conversations/all-streams-endpoints/list-user-streams-admin)
* [List user streams](https://rest-api.symphony.com/main/streams-conversations/all-streams-endpoints/list-user-streams)
* [List stream members](https://rest-api.symphony.com/main/streams-conversations/all-streams-endpoints/stream-members)
* [List room members](https://rest-api.symphony.com/main/streams-conversations/room-endpoints/room-members)
* [List user streams (admin)](https://rest-api.symphony.com/main/streams-conversations/all-streams-endpoints/list-user-streams-admin)

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
    asyncio.run(StreamMain.run())
```

You can check more examples
[here](https://github.com/finos/symphony-bdk-python/blob/main/examples/services/streams.py)
