import base64
from typing import Union

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.user.model.delegate_action_enum import DelegateActionEnum
from symphony.bdk.core.service.user.model.role_id import RoleId
from symphony.bdk.gen.agent_api.audit_trail_api import AuditTrailApi
from symphony.bdk.gen.agent_model.v1_audit_trail_initiator_list import V1AuditTrailInitiatorList
from symphony.bdk.gen.pod_api.system_api import SystemApi
from symphony.bdk.gen.pod_api.user_api import UserApi
from symphony.bdk.gen.pod_api.users_api import UsersApi
from symphony.bdk.gen.pod_model.avatar import Avatar
from symphony.bdk.gen.pod_model.avatar_update import AvatarUpdate
from symphony.bdk.gen.pod_model.delegate_action import DelegateAction
from symphony.bdk.gen.pod_model.disclaimer import Disclaimer
from symphony.bdk.gen.pod_model.feature import Feature
from symphony.bdk.gen.pod_model.feature_list import FeatureList
from symphony.bdk.gen.pod_model.followers_list import FollowersList
from symphony.bdk.gen.pod_model.followers_list_response import FollowersListResponse
from symphony.bdk.gen.pod_model.following_list_response import FollowingListResponse
from symphony.bdk.gen.pod_model.role_detail import RoleDetail
from symphony.bdk.gen.pod_model.string_id import StringId
from symphony.bdk.gen.pod_model.user_filter import UserFilter
from symphony.bdk.gen.pod_model.user_id_list import UserIdList
from symphony.bdk.gen.pod_model.user_search_query import UserSearchQuery
from symphony.bdk.gen.pod_model.user_search_results import UserSearchResults
from symphony.bdk.gen.pod_model.user_status import UserStatus
from symphony.bdk.gen.pod_model.v2_user_attributes import V2UserAttributes
from symphony.bdk.gen.pod_model.v2_user_create import V2UserCreate
from symphony.bdk.gen.pod_model.v2_user_detail import V2UserDetail
from symphony.bdk.gen.pod_model.v2_user_list import V2UserList
from symphony.bdk.gen.pod_model.user_suspension import UserSuspension


