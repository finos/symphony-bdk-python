from typing import AsyncGenerator

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.pagination import offset_based_pagination
from symphony.bdk.gen.agent_api.signals_api import SignalsApi
from symphony.bdk.gen.agent_model.base_signal import BaseSignal
from symphony.bdk.gen.agent_model.channel_subscriber import ChannelSubscriber
from symphony.bdk.gen.agent_model.channel_subscriber_response import ChannelSubscriberResponse
from symphony.bdk.gen.agent_model.channel_subscription_response import ChannelSubscriptionResponse
from symphony.bdk.gen.agent_model.signal import Signal
from symphony.bdk.gen.agent_model.signal_list import SignalList


class OboSignalService:
    """Service class exposing OBO-enabled endpoints to manage signal information.

    This service is used for listing signals related to the OBO user, get information of a specified signal
    or perform some actions related to the signal like:

    * List signals
    * Get a signal
    * Create a signal
    * Update a signal
    * Delete a signal
    * Subscribe or unsubscribe a signal
    """

    def __init__(self, signals_api: SignalsApi, auth_session: AuthSession):
        self._signals_api = signals_api
        self._auth_session = auth_session

    async def list_signals(self, skip: int = 0, limit: int = 50) -> SignalList:
        """Lists signals on behalf of the user. The response includes signals that the user has created and
        public signals to which they have subscribed.

        See: 'List signals <https://developers.symphony.com/restapi/reference#list-signals>'_

        :param skip: The number of signals to skip.
        :param limit: Maximum number of signals to return. Default is 50, maximum value is 500.
        :return: List of signals found.
        """

        return await self._signals_api.v1_signals_list_get(
            skip=skip, limit=limit, session_token=await self._auth_session.session_token,
            key_manager_token=await self._auth_session.key_manager_token)

    async def list_all_signals(self, chunk_size: int = 50, max_number: int = None) -> AsyncGenerator[Signal, None]:
        """Lists all signals on behalf of the user. The response includes signals that the user has created and
        public signals to which they have subscribed.

        See: 'List signals <https://developers.symphony.com/restapi/reference#list-signals>'_

        :param chunk_size: the maximum number of elements to retrieve in one underlying HTTP call
        :param max_number: the total maximum number of elements to retrieve
        :return: an asynchronous generator of found signals
        """

        async def list_signals_one_page(skip, limit):
            result = await self.list_signals(skip, limit)
            return result.value if result else None

        return offset_based_pagination(list_signals_one_page, chunk_size, max_number)

    async def get_signal(self, signal_id: str) -> Signal:
        """ Gets details about the specified signal.

        See: 'Get signal <https://developers.symphony.com/restapi/reference#get-signal>'_

        :param signal_id: Id of the signal to display.
        :return: The signal found.
        """

        return await self._signals_api.v1_signals_id_get_get(
            id=signal_id, session_token=await self._auth_session.session_token,
            key_manager_token=await self._auth_session.key_manager_token)

    async def create_signal(self, signal: BaseSignal) -> Signal:
        """ Creates a new Signal.

        See: 'Create signal <https://developers.symphony.com/restapi/reference#create-signal>'_

        :param signal: The new Signal object to be created.
        :return: The signal created.
        """

        return await self._signals_api.v1_signals_create_post(
            signal=signal, session_token=await self._auth_session.session_token,
            key_manager_token=await self._auth_session.key_manager_token)

    async def update_signal(self, signal_id: str, signal: BaseSignal) -> Signal:
        """ Updates an existing Signal.

        See: 'Update signal <https://developers.symphony.com/restapi/reference#update-signal>'_

        :param signal_id: The Id of the signal to be modified.
        :param signal: The Signal object to be updated.
        :return: The updated signal.
        """

        return await self._signals_api.v1_signals_id_update_post(
            id=signal_id, signal=signal, session_token=await self._auth_session.session_token,
            key_manager_token=await self._auth_session.key_manager_token)

    async def delete_signal(self, signal_id: str) -> None:
        """ Deletes an existing Signal.

        See: 'Delete signal <https://developers.symphony.com/restapi/reference#delete-signal>'_

        :param signal_id: The Id of the existing signal to be deleted.
        """

        await self._signals_api.v1_signals_id_delete_post(id=signal_id,
                                                          session_token=await self._auth_session.session_token,
                                                          key_manager_token=await self._auth_session.key_manager_token)

    async def subscribe_users_to_signal(self, signal_id: str, pushed: bool,
                                        user_ids: [int]) -> ChannelSubscriptionResponse:
        """ Subscribe an array of users to a Signal.

        See: 'Subscribe signal <https://developers.symphony.com/restapi/reference#subscribe-signal>'_

        :param signal_id: The Id of the signal to be subscribed.
        :param pushed: Prevents the user from unsubscribing from the Signal
        :param user_ids: An array of User Ids to subscribe to the Signal
        :return: Result of the bulk subscriptions
        """

        return await self._signals_api.v1_signals_id_subscribe_post(
            id=signal_id, pushed=pushed, users=user_ids, session_token=await self._auth_session.session_token,
            key_manager_token=await self._auth_session.key_manager_token)

    async def unsubscribe_users_to_signal(self, signal_id: str, user_ids: [int]) -> ChannelSubscriptionResponse:
        """ Unsubscribes an array of users from the specified Signal.

        See: 'Unsubscribe signal <https://developers.symphony.com/restapi/reference#unsubscribe-signal>'_

        :param signal_id: The Id of the signal to be subscribed.
        :param user_ids: An array of User Ids to subscribe to the Signal
        :return: Result of the bulk unsubscriptions
        """

        return await self._signals_api.v1_signals_id_unsubscribe_post(
            id=signal_id, users=user_ids, session_token=await self._auth_session.session_token,
            key_manager_token=await self._auth_session.key_manager_token)

    async def list_subscribers(self, signal_id: str, skip: int = 0, limit: int = 50) -> ChannelSubscriberResponse:
        """Gets the subscribers for the specified signal.

        See: 'Subscribers <https://developers.symphony.com/restapi/reference#subscribers>'_

        :param signal_id: The Id of the signal.
        :param skip: The number of results to skip.
        :param limit: The maximum number of subscribers to return. The maximum value accepted for this parameter is 100
          and the default value is 50.
        :return: The list of users subscribed to the signal.
        """

        return await self._signals_api.v1_signals_id_subscribers_get(
            id=signal_id, skip=skip, limit=limit, session_token=await self._auth_session.session_token,
            key_manager_token=await self._auth_session.key_manager_token)

    async def list_all_subscribers(self, signal_id: str, chunk_size: int = 50, max_number: int = None) \
            -> AsyncGenerator[ChannelSubscriber, None]:
        """Gets all the subscribers for the specified signal.

        See: 'Subscribers <https://developers.symphony.com/restapi/reference#subscribers>'_

        :param signal_id: the Id of the signal.
        :param chunk_size: the maximum number of elements to retrieve in one underlying HTTP call.
        :param max_number: the total maximum number of elements to retrieve.
        :return: an asynchronous generator returning all users subscribed to the signal.
        """

        async def list_subscribers_one_page(skip, limit):
            result = await self.list_subscribers(signal_id, skip, limit)
            return result.data if result else None

        return offset_based_pagination(list_subscribers_one_page, chunk_size, max_number)


class SignalService(OboSignalService):
    """Service class for managing signal information.
    This service is used for listing signals related to the user, get information of a specified signal
    or perform some actions related to the signal like:

    * List signals
    * Get a signal
    * Create a signal
    * Update a signal
    * Delete a signal
    * Subscribe or unsubscribe a signal
    """
