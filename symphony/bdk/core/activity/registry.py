import logging

from symphony.bdk.core.activity.api import AbstractActivity
from symphony.bdk.core.activity.command import (
    CommandActivity,
    CommandContext,
    SlashCommandActivity,
)
from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext
from symphony.bdk.core.activity.user_joined_room import (
    UserJoinedRoomActivity,
    UserJoinedRoomContext,
)
from symphony.bdk.core.service.datafeed.real_time_event_listener import (
    RealTimeEventListener,
)
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_symphony_elements_action import (
    V4SymphonyElementsAction,
)
from symphony.bdk.gen.agent_model.v4_user_joined_room import V4UserJoinedRoom

logger = logging.getLogger(__name__)


def _initialize_display_name(func):
    """Decorator around :py:class:`~ActivityRegistry` methods which calls
    :py:meth:`~ActivityRegistry.fetch_bot_display_name` before actually executing the instance method.

    :param func: the function to be decorated
    :return: the decorated function
    """

    async def decorator(*args, **kwargs):
        registry = args[0]
        await registry.fetch_bot_info()
        return await func(*args, **kwargs)

    return decorator


class ActivityRegistry(RealTimeEventListener):
    """
    This class allows to bind an py:class::`AbstractActivity` to the Real Time Events source, or Datafeed.
    It also maintains the list of registered activities.
    """

    def __init__(self, session_service: SessionService):
        self._activity_list = []
        self._session_service = session_service
        self._bot_display_name = None
        self._bot_user_id = None

    @property
    def activity_list(self):
        return self._activity_list

    def register(self, activity: AbstractActivity):
        """Registers an activity.

        :param activity: any object inheriting from base :class:`AbstractActivity`
        """
        logger.debug("Registering new activity %s", activity)
        self._pre_process_activity(activity)
        self._activity_list.append(activity)

    def _pre_process_activity(self, activity: AbstractActivity):
        for act in self._activity_list:
            if act == activity:
                self._activity_list.remove(act)
                logger.debug(
                    "Activity '%s' has been removed/unsubscribed in order to be replaced",
                    act,
                )

    def slash(self, command: str, mention_bot: bool = True, description: str = ""):
        """Decorator around a listener callback coroutine which takes a
        :py:class:`~symphony.bdk.core.activity.command.CommandContext` as single parameter and returns nothing.
        This registers a new :py:class:`~symphony.bdk.core.activity.command.SlashCommandActivity`
        which executes the decorated coroutine if a message is matching.

        :param command: the command name e.g. "/hello"
        :param mention_bot: if user should mention the bot to trigger the slash command
        :param description: command description
        :return: None
        """

        def decorator(func):
            logger.debug(
                "Registering slash command with command=%s, mention_bot=%s",
                command,
                mention_bot,
            )
            self.register(SlashCommandActivity(command, mention_bot, func, description))
            return func

        return decorator

    @_initialize_display_name
    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        context = CommandContext(
            initiator, event, self._bot_display_name, self._bot_user_id
        )
        for act in self._activity_list:
            if isinstance(act, CommandActivity):
                act.before_matcher(context)
                if act.matches(context):
                    await act.on_activity(context)

    @_initialize_display_name
    async def on_symphony_elements_action(
        self, initiator: V4Initiator, event: V4SymphonyElementsAction
    ):
        context = FormReplyContext(initiator, event)
        for act in self._activity_list:
            if isinstance(act, FormReplyActivity):
                act.before_matcher(context)
                if act.matches(context):
                    await act.on_activity(context)

    @_initialize_display_name
    async def on_user_joined_room(
        self, initiator: V4Initiator, event: V4UserJoinedRoom
    ):
        context = UserJoinedRoomContext(initiator, event)
        for act in self._activity_list:
            if isinstance(act, UserJoinedRoomActivity):
                act.before_matcher(context)
                if act.matches(context):
                    await act.on_activity(context)

    async def fetch_bot_info(self):
        """Fetches the bot display name if not already done.

        :return: None
        """
        if self._bot_display_name is None:
            session = await self._session_service.get_session()
            self._bot_display_name = session.display_name
            self._bot_user_id = session.id

            for activity in self._activity_list:
                activity.bot_user_id = self._bot_user_id

            logger.debug("Bot display name is : %s", self._bot_display_name)