class OboUserService:
    """Class exposing OBO-enabled endpoints for user management.
    This service is used for retrieving information about a particular user,
    search users by ids, emails or usernames, perform some action related to
    user like:

    * list/search users
    * follow/unfollow users
    """

    def __init__(self, user_api: UserApi,
                 users_api: UsersApi,
                 auth_session: AuthSession):
        self._user_api = user_api
        self._users_api = users_api
        self._auth_session = auth_session

    async def list_users_by_ids(
            self,
            user_ids: [int],
            local: bool = False,
            active: bool = None
    ) -> V2UserList:
        """
        Search users by user ids.
        See : `Users Lookup v3 <https://developers.symphony.com/restapi/v20.10/reference#users-lookup-v3>`_

        :param user_ids:    List of user ids.
        :param local:       If true then a local DB search will be performed and only local pod users will be
                            returned. If absent or false then a directory search will be performed and users
                            from other pods who are visible to the calling user will also be returned.
        :param active:      If not set all user status will be returned,
                            if true all active users will be returned,
                            if false all inactive users will be returned.

        :return: Users found by user ids.

        """
        user_ids_str = ','.join(map(str, user_ids))
        params = {
            'uid': user_ids_str,
            'local': local,
            'session_token': await self._auth_session.session_token
        }
        if active is not None:
            params['active'] = active
        return await self._users_api.v3_users_get(**params)

    async def list_users_by_emails(
            self,
            emails: [str],
            local: bool = False,
            active: bool = None
    ) -> V2UserList:
        """
        Search users by emails.
        See : `Users Lookup v3 <https://developers.symphony.com/restapi/v20.10/reference#users-lookup-v3>`_

        :param emails:      List of emails.
        :param local:       If true then a local DB search will be performed and only local pod users will be
                            returned. If absent or false then a directory search will be performed and users
                            from other pods who are visible to the calling user will also be returned.
        :param active:      If not set all user status will be returned,
                            if true all active users will be returned,
                            if false all inactive users will be returned.

        :return: Users found by emails.

        """
        emails_str = ','.join(emails)
        params = {
            'email': emails_str,
            'local': local,
            'session_token': await self._auth_session.session_token
        }
        if active is not None:
            params['active'] = active
        return await self._users_api.v3_users_get(**params)

    async def list_users_by_usernames(
            self,
            usernames: [str],
            active: bool = None
    ) -> V2UserList:
        """
        Search users by usernames.
        See : `Users Lookup v3 <https://developers.symphony.com/restapi/v20.10/reference#users-lookup-v3>`_

        :param usernames    List of usernames.
        :param active:      If not set all user status will be returned,
                            if true all active users will be returned,
                            if false all inactive users will be returned.

        :return: Users found by usernames.

        """
        usernames_str = ','.join(usernames)
        params = {
            'username': usernames_str,
            'local': True,
            'session_token': await self._auth_session.session_token
        }
        if active is not None:
            params['active'] = active
        return await self._users_api.v3_users_get(**params)

    async def search_users(
            self,
            query: [UserSearchQuery],
            local: bool = False,
            skip: int = 0,
            limit: int = 50
    ) -> UserSearchResults:
        """
        Search for users by first name, last name, display name, and email; optionally, filter results by company,
        title, location, marketCoverage, responsibility, function, or instrument.
        See: `Search Users <https://developers.symphony.com/restapi/v20.10/reference#search-users>`_

        :param query:   Searching query containing complicated information like title, location, company...
        :param local:   If true then a local DB search will be performed and only local pod users will be
                        returned. If absent or false then a directory search will be performed and users
                        from other pods who are visible to the calling user will also be returned.
        :param skip:    Number of users to skip. Default: 0
        :param limit:   Maximum number of users to return. Default: 50

        :return: the list of users found by query.

        """
        params = {
            'search_request': query,
            'local': local,
            'session_token': await self._auth_session.session_token,
            'skip': skip,
            'limit': limit
        }
        return await self._users_api.v1_user_search_post(**params)

    async def follow_user(
            self,
            follower_ids: [int],
            user_id: int
    ) -> None:
        """
        Make a list of users to start following a specific user.
        See: `Follow User <https://developers.symphony.com/restapi/v20.9/reference#follow-user>`_

        :param follower_ids:    List of the ids of the followers.
        :param user_id:         The id of the user to be followed.

        """
        params = {
            'uid': user_id,
            'uid_list': FollowersList(followers=UserIdList(value=follower_ids)),
            'session_token': await self._auth_session.session_token
        }
        await self._user_api.v1_user_uid_follow_post(**params)

    async def unfollow_user(
            self,
            follower_ids: [int],
            user_id: int
    ) -> None:
        """
        Make a list of users to stop following a specific user.
        See: `Unfollow User <https://developers.symphony.com/restapi/v20.9/reference#unfollow-user>`_

        :param follower_ids:    List of the ids of the followers.
        :param user_id:         The id of the user to be unfollowed.

        Returns:

        """
        params = {
            'uid': user_id,
            'uid_list': FollowersList(followers=UserIdList(value=follower_ids)),
            'session_token': await self._auth_session.session_token
        }
        await self._user_api.v1_user_uid_unfollow_post(**params)


