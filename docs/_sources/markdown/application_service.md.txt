# Application Service

The Application Service is a component at the service layer of the BDK which aims to cover the Applications part of the [REST API documentation](https://developers.symphony.com/restapi/reference).
More precisely:
* [Create application](https://developers.symphony.com/restapi/reference#create-app)
* [Create application with an RSA public key](https://developers.symphony.com/restapi/reference#create-application-with-an-rsa-public-key)
* [Update application](https://developers.symphony.com/restapi/reference#update-application)
* [Update application with an RSA public key](https://developers.symphony.com/restapi/reference#update-application-with-an-rsa-public-key)
* [Delete application](https://developers.symphony.com/restapi/reference#delete-application)
* [Get application](https://developers.symphony.com/restapi/reference#get-application)
* [List application entitlements](https://developers.symphony.com/restapi/reference#list-app-entitlements)
* [Update application entitlements](https://developers.symphony.com/restapi/reference#update-application-entitlements)
* [List user applications](https://developers.symphony.com/restapi/reference#user-apps)
* [Update user applications](https://developers.symphony.com/restapi/reference#update-user-apps)
* [Patch user applications](https://developers.symphony.com/restapi/reference/partial-update-user-apps)


## How to use
The central component for the Application Service is the `ApplicationService` class.
This class exposes the user-friendly service APIs which serve all the services mentioned above
and is accessible from the `SymphonyBdk` object by calling the `applications()` method:
```python
class ApplicationMain:
    @staticmethod
    async def run():
        bdk_config = BdkConfigLoader.load_from_file("path/to/config.yaml")
        async with SymphonyBdk(bdk_config) as bdk:
            application_service = bdk.applications()
            app_entitlements = await application_service.list_application_entitlements()
            print(app_entitlements)


if __name__ == "__main__":
    asyncio.run(ApplicationMain.run())
```
