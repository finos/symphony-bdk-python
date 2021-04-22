from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator

C = TypeVar('C')  # Context type
E = TypeVar('E')  # Event type


class ActivityContext(Generic[E]):
    """
    Base class for any activity context holder.
    """

    def __init__(self, initiator: V4Initiator, source_event: E):
        """

        :param initiator: The activity initiator  (i.e. the Symphony user that triggered an event in the chat)
        :param source_event: The activity source real-time event.
        """
        self._initiator = initiator
        self._source_event = source_event

    @property
    def initiator(self):
        """

        :return: The activity initiator  (i.e. the Symphony user that triggered an event in the chat)
        """
        return self._initiator

    @property
    def source_event(self):
        """

        :return: The activity source real-time event.
        """
        return self._source_event


class AbstractActivity(ABC, Generic[C]):
    """
    Base abstract class for activities provided by the BDK. Provides a generic flow to process an incoming chat event.
    """

    @abstractmethod
    def matches(self, context: C) -> bool:
        """Matches the :py:class:`ActivityContext` to decide whether an :py:class:`AbstractActivity` can be executed
        or not.

        :param context: an instance of :py:class:`ActivityContext`
        :return: True if activity has to be triggered, False otherwise.
        """

    @abstractmethod
    def on_activity(self, context: C):
        """Contains the activity business logic. Executed only if the `matches` method returned a true value.

        :param context: an instance of :py:class:`ActivityContext`
        """

    def before_matcher(self, context: C):
        """ This callback can be used to prepare :py:class:`ActivityContext` before actually processing the `matches`
        method.

        :param context: an instance of :py:class:`ActivityContext`
        """
