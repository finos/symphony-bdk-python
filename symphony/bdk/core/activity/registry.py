import logging

from symphony.bdk.gen.agent_model.v4_user_joined_room import V4UserJoinedRoom

from symphony.bdk.core.activity.api import AbstractActivity
from symphony.bdk.core.activity.command import CommandActivity, CommandContext
from symphony.bdk.core.activity.form import FormReplyContext, FormReplyActivity
from symphony.bdk.core.activity.user_joined_room import UserJoinedRoomContext, UserJoinedRoomActivity
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_symphony_elements_action import V4SymphonyElementsAction

logger = logging.getLogger(__name__)


class ActivityRegistry(RealTimeEventListener):
    """
    This class allows to bind an py:class::`AbstractActivity` to the Real Time Events source, or Datafeed.
    It also maintains the list of registered activities.
    """

    def __init__(self, session_service: SessionService):
        self._activity_list = []
        self._session_service = session_service
        self._bot_display_name = None

    async def register(self, activity: AbstractActivity):
        """Registers an activity.

        :param activity: any object inheriting from base :class:`AbstractActivity`
        """

        logger.debug('Registering new activity %s', activity)

        if self._bot_display_name is None:
            session = await self._session_service.get_session()
            self._bot_display_name = session.display_name
            logger.debug('Bot display name is : %s', self._bot_display_name)

        self._activity_list.append(activity)

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        context = CommandContext(initiator, event, self._bot_display_name)
        for act in self._activity_list:
            if isinstance(act, CommandActivity):
                act.before_matcher(context)
                if act.matches(context):
                    await act.on_activity(context)

    async def on_symphony_elements_action(self, initiator: V4Initiator, event: V4SymphonyElementsAction):
        context = FormReplyContext(initiator, event)
        for act in self._activity_list:
            if isinstance(act, FormReplyActivity):
                act.before_matcher(context)
                if act.matches(context):
                    await act.on_activity(context)

    async def on_user_joined_room(self, initiator: V4Initiator, event: V4UserJoinedRoom):
        context = UserJoinedRoomContext(initiator, event)
        for act in self._activity_list:
            if isinstance(act, UserJoinedRoomActivity):
                act.before_matcher(context)
                if act.matches(context):
                    await act.on_activity(context)
