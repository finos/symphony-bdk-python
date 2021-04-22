from typing import List
from enum import Enum, auto

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.gen.pod_api.presence_api import PresenceApi
from symphony.bdk.gen.pod_model.v2_presence import V2Presence
from symphony.bdk.gen.pod_model.v2_presence_status import V2PresenceStatus
from symphony.bdk.gen.pod_model.v2_user_presence import V2UserPresence


class PresenceStatus(Enum):
    """The list of all possible values for the presence status.
    Set Presence <https://developers.symphony.com/restapi/reference#set-presence>`_
    """

    AVAILABLE = auto()
    BUSY = auto()
    AWAY = auto()
    ON_THE_PHONE = auto()
    BE_RIGHT_BACK = auto()
    IN_A_MEETING = auto()
    OUT_OF_OFFICE = auto()
    OFF_WORK = auto()


class OboPresenceService:
    """Service class exposing OBO-enabled endpoints to manage user presence information.

    This service is used for retrieving information about the presence of the OBO user or a specified user or
    all users in the pod, and perform some actions related to the user presence information like:

    * Set Presence to calling user
    * Set Presence to a specified user
    * Create a presence feed
    * Read a created presence feed
    * Delete a created presence feed
    """

    def __init__(self, presence_api: PresenceApi, auth_session: AuthSession):
        self._presence_api = presence_api
        self._auth_session = auth_session

    async def get_presence(self) -> V2Presence:
        """ Get the online status (presence info) of the calling user.
        See: `Get Presence <https://developers.symphony.com/restapi/reference#get-presence>`_.

        :return: Presence info of the calling user.
        """
        return await self._presence_api.v2_user_presence_get(session_token=await self._auth_session.session_token)

    async def get_all_presence(self, last_user_id: int, limit: int) -> List[V2Presence]:
        """ Get the presence info of all users in a pod.
        See: `Get All Presence <https://developers.symphony.com/restapi/reference#get-all-presence>`_.

        :param last_user_id: Last user ID retrieved, used for paging. If provided, results skip users with IDs less
          than this parameter.
        :param limit: Maximum number of records to return. The maximum supported value is 5000.
        :return: Presence info of the looked up user.
        """
        presence_list = await self._presence_api.v2_users_presence_get(
            session_token=await self._auth_session.session_token,
            last_user_id=last_user_id,
            limit=limit)
        return presence_list.value

    async def get_user_presence(self, user_id: int, local: bool) -> V2Presence:
        """ Get the presence info of a specified user.
        See: `Get User Presence <https://developers.symphony.com/restapi/reference#user-presence-v3>`_.

        :param user_id: User Id
        :param local: If true then Perform a local query and set the presence to OFFLINE for  users who are not local to
          the calling user’s pod. If false or absent then query the presence of all local  and external users who are
          connected to the calling user.
        :return: Presence info of the looked up user.
        """
        return await self._presence_api.v3_user_uid_presence_get(uid=user_id,
                                                                 session_token=await self._auth_session.session_token,
                                                                 local=local)

    async def external_presence_interest(self, user_ids: List[int]):
        """ Register interest in a list of external users to get their presence info.
        See: `External Presence Interest
        <https://developers.symphony.com/restapi/reference#register-user-presence-interest>`_.

        :param user_ids: List of user ids to be registered.
        """
        await self._presence_api.v1_user_presence_register_post(session_token=await self._auth_session.session_token,
                                                                uid_list=user_ids)

    async def set_presence(self, status: PresenceStatus, soft: bool) -> V2Presence:
        """ Set the presence info of the calling user.
        See: `Set Presence <https://developers.symphony.com/restapi/reference#set-presence>`_.

        :param status: The new presence state for the user.
          Possible values are AVAILABLE, BUSY, AWAY, ON_THE_PHONE, BE_RIGHT_BACK, IN_A_MEETING, OUT_OF_OFFICE, OFF_WORK.
        :param soft: If true, the user's current status is taken into consideration. If the user is currently OFFLINE,
          the user's presence will still be OFFLINE, but the new presence will take effect when the user comes online.
          If the user is currently online, the user's activity state will be applied to the presence if applicable.
          (e.g. if you are setting their presence to AVAILABLE, but the user is currently idle, their status will be
          represented as AWAY)
        :return: Presence info of the calling user.
        """
        presence_status: V2PresenceStatus = V2PresenceStatus(category=status.name)
        return await self._presence_api.v2_user_presence_post(session_token=await self._auth_session.session_token,
                                                              presence=presence_status,
                                                              soft=soft)

    async def create_presence_feed(self) -> str:
        """ Creates a new stream capturing online status changes ("presence feed") for the company (pod) and returns
        the ID of the new feed. The feed will return the presence of users whose presence status has changed since it
        was last read.
        See: `Create Presence Feed <https://developers.symphony.com/restapi/reference#create-presence-feed>`_.

        :return: Presence feed Id
        """
        string_id = await self._presence_api.v1_presence_feed_create_post(
            session_token=await self._auth_session.session_token)
        return string_id.id

    async def read_presence_feed(self, feed_id: str) -> List[V2Presence]:
        """ Reads the specified presence feed that was created.
        The feed returned includes the user presence statuses that have changed since they were last read.
        See: `Read Presence Feed <https://developers.symphony.com/restapi/reference#read-presence-feed>`_.

        :param feed_id: The presence feed id to be read.
        :return: The list of user presences has changed since the last presence read.
        """
        presence_list = await self._presence_api.v1_presence_feed_feed_id_read_get(
            session_token=await self._auth_session.session_token,
            feed_id=feed_id)
        return presence_list.value

    async def delete_presence_feed(self, feed_id: str) -> str:
        """ Delete the specified presence feed that was created.
        See: `Delete Presence Feed <https://developers.symphony.com/restapi/reference#delete-presence-feed>`_.

        :param feed_id: The presence feed id to be deleted.
        :return: The id of the deleted presence feed.
        """
        string_id = await self._presence_api.v1_presence_feed_feed_id_delete_post(
            session_token=await self._auth_session.session_token, feed_id=feed_id)
        return string_id.id

    async def set_user_presence(self, user_id: int, status: PresenceStatus, soft: bool) -> V2Presence:
        """ Set the presence state of a another user.
        See: `Set Other User's Presence - Admin V3
        <https://developers.symphony.com/restapi/reference#set-user-presence>`_.

        :param user_id: The id of the specified user.
        :param status: Presence state to set.
          Possible values are AVAILABLE, BUSY, AWAY, ON_THE_PHONE, BE_RIGHT_BACK, IN_A_MEETING, OUT_OF_OFFICE, OFF_WORK.
        :param soft: If true, the user's current status is taken into consideration. If the user is currently OFFLINE,
          the user's presence will still be OFFLINE, but the new presence will take effect when the user comes online.
          If the user is currently online, the user's activity state will be applied to the presence if applicable.
          (e.g. if you are setting their presence to AVAILABLE, but the user is currently idle, their status will be
          represented as AWAY)
        :return: The presence info of the specified user.
        """
        user_presence: V2UserPresence = V2UserPresence(category=status.name, user_id=user_id)
        return await self._presence_api.v3_user_presence_post(session_token=await self._auth_session.session_token,
                                                              presence=user_presence,
                                                              soft=soft)


class PresenceService(OboPresenceService):
    """Service class for managing user presence information.

    This service is used for retrieving information about the presence of the calling user or a specified user or
    all users in the pod, and perform some actions related to the user presence information like:

    * Set Presence to calling user
    * Set Presence to a specified user
    * Create a presence feed
    * Read a created presence feed
    * Delete a created presence feed
    """
