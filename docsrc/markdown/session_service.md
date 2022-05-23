# Session service
The Session Service is a component at the service layer of the BDK which covers the Session part of the [REST API documentation](https://developers.symphony.com/restapi/reference).
More precisely:
* [Get session](https://developers.symphony.com/restapi/reference/session-info-v2)


## How to use
The central component for the Session Service is the `SessionService` class, it exposes the service APIs endpoints mentioned above.  
The service is accessible from the`SymphonyBdk` object by calling the `sessions()` method:

```python
class SessionMain:
    @staticmethod
    async def run():
        bdk_config = BdkConfigLoader.load_from_file("path/to/config.yaml")
        async with SymphonyBdk(bdk_config) as bdk:
            sessions_service = bdk.sessions()
            session_info = await sessions_service.get_session()
            print(session_info)


if __name__ == "__main__":
    asyncio.run(SessionMain.run())