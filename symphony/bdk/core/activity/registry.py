import logging

from symphony.bdk.core.activity.api import AbstractActivity
from symphony.bdk.core.activity.command import CommandActivity, CommandContext
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent

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
        """
        Registers an activity.

        Args:
            activity: any object inheriting from base :class:`AbstractActivity`
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
            act.before_matcher(context)
            if isinstance(act, CommandActivity) and act.matches(context):
                await act.on_activity(context)
