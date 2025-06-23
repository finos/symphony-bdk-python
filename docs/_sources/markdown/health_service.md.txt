# Health service
The Health Service is a component at the service layer of the BDK which covers the Health Service part of the [REST API documentation](https://developers.symphony.com/restapi/reference).
More precisely:
* [Health check](https://developers.symphony.com/restapi/reference/health-check-v3)
* [Health check extended](https://developers.symphony.com/restapi/reference/health-check-extended-v3)
* [Agent info](https://developers.symphony.com/restapi/reference/agent-info-v1)


## How to use
The central component for the Health Service is the `HealthService` class, it exposes the service APIs endpoints mentioned above.  
The service is accessible from the`SymphonyBdk` object by calling the `health()` method:

```python
class HealthMain:
    @staticmethod
    async def run():
        bdk_config = BdkConfigLoader.load_from_file("path/to/config.yaml")
        async with SymphonyBdk(bdk_config) as bdk:
            health_service = bdk.health()
            health = await health_service.health_check_extended()
            print(health)


if __name__ == "__main__":
    asyncio.run(HealthMain.run())
```