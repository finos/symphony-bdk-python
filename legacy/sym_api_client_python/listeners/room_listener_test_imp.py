import asyncio
import logging
from .room_listener import RoomListener
from .simple_message_processor import MessageProcessor
from sym_api_client_python.processors.sym_message_parser import SymMessageParser
# A sample implementation of Abstract RoomListener class
# The listener can respond to incoming events if the respective event
# handler has been implemented


class RoomListenerTestImp(RoomListener):
    """Example implementation of RoomListener

        sym_bot_client: contains clients which respond to incoming events

    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client

    def on_room_msg(self, msg):
        logging.debug('room msg received', msg)
        msg_processor = MessageProcessor(self.bot_client)
        msg_processor.process(msg)

    def on_room_created(self, room_created):
        logging.debug('room created', room_created)

    def on_room_deactivated(self, room_deactivated):
        logging.debug('room Deactivated', room_deactivated)

    def on_room_member_demoted_from_owner(self,
                                          room_member_demoted_from_owner):
        logging.debug('room member demoted from owner',
                      room_member_demoted_from_owner)

    def on_room_member_promoted_to_owner(self, room_member_promoted_to_owner):
        logging.debug('room member promoted to owner',
                      room_member_promoted_to_owner)

    def on_room_reactivated(self, room_reactivated):
        logging.debug('room reactivated', room_reactivated)

    def on_room_updated(self, room_updated):
        logging.debug('room updated', room_updated)

    def on_user_joined_room(self, user_joined_room):
        logging.debug('USER JOINED ROOM', user_joined_room)

    def on_user_left_room(self, user_left_room):
        logging.debug('USER LEFT ROOM', user_left_room)


class AsyncRoomListenerImp(RoomListener):
    """Example implementation of RoomListener with asynchronous functionality
        
    Call the bot with /wait to see an example of a non-blocking wait
    """

    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client
        self.message_parser = SymMessageParser()

    async def on_room_msg(self, msg):
        logging.debug('room msg received', msg)

        await asyncio.sleep(5)

        msg_text = self.message_parser.get_text(msg)

        if "/wait" in msg_text:
            await asyncio.sleep(5)
            msg_to_send = dict(
                    message='<messageML>Hello {}, sorry to keep you waiting!</messageML>'.format(
                        self.message_parser.get_im_first_name(msg))
                    )
        else:
            msg_to_send = dict(
                    message='<messageML>Hello {}, hope you are doing well!</messageML>'.format(
                        self.message_parser.get_im_first_name(msg))
                    )

        if msg_text:
            stream_id = self.message_parser.get_stream_id(msg)
            self.bot_client.get_message_client(). \
                    send_msg(stream_id, msg_to_send)


    async def on_room_created(self, room_created):
        logging.debug('room created', room_created)

    async def on_room_deactivated(self, room_deactivated):
        logging.debug('room Deactivated', room_deactivated)

    async def on_room_member_demoted_from_owner(self,
                                          room_member_demoted_from_owner):
        logging.debug('room member demoted from owner',
                      room_member_demoted_from_owner)

    async def on_room_member_promoted_to_owner(self, room_member_promoted_to_owner):
        logging.debug('room member promoted to owner',
                      room_member_promoted_to_owner)

    async def on_room_reactivated(self, room_reactivated):
        logging.debug('room reactivated', room_reactivated)

    async def on_room_updated(self, room_updated):
        logging.debug('room updated', room_updated)

    async def on_user_joined_room(self, user_joined_room):
        logging.debug('USER JOINED ROOM', user_joined_room)

    async def on_user_left_room(self, user_left_room):
        logging.debug('USER LEFT ROOM', user_left_room)
