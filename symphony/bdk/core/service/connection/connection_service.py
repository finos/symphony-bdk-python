from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.connection.model.connection_status import ConnectionStatus
from symphony.bdk.gen.pod_api.connection_api import ConnectionApi
from symphony.bdk.gen.pod_model.user_connection import UserConnection
from symphony.bdk.gen.pod_model.user_connection_request import UserConnectionRequest


class OboConnectionService:
    """Class exposing OBO-enabled endpoints for connection management.

    This service is used for retrieving the connection status between the OBO user and a specified user or several
    other internal or external users in the pod, and perform some actions related to the connection status like:

    * Send a connection request to an user
    * Accept a connection request from a user
    * Reject a connection request from a user
    * Remove a connection with a user
    """

    def __init__(self, connection_api: ConnectionApi, auth_session: AuthSession):
        self._connection_api = connection_api
        self._auth_session = auth_session

    async def get_connection(self, user_id: int) -> UserConnection:
        """
        Get connection status, i.e. check if the calling user is connected to the specified user.
        See: `Get Connection <https://developers.symphony.com/restapi/reference#get-connection>`_

        :param user_id: The id of the user with whom the caller want to check.

        :return: Connection status with the specified user.

        """
        params = {
            'user_id': str(user_id),
            'session_token': await self._auth_session.session_token
        }
        return await self._connection_api.v1_connection_user_user_id_info_get(**params)

    async def list_connections(
            self,
            status: ConnectionStatus = ConnectionStatus.ALL,
            user_ids: [int] = None
    ) -> [UserConnection]:
        """
        List all connection statuses of the requesting user with external or specified users.
        See: `List Connections <https://developers.symphony.com/restapi/reference#list-connections>`_

        :param status:      Filter the connection list based on the connection status.
                            The connection status can only be pending_incoming, pending_outgoing,
                            accepted, rejected, or all.
                            If you do not specify a status, all connections will be returned.
        :param user_ids:    List of user ids which are used to restrict the list of results.
                            This can be used to return connections with internal users;
                            although, by default, this endpoint does not list implicit connections with internal users.

        :return: List of connection statuses with the specified users and status.

        """
        params = {
            'status': status.value,
            'session_token': await self._auth_session.session_token
        }
        if user_ids is not None:
            params['user_ids'] = ','.join(map(str, user_ids))

        user_connection_list = await self._connection_api.v1_connection_list_get(**params)
        return user_connection_list.value

    async def create_connection(self, user_id: int) -> UserConnection:
        """
        Sends a connection request to another user.
        See: `Create Connection <https://developers.symphony.com/restapi/reference#create-connection>`_

        :param user_id: The id of the user with whom the caller want to connect.

        :return: Connection status with the specified user.

        """
        user_connection_request = UserConnectionRequest(user_id=user_id)
        params = {
            'connection_request': user_connection_request,
            'session_token': await self._auth_session.session_token
        }
        return await self._connection_api.v1_connection_create_post(**params)

    async def accept_connection(self, user_id: int) -> UserConnection:
        """
        Accept the connection request from a requesting user.
        See: `Accept Connection <https://developers.symphony.com/restapi/reference#accepted-connection>`_

        :param user_id: The id of the user who requested to connect with the caller.

        :return: Connection status with the requesting user.

        """
        user_connection_request = UserConnectionRequest(user_id=user_id)
        params = {
            'connection_request': user_connection_request,
            'session_token': await self._auth_session.session_token
        }
        return await self._connection_api.v1_connection_accept_post(**params)

    async def reject_connection(self, user_id: int) -> UserConnection:
        """
        Reject the connection request from a requesting user.
        See: `Reject Connection <https://developers.symphony.com/restapi/reference#reject-connection>`_

        :param user_id: The id of the user who requested to connect with the caller.

        :return: Connection status with the requesting user.

        """
        user_connection_request = UserConnectionRequest(user_id=user_id)
        params = {
            'connection_request': user_connection_request,
            'session_token': await self._auth_session.session_token
        }
        return await self._connection_api.v1_connection_reject_post(**params)

    async def remove_connection(self, user_id: int) -> None:
        """
        Removes a connection with a user.
        See: `Remove Connection <https://developers.symphony.com/restapi/reference#remove-connection>`_

        :param user_id: The id of the user with whom we want to remove the connection.

        """
        params = {
            'uid': user_id,
            'session_token': await self._auth_session.session_token
        }
        await self._connection_api.v1_connection_user_uid_remove_post(**params)


class ConnectionService(OboConnectionService):
    """Service class for managing the connections between users

    This service is used for retrieving the connection status between the calling user and a specified user or several
    other internal or external users in the pod, and perform some actions related to the connection status like:

    * Send a connection request to an user
    * Accept a connection request from a user
    * Reject a connection request from a user
    * Remove a connection with a user
    """
