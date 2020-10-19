import logging
import json

from .abstract_datafeed_event_service import AbstractDatafeedEventService

from ..exceptions.UnauthorizedException import UnauthorizedException
from ..exceptions.DatafeedExpiredException import DatafeedExpiredException
from ..exceptions.ServerErrorException import ServerErrorException
from ..exceptions.MaxRetryException import MaxRetryException
from ..exceptions.APIClientErrorException import APIClientErrorException
import time

log = logging.getLogger(__name__)

class DataFeedEventServiceV2(AbstractDatafeedEventService):
    def __init__(self, *args, **kwargs):
        self.datafeed_id = None
        super().__init__(*args, **kwargs)



    def start_datafeed(self):
        log.debug('DataFeedEventServiceV2/startDataFeed()')
        self.read_datafeed()

    def activate_datafeed(self):
        if self.stop:
            self.stop = False

    def deactivate_datafeed(self):
        if not self.stop:
            self.stop = True

    def read_datafeed(self):
        """
            Read_datafeed function reads an array of events coming back from DataFeedClient.

            The json objects returned from read_datafeed() gets passed to handle_events().
        """
        datafeed_ids = self.datafeed_client.list_datafeed_id()

        if len(datafeed_ids) == 0:
            self.datafeed_id = self.datafeed_client.create_datafeed()
        else:
            self.datafeed_id = datafeed_ids[0].get("id")

        while not self.stop:
            try:
                events = self.datafeed_client.read_datafeed(self.datafeed_id, self.datafeed_client.get_ack_id())
            except Exception as exc:
                self.handle_datafeed_errors(exc)
                continue

            self.decrease_timeout()

            if events and events != [None]:
                self.handle_events(events)
            else:
                log.debug(
                    'DataFeedEventServiceV2() - no data coming in from '
                    'datafeed: {}'.format(self.datafeed_id)
                )


    def handle_datafeed_errors(self, thrown_exception):
        """Various errors may get thrown by the datafeed reader, from 500s when a server node is
        being bounced, intermittent connectivity or SSL problems. With the exception of a 403
        UnauthorisedError where reauthentication occurs upstream, these are all handled in
        the same way - sleep, request a new datafeed id and then retry.
        """
        try:
            raise thrown_exception
        except UnauthorizedException:
            log.error('DataFeedEventService - caught unauthorized exception')
        except MaxRetryException as e:
            log.error('DataFeedEventService - Bot has tried to authenticate more than 5 times ')
            raise

        except (DatafeedExpiredException, APIClientErrorException, ServerErrorException) as exc:
            log.error('DataFeedEventService - ' + str(exc))
        except Exception as exc:
            log.exception('DataFeedEventService - Unknown exception: ' + str(exc))
        sleep_for = self.get_and_increase_timeout(thrown_exception)
        log.debug('DataFeedEventService/handle_event() --> Sleeping for {:.4g}s'.format(sleep_for))
        time.sleep(sleep_for)

        try:
            log.debug('DataFeedEventServiceV2 --> Deleting previous Datafeed')
            self.datafeed_client.delete_datafeed(self.datafeed_id)
        except Exception as exc:
            self.handle_datafeed_errors(exc)

        try:
            log.debug('DataFeedEventServiceV2/handle_event() --> Restarting Datafeed')
            self.datafeed_id = self.datafeed_client.create_datafeed()

        except Exception as exc:
            self.handle_datafeed_errors(exc)