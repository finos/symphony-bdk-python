# Message Service

The Message Service is a component at the service layer of the BDK which aims to cover the Messages part of the [REST API documentation](https://developers.symphony.com/restapi/reference#messages-v4).
More precisely:
* [Get a message](https://developers.symphony.com/restapi/reference#get-message-v1)
* [Get messages](https://developers.symphony.com/restapi/reference#messages-v4)
* [Get message IDs by timestamp](https://developers.symphony.com/restapi/reference#get-message-ids-by-timestamp)
* [Send message](https://developers.symphony.com/restapi/reference#create-message-v4)
* [Import messages](https://developers.symphony.com/restapi/reference#import-message-v4)
* [Get attachment](https://developers.symphony.com/restapi/reference#attachment)
* [List attachments](https://developers.symphony.com/restapi/reference#list-attachments)
* [Get allowed attachment types](https://developers.symphony.com/restapi/reference#attachment-types)
* [Suppress message](https://developers.symphony.com/restapi/reference#suppress-message)
* [Get message status](https://developers.symphony.com/restapi/reference#message-status)
* [Get message receipts](https://developers.symphony.com/restapi/reference#list-message-receipts)
* [Get message relationships](https://developers.symphony.com/restapi/reference#message-metadata-relationship)

## How to use
The central component for the Message Service is the `MessageService` class.
This class exposes the user-friendly service APIs which serve all the services mentioned above 
and is accessible from the `SymphonyBdk` object by calling the `messages()` method:
```python
class MessageMain:

    @staticmethod
    async def run():
        stream_id_1 = "stream-id-1"

        bdk_config = BdkConfigLoader.load_from_file("path/to/config.yaml")
        bdk = SymphonyBdk(bdk_config)
        try:
            message_service = await bdk.messages()
            with open("/path/to/attachment1", "rb") as file1, \
                    open("/path/to/attachment2", "rb") as file2:
                await message_service.send_message(
                    stream_id_1,
                    "<messageML>Hello, World!</messageML>",
                    attachment=[file1, file2]
                )

        finally:
            await bdk.close_clients()


if __name__ == "__main__":
    asyncio.run(MessageMain.run())
```
