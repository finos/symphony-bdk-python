# symphony-api-client-python

## Overview
This Symphony bot client is written in an event handler architecture. The client keeps polling a datafeed and responds to different types of [Real Time Events](https://rest-api.symphony.com/docs/real-time-events) it receives.

To build a functional bot which responds to different types of incoming messages from datafeed (Connection, IM, Chat Room, etc....), the respective
type of listener needs to be implemented by inheriting the interfaces in the **listeners** folder. Currently **ConnectionListener**, **imListener**, **RoomListener** interfaces are provided.

## Environment Setup
This client is compatible with **Python 3.6 or above**

Create a virtual environment by executing the following command **(optional)**:
``python -m venv ./venv``

Activate the virtual environment **(optional)**:
``source ./venv/bin/activate``

Install dependencies required for this client by executing the command below.
``pip install -r requirements.txt``

## Getting Started
### 1 - Prepare the service account
The Python client operates using a [Symphony Service Account](https://support.symphony.com/hc/en-us/articles/360000720863-Create-a-new-service-account), which is a type of account that applications use to work with Symphony APIs. Please contact with Symphony Admin in your company to get the account.

The client currently supports two types of Service Account authentications, they are
[Client Certificates Authentication](https://symphony-developers.symphony.com/symphony-developer/docs/bot-authentication-workflow#section-authentication-using-client-certificates)
and [RSA Public/Private Key Pair Authentication](https://symphony-developers.symphony.com/symphony-developer/docs/rsa-bot-authentication-workflow).

### 2 - Implement the event listeners
As an example, the **roomListenerTestImp** has been implemented to respond with "Hello World", to a chat room in which there is an incoming message. To respond to other types of events, respective Listeners need to be implemented.

### 3.1 - Run bot with RSA Public/Private Key Pair
**RSA Public/Private Key Pair** is the recommended authentication mechanism by Symphony, due to its robust security and simplicity.

To run the bot using the **RSA Public/Private Key Pair**, a **rsa_config.json** should be provided. In our example, the json file resides in the
**resources** folder but it can be anywhere.

An example **main_RSA.py** has been provided to illustrate how all components work together.

**Notes:**
Most of the time, the **port numbers** do not need to be changed.

An example of json has been provided below.  (The "botRSAPath" ends with a trailing "/")

    {
      "sessionAuthHost": "MY_ENVIRONMENT.symphony.com",
      "sessionAuthPort": 443,
      "keyAuthHost": "MY_ENVIRONMENT.symphony.com",
      "keyAuthPort": 443,
      "podHost": "MY_ENVIRONMENT.symphony.com",
      "podPort": 443,
      "agentHost": "MY_ENVIRONMENT.symphony.com",
      "agentPort": 443,
      "botRSAPath":"./sym_api_client_python/resources/",
      "botRSAName": "bot_private_key.pem",
      "botUsername": "YOUR_BOT_USERNAME",
      "botEmailAddress": "YOUR_BOT_EMAIL_ADDRESS",
      "appCertPath": "",
      "appCertName": "",
      "appCertPassword": "",
      "proxyURL": "",
      "proxyPort": "",
      "proxyUsername": "",
      "proxyPassword": "",
      "authTokenRefreshPeriod": "30"
    }


### Example main class (using RSA)
Adjust the following paths in the sample to match your configuration
 - "sym_api_client_python/logs/example.log"
 - "sym_api_client_python/resources/config.json"

Example Main Class:

    import logging
    from sym_api_client_python.configure.configure import SymConfig
    from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
    from sym_api_client_python.clients.sym_bot_client import SymBotClient
    from sym_api_client_python.listeners.\
            im_listener_test_imp import IMListenerTestImp
    from sym_api_client_python.listeners.\
            room_listener_test_imp import RoomListenerTestImp


    def configure_logging():
            logging.basicConfig(
                    filename='sym_api_client_python/logs/example.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='w', level=logging.DEBUG
            )
            logging.getLogger("urllib3").setLevel(logging.WARNING)


    def main():
            print('Python Client runs using RSA authentication')

            # Configure log
            configure_logging()

            # RSA Auth flow: pass path to rsa_config.json file
            configure = SymConfig('sym_api_client_python/resources'
                                  '/rsa_config.json')
            configure.load_rsa_config()
            auth = SymBotRSAAuth(configure)
            auth.authenticate()

            # Initialize SymBotClient with auth and configure objects
            bot_client = SymBotClient(auth, configure)

            # Initialize datafeed service
            datafeed_event_service = bot_client.get_datafeed_event_service()

            # Initialize listener objects and append them to datafeed_event_service
            # Datafeed_event_service polls the datafeed and the event listeners
            # respond to the respective types of events
            im_listener_test = IMListenerTestImp(bot_client)
            datafeed_event_service.add_im_listener(im_listener_test)
            room_listener_test = RoomListenerTestImp(bot_client)
            datafeed_event_service.add_room_listener(room_listener_test)

            # Create and read the datafeed
            print('Starting datafeed')
            datafeed_event_service.start_datafeed()


    if __name__ == "__main__":
        main()

### 3.2 - Run bot with Certificates
To run the bot using the **Client Certificates Authentication**, a **config.json** should be provided. In our example, the json file resides in the
**resources** folder but it can be anywhere.

An example **main_certificate.py** has been provided to illustrate how all components work together.

**Notes:**
Most of the time, the **port numbers** do not need to be changed.

An example of json has been provided below. (The "botCertPath" ends with a trailing "/")

    {
      "sessionAuthHost": "MY_ENVIRONMENT-api.symphony.com",
      "sessionAuthPort": 443,
      "keyAuthHost": "MY_ENVIRONMENT-api.symphony.com",
      "keyAuthPort": 443,
      "podHost": "MY_ENVIRONMENT.symphony.com",
      "podPort": 443,
      "agentHost": "MY_ENVIRONMENT.symphony.com",
      "agentPort": 443,
      "botCertPath": "./sym_api_client_python/resources/certificates/",
      "botCertName": "my_bot_cert.p12",
      "botCertPassword": "YOUR_PASSWORD",
      "botEmailAddress": "YOUR_BOT_EMAIL_ADDRESS",
      "appCertPath": "",
      "appCertName": "",
      "appCertPassword": "",
      "proxyURL": "",
      "proxyPort": 8080,
      "proxyUsername": "",
      "proxyPassword": "",
      "authTokenRefreshPeriod": "30"
    }

### Run with Example main class (using certificates)
Once the certificates are provided and example listeners are implemented, let's run the bot by executing following command:

``python3 main_certificate.py``.

Change the paths to both **log**, and **config.json**
 - "sym_api_client_python/logs/example.log"
 - "sym_api_client_python/resources/config.json"

Example Main Class:

    import logging
    from sym_api_client_python.configure.configure import SymConfig
    from sym_api_client_python.auth.auth import Auth
    from sym_api_client_python.clients.sym_bot_client import SymBotClient
    from sym_api_client_python.listeners.im_listener_test_imp import \
            IMListenerTestImp
    from sym_api_client_python.listeners.room_listener_test_imp import \
            RoomListenerTestImp


    def configure_logging():
            logging.basicConfig(
                    filename='sym_api_client_python/logs/example.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='w', level=logging.DEBUG)
            logging.getLogger("urllib3").setLevel(logging.WARNING)


    def main():
            print('Python Client runs using certificate authentication')
            # Configure log
            configure_logging()

            # Certificate Auth flow: Pass in path to config file
            configure = SymConfig('sym_api_client_python/resources/config.json')
            configure.load_cert_config()
            auth = Auth(configure)
            auth.authenticate()

            # Initialize SymBotClient with auth and configure objects
            bot_client = SymBotClient(auth, configure)

            # Initialize datafeed service
            datafeed_event_service = bot_client.get_datafeed_event_service()

            # Initialize listener objects and append them to datafeed_event_service
            # Datafeed_event_service polls the datafeed and the event listeners
            # respond to the respective types of events
            im_listener_test = IMListenerTestImp(bot_client)
            datafeed_event_service.add_im_listener(im_listener_test)
            room_listener_test = RoomListenerTestImp(bot_client)
            datafeed_event_service.add_room_listener(room_listener_test)

            # create data feed and read datafeed continuously in while loop.
            print('starting datafeed')
            datafeed_event_service.start_datafeed()


    if __name__ == "__main__":
        main()



### 4 - Interacting with the joke bot!
The joke bot shows how a Symphony chat bot application works. In general, a chat bot application keeps polling the [datafeed](https://rest-api.symphony.com/reference#read-messagesevents-stream-v4) API for new messages, then it sends the messages to listeners to handle,
depending on the message type.

To interact with the joke bot, try ``/bot joke``

Symphony REST API offer a range of capabilities for application to integrate, visit the [official documentation](https://rest-api.symphony.com/reference) for more information.

# Release Notes
## 0.1.12
- The updates in this release may break your existing bot implementation.  Please ensure you review and test against this client prior to deployment in Production.
- Extensively renamed client libraries to follow PEP8 Python standard.  Naming now follows "snake_case" convention.
- Bug fixes.
