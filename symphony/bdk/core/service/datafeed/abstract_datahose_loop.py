import logging
from abc import ABC, abstractmethod

from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener

logger = logging.getLogger(__name__)


class AbstractDatahoseLoop(ABC):
    """Base class for implementing the datahose services.

        A datahose service can help a bot to get all the received real-time events that are set
        as filters in the configuration.
    """

    @abstractmethod
    async def start(self):
        """Start the datahose event service

        :return: None
        """

    @abstractmethod
    async def stop(self, hard_kill: bool = False, timeout: float = None):
        """Stop the datahose event service

        :param hard_kill: if set to True, tasks running listener methods will be cancelled immediately. Otherwise, tasks
          will be awaited until completion.
        :param timeout: timeout in seconds to wait for tasks completion when loop stops.
          None means wait until completion. Ignored if hard_kill set to True.
        :return: None
        """

    @abstractmethod
    def subscribe(self, listener: RealTimeEventListener):
        """Subscribes a new listener to the datahose loop instance.

        :param listener: the RealTimeEventListener to be added.
        """

    @abstractmethod
    def unsubscribe(self, listener: RealTimeEventListener):
        """Removes a given listener from the datahose loop instance.

        :param listener: the RealTimeEventListener to be removed.
        """