class UserService(OboUserService):
    """Service class for managing users

    This service is used for retrieving information about a particular user,
    search users by ids, emails or usernames, perform some action related to
    user like:

    * Add or remove roles from an user
    * Get or update avatar of an user
    * Get, assign or unassign disclaimer to an user
    * Get, update feature entitlements of an user
    * Get, update status of an user
    """

    def __init__(self, user_api: UserApi,
                 users_api: UsersApi,
                 audit_trail_api: AuditTrailApi,
                 system_api: SystemApi,
                 auth_session: AuthSession):
        super().__init__(user_api, users_api, auth_session)
        self._audit_trail_api = audit_trail_api
        self._system_api = system_api

    async def get_user_detail(
            self,
            user_id: int
    ) -> V2UserDetail:
        """
        Retrieve user details of a particular user.
        See: 'Get User v2 <https://developers.symphony.com/restapi/reference#get-user-v2>'_

        :param user_id: User Id

        :return: Details of the user.

        """
        params = {
            'uid': user_id,
            'session_token': await self._auth_session.session_token
        }
        return await self._user_api.v2_admin_user_uid_get(**params)

    async def list_user_details(
            self,
            skip: int = 0,
            limit: int = 50
    ) -> [V2UserDetail]:
        """
        Retrieve all users in the company (pod).
        See: 'List Users V2 <https://developers.symphony.com/restapi/reference#list-users-v2>'_

        :param skip:    Number of users to skip. Default: 0
        :param limit:   Maximum number of users to return. Default: 50

        :return: List of details of all users in the company.

        """
        params = {
            'session_token': await self._auth_session.session_token,
            'skip': skip,
            'limit': limit
        }
        user_detail_list = await self._user_api.v2_admin_user_list_get(**params)
        return user_detail_list.value

    async def list_user_details_by_filter(
            self,
            user_filter: UserFilter,
            skip: int = 0,
            limit: int = 50
    ) -> [V2UserDetail]:
        """
        Retrieve a list of users in the company (pod) by a filter.
        See: `Find Users V1 <https://developers.symphony.com/restapi/reference#find-users>`_

        :param user_filter: Filter using to filter users by.
        :param skip:    Number of users to skip. Default: 0
        :param limit:   Maximum number of users to return. Default: 50

        :return: List of retrieved users.

        """
        params = {
            'payload': user_filter,
            'session_token': await self._auth_session.session_token,
            'skip': skip,
            'limit': limit
        }
        user_detail_list = await self._user_api.v1_admin_user_find_post(**params)
        return user_detail_list.value

    async def add_role(
            self,
            user_id: int,
            role_id: RoleId
    ) -> None:
        """
        Add a role to an user.
        See: `Add Role <https://developers.symphony.com/restapi/reference#add-role>`_

        :param user_id: user id
        :param role_id: role id

        """
        params = {
            'uid': user_id,
            'payload': StringId(id=role_id.value),
            'session_token': await self._auth_session.session_token
        }
        await self._user_api.v1_admin_user_uid_roles_add_post(**params)

    async def list_roles(self) -> [RoleDetail]:
        """
        List all roles in the pod.
        See: `List Roles <https://developers.symphony.com/restapi/reference#list-roles>`_

        :return: List of all roles details in the pod.

        """
        params = {
            'session_token': await self._auth_session.session_token
        }
        role_list = await self._system_api.v1_admin_system_roles_list_get(**params)
        return role_list.value

    async def remove_role(
            self,
            user_id: int,
            role_id: RoleId
    ) -> None:
        """
        Remove a role from an user.
        See: `Remove Role <https://developers.symphony.com/restapi/reference#remove-role>`_

        :param user_id: user id
        :param role_id: role id

        """
        params = {
            'uid': user_id,
            'payload': StringId(id=role_id.value),
            'session_token': await self._auth_session.session_token
        }
        await self._user_api.v1_admin_user_uid_roles_remove_post(**params)

    async def get_avatar(
            self,
            user_id: int
    ) -> [Avatar]:
        """
        Get the url of avatar of an user.
        See: `User Avatar <https://developers.symphony.com/restapi/reference#user-avatar>`_

        :param user_id: User id

        :return: List of avatar urls of the user

        """
        params = {
            'uid': user_id,
            'session_token': await self._auth_session.session_token
        }
        avatar_list = await self._user_api.v1_admin_user_uid_avatar_get(**params)
        return avatar_list.value

    async def update_avatar(
            self,
            user_id: int,
            image: Union[str, bytes]
    ) -> None:
        """
        Update avatar of an user.
        See: `Update User Avatar <https://developers.symphony.com/restapi/reference#update-user-avatar>`_

        :param user_id: User id
        :param image:   The avatar image for the user profile picture.
                        The image must be a base64-encoded string or a bytes array.

        """
        if isinstance(image, bytes):
            image = str(base64.standard_b64encode(image))
        params = {
            'uid': user_id,
            'payload': AvatarUpdate(image=image),
            'session_token': await self._auth_session.session_token
        }
        await self._user_api.v1_admin_user_uid_avatar_update_post(**params)

    async def get_disclaimer(
            self,
            user_id: int
    ) -> Disclaimer:
        """
        Get disclaimer assigned to an user.
        See: `User Disclaimer <https://developers.symphony.com/restapi/reference#user-disclaimer>`_

        :param user_id: user id

        :return: Disclaimer assigned to the user.

        """
        params = {
            'uid': user_id,
            'session_token': await self._auth_session.session_token
        }
        return await self._user_api.v1_admin_user_uid_disclaimer_get(**params)

    async def remove_disclaimer(
            self,
            user_id: int
    ) -> None:
        """
        Unassign disclaimer from an user.
        See: `Unassign User Disclaimer <https://developers.symphony.com/restapi/reference#unassign-user-disclaimer>`_

        :param user_id: user id

        """
        params = {
            'uid': user_id,
            'session_token': await self._auth_session.session_token
        }
        await self._user_api.v1_admin_user_uid_disclaimer_delete(**params)

    async def add_disclaimer(
            self,
            user_id: int,
            disclaimer_id: str
    ) -> None:
        """
        Assign disclaimer to an user.
        See: `Update User Disclaimer <https://developers.symphony.com/restapi/reference#update-disclaimer>`_

        :param user_id:         User id
        :param disclaimer_id:   Disclaimer to be assigned

        """
        params = {
            'uid': user_id,
            'payload': StringId(id=disclaimer_id),
            'session_token': await self._auth_session.session_token
        }
        await self._user_api.v1_admin_user_uid_disclaimer_update_post(**params)

    async def get_delegates(
            self,
            user_id: int
    ) -> [int]:
        """
        Get delegates assigned to an user.
        See: `User Delegates <https://developers.symphony.com/restapi/reference#delegates>`_

        :param user_id: User id.

        :return: List of delegates assigned to an user.

        """
        params = {
            'uid': user_id,
            'session_token': await self._auth_session.session_token
        }
        delegates_list = await self._user_api.v1_admin_user_uid_delegates_get(**params)
        return delegates_list.value

    async def update_delegates(
            self,
            user_id: int,
            delegate_user_id: int,
            action: DelegateActionEnum
    ) -> None:
        """
        Update delegates assigned to an user.
        See: `Update User Delegates <https://developers.symphony.com/restapi/reference#update-delegates>`_

        :param user_id:             User id.
        :param delegate_user_id:    Delegated user Id to be assigned
        :param action:              Action to be performed

        """
        params = {
            'uid': user_id,
            'payload': DelegateAction(user_id=delegate_user_id, action=action.value),
            'session_token': await self._auth_session.session_token
        }
        await self._user_api.v1_admin_user_uid_delegates_update_post(**params)

    async def get_feature_entitlements(
            self,
            user_id: int
    ) -> [Feature]:
        """
        Get feature entitlements of an user.
        See: `User Features <https://developers.symphony.com/restapi/reference#features>`_

        :param user_id: User id.

        :return: List of feature entitlements of the user.

        """
        params = {
            'uid': user_id,
            'session_token': await self._auth_session.session_token
        }
        feature_list = await self._user_api.v1_admin_user_uid_features_get(**params)
        return feature_list.value

    async def update_feature_entitlements(
            self,
            user_id: int,
            features: [Feature]
    ) -> None:
        """
        Update feature entitlements of an user.
        See: `Update User Features <https://developers.symphony.com/restapi/reference#update-features>`_

        :param user_id:     User id.
        :param features:    List of feature entitlements to be updated

        """
        params = {
            'uid': user_id,
            'payload': FeatureList(value=features),
            'session_token': await self._auth_session.session_token
        }
        await self._user_api.v1_admin_user_uid_features_update_post(**params)

    async def get_status(
            self,
            user_id: int
    ) -> UserStatus:
        """
        Get status of an user.
        See: `User Status <https://developers.symphony.com/restapi/reference#user-status>`_

        :param user_id: User id.

        :return: Status of the user.

        """
        params = {
            'uid': user_id,
            'session_token': await self._auth_session.session_token
        }
        return await self._user_api.v1_admin_user_uid_status_get(**params)

    async def update_status(
            self,
            user_id: int,
            user_status: UserStatus
    ) -> None:
        """
        Update the status of an user.
        See: `Update User Status <https://developers.symphony.com/restapi/reference#update-user-status>`_

        :param user_id:     User id.
        :param user_status: Status to be updated to the user.

        """
        params = {
            'uid': user_id,
            'payload': user_status,
            'session_token': await self._auth_session.session_token
        }
        await self._user_api.v1_admin_user_uid_status_update_post(**params)

    async def list_user_followers(
            self,
            user_id: int,
            limit: int = 100,
            before: int = None,
            after: int = None
    ) -> FollowersListResponse:
        """
        Returns the list of followers of a specific user.
        See: `List User Followers <https://developers.symphony.com/restapi/v20.9/reference#list-user-followers>`_

        :param user_id: User id.
        :param limit:   Maximum number of followers to return. Default: 100
        :param before:  Returns results from an opaque “before” cursor value as presented via a response cursor.
        :param after:   Returns results from an opaque “after” cursor value as presented via a response cursor.

        :return: List of followers of a specific user.

        """
        params = {
            'uid': user_id,
            'limit': limit,
            'session_token': await self._auth_session.session_token
        }
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        return await self._user_api.v1_user_uid_followers_get(**params)

    async def list_users_following(
            self,
            user_id: int,
            limit: int = 100,
            before: int = None,
            after: int = None
    ) -> FollowingListResponse:
        """
        Returns the list of users followed by a specific user.
        See: `List Users Followed <https://developers.symphony.com/restapi/v20.9/reference#list-users-followed>`_

        :param user_id: User id.
        :param limit:   Maximum number of users to return. Default: 100
        :param before:  Returns results from an opaque “before” cursor value as presented via a response cursor.
        :param after:   Returns results from an opaque “after” cursor value as presented via a response cursor.

        :return: The list of users followed by a specific user.

        """
        params = {
            'uid': user_id,
            'limit': limit,
            'session_token': await self._auth_session.session_token
        }
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        return await self._user_api.v1_user_uid_following_get(**params)

    async def create(
            self,
            payload: V2UserCreate
    ) -> V2UserDetail:
        """
        Create a new user.
        See: `Create User v2 <https://developers.symphony.com/restapi/reference#create-user-v2>`_

        :param payload: User's details to create.

        :return: Created user details.

        """
        params = {
            'payload': payload,
            'session_token': await self._auth_session.session_token
        }
        return await self._user_api.v2_admin_user_create_post(**params)

    async def update(
            self,
            user_id: int,
            payload: V2UserAttributes
    ) -> V2UserDetail:
        """
        Updates an existing user.
        See: `Update User v2 <https://developers.symphony.com/restapi/reference#update-user-v2>`_

        :param user_id: User Id
        :param payload: User's new attributes for update.

        :return: User with the updated user details.

        """
        params = {
            'uid': user_id,
            'payload': payload,
            'session_token': await self._auth_session.session_token
        }
        return await self._user_api.v2_admin_user_uid_update_post(**params)

    async def list_audit_trail(
            self,
            start_timestamp: int,
            end_timestamp: int = None,
            initiator_id: int = None,
            role: RoleId = None,
            limit: int = 50,
            before: int = None,
            after: int = None
    ) -> V1AuditTrailInitiatorList:
        """
        Returns audit trail of actions performed by a privileged user in a given period of time.
        See: `List Audit Trail v1 <https://developers.symphony.com/restapi/reference#list-audit-trail-v1>`_

        :param start_timestamp: The start time of the period to retrieve the data.
        :param end_timestamp:   The end time of the period to retrieve the data.
        :param initiator_id:    The range and limit for pagination of data.
        :param role:            Role to list audit trail for.
        :param limit:           Maximum number of audit trail to return. Default: 50
        :param before:          Returns results from an opaque “before” cursor value as presented via a response cursor.
        :param after:           Returns results from an opaque “after” cursor value as presented via a response cursor.

        :return: List of audit trail initiator.

        """
        params = {
            'start_timestamp': start_timestamp,
            'limit': limit,
            'session_token': await self._auth_session.session_token,
            'key_manager_token': await self._auth_session.key_manager_token
        }
        if end_timestamp is not None:
            params['end_timestamp'] = end_timestamp
        if initiator_id is not None:
            params['initiator_id'] = initiator_id
        if role is not None:
            params['role'] = role.value
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        return await self._audit_trail_api.v1_audittrail_privilegeduser_get(**params)

    async def suspend_user(
            self,
            user_id: int,
            user_suspension: UserSuspension
    ) -> None:
        """
        Suspends or re-activates (unsuspend) a user account.
        See: `Suspend User Account v1 <https://developers.symphony.com/restapi/v20.10/reference#suspend-user-v1>`_

        :param user_id:         User id.
        :param user_suspension: User suspension payload.

        """
        params = {
            'user_id': user_id,
            'payload': user_suspension,
            'session_token': await self._auth_session.session_token
        }

        await self._user_api.v1_admin_user_user_id_suspension_update_put(**params)
