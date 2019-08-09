import sys

def is_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

if is_venv():
    print('In virtual environment. Proceeding.')
else:
    print('Not running in virtual environment. Consider exiting program with ctrl-c') 
    print('Docs for setting up virtual environment:')
    print('https://docs.python.org/3/library/venv.html')

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
                filename='./logs/example.log',
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                filemode='w', level=logging.DEBUG
        )
        logging.getLogger("urllib3").setLevel(logging.WARNING)


def main():
        print('Python Client runs using Cert authentication')

        # Configure log
        configure_logging()

        # Cert Auth flow: pass path to certificate config.json file
        configure = SymConfig('../resources/config.json')
        configure.load_config()
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

        # Create and read the datafeed
        print('Starting datafeed')
        datafeed_event_service.start_datafeed()


if __name__ == "__main__":
    main()

