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
