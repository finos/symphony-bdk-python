# Datafeed

The datafeed service is a service used for handling the [_Real Time Events_](https://developers.symphony.com/restapi/docs/real-time-events). 

When a user makes an interaction within the IM, MIM or Room chat like sending a message, joining or leaving a room chat..., 
when a connection request is sent, when a wall post is published or when a user replies an Symphony element, an event will be sent to the datafeed.

The datafeed service is a core service built on top of the Datafeed API and provides a dedicated contract to bot developers to work with datafeed. 


## How to use
The central component for the contract between bot developers and the Datafeed API is the `DatafeedLoop`.
This service is accessible from the `SymphonyBdk` object by calling the `datafeed()` method.
For instance:

```python
async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
    datafeed_loop = bdk.datafeed()
        
    await datafeed_loop.start()
```