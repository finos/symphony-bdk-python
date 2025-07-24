# Application Service

The Application Service is a component at the service layer of the BDK which aims to cover the Applications part of the [REST API documentation](https://developers.symphony.com/restapi/reference).
More precisely:
* [Create application](https://rest-api.symphony.com/main/manage-apps/create-app)
* [Update application](https://rest-api.symphony.com/main/manage-apps/update-application)
* [Delete application](https://rest-api.symphony.com/main/manage-apps/delete-application)
* [Get application](https://rest-api.symphony.com/main/manage-apps/get-application)
* [List application entitlements](https://rest-api.symphony.com/main/apps-entitlements/list-app-entitlements)
* [Update application entitlements](https://rest-api.symphony.com/main/apps-entitlements/update-application-entitlements)
* [List user applications](https://rest-api.symphony.com/main/apps-entitlements/user-apps)
* [Update user applications](https://rest-api.symphony.com/main/apps-entitlements/update-user-apps)
* [Patch user applications](https://rest-api.symphony.com/main/apps-entitlements/partial-update-user-apps)


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
