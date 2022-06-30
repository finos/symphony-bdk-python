from typing import AsyncGenerator

from symphony.bdk.core.extension import BdkAuthenticationAware, BdkApiClientFactoryAware, BdkExtensionServiceProvider, \
    BdkConfigAware
from symphony.bdk.core.retry import retry
from symphony.bdk.core.retry.strategy import is_network_or_minor_error, is_unauthorized
from symphony.bdk.core.service.pagination import offset_based_pagination, cursor_based_pagination
from symphony.bdk.core.service.user.user_util import extract_tenant_id
from symphony.bdk.gen.group_api.group_api import GroupApi
from symphony.bdk.gen.group_model.add_member import AddMember
from symphony.bdk.gen.group_model.create_group import CreateGroup
from symphony.bdk.gen.group_model.group_list import GroupList
from symphony.bdk.gen.group_model.member import Member
from symphony.bdk.gen.group_model.read_group import ReadGroup
from symphony.bdk.gen.group_model.sort_order import SortOrder
from symphony.bdk.gen.group_model.status import Status
from symphony.bdk.gen.group_model.update_group import UpdateGroup
from symphony.bdk.gen.group_model.upload_avatar import UploadAvatar
from symphony.bdk.gen.login_api.authentication_api import AuthenticationApi


async def refresh_bearer_token_if_unauthorized(retry_state):
    """Function used by the retry decorator to refresh the bearer token if conditions apply

    :param retry_state: current retry state
    :return: True if we want to retry, False otherwise
    """
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        if is_network_or_minor_error(exception):
            if is_unauthorized(exception):
                await retry_state.args[0]._oauth_session.refresh()
            return True
    return False


class SymphonyGroupBdkExtension(BdkAuthenticationAware, BdkApiClientFactoryAware, BdkConfigAware,
                                BdkExtensionServiceProvider):
    """Extension for Symphony Groups APIs
    """

    def __init__(self):
        self._api_client_factory = None
        self._bot_session = None
        self._config = None

    def set_api_client_factory(self, api_client_factory):
        self._api_client_factory = api_client_factory

    def set_bot_session(self, bot_session):
        self._bot_session = bot_session

    def set_config(self, config):
        self._config = config

    def get_service(self):
        return SymphonyGroupService(self._api_client_factory, self._bot_session, self._config.retry)


class SymphonyGroupService:
    """Service class for managing Symphony Groups
    """

    def __init__(self, api_client_factory, auth_session, retry_config):
        self._api_client_factory = api_client_factory
        self._auth_session = auth_session
        self._retry_config = retry_config
        self._oauth_session = OAuthSession(self._api_client_factory.get_login_client(), self._auth_session,
                                           self._retry_config)
        client = self._api_client_factory.get_client("/profile-manager")
        client.configuration.auth_settings = self._oauth_session.get_auth_settings

        # needed for the x_symphony_host parameter to allow empty value
        client.configuration._disabled_client_side_validations = ["minLength"]
        self._group_api = GroupApi(client)

    @retry(retry=refresh_bearer_token_if_unauthorized)
    async def insert_group(self, create_group: CreateGroup) -> ReadGroup:
        """Create a new group
        See: `Insert a new group <https://developers.symphony.com/restapi/reference/insertgroup>`_

        :param create_group: the details of the group to be created
        :return: the created group
        """
        return await self._group_api.insert_group(x_symphony_host="", create_group=create_group)

    @retry(retry=refresh_bearer_token_if_unauthorized)
    async def list_groups(self, status: Status = None, before: str = None, after: str = None, limit: int = None,
                          sort_order: SortOrder = None) -> GroupList:
        """List groups of type SDL
        See: `List all groups of specified type <https://developers.symphony.com/restapi/reference/listgroups>`_

        :param status: filter by status, active or deleted. If not specified, all of them are returned.
        :param before: NOT SUPPORTED YET, currently ignored.
        :param after: cursor that points to the end of the current page of data. If not present, the current page is
            the first page
        :param limit: maximum number of items to return
        :param sort_order: sorting direction of items (ordered by creation date)
        :return: the list of matching groups
        """
        kwargs = dict(x_symphony_host="", type_id="SDL")
        if status is not None:
            kwargs["status"] = status
        if before is not None:
            kwargs["before"] = before
        if after is not None:
            kwargs["after"] = after
        if limit is not None:
            kwargs["limit"] = limit
        if sort_order is not None:
            kwargs["sort_order"] = sort_order
        return await self._group_api.list_groups(**kwargs)

    async def list_all_groups(
              self,
              status: Status = None,
              chunk_size: int = 100,
              max_number: int = None
    ) -> AsyncGenerator[ReadGroup, None]:
        """Returns an asynchronous generator of groups of type SDL
        See: `List all groups of specified type <https://developers.symphony.com/restapi/reference/listgroups>`_

        :param status:      filter by status, active or deleted. If not specified, all of them are returned.
        :param chunk_size:  the maximum number of groups to return in one HTTP call. Default: 100.
        :param max_number:  the total maximum number of groups to retrieve. If set to None, we retrieve
                            all groups until the last page.
        :return:            an async generator of groups list.
        """

        async def groups_one_page(limit, after=None):
            result = await self.list_groups(status=status,
                                            limit=limit,
                                            after=after)
            return result.data, getattr(result.pagination.cursors, 'after', None)

        return cursor_based_pagination(groups_one_page, chunk_size, max_number)

    @retry(retry=refresh_bearer_token_if_unauthorized)
    async def update_group(self, if_match: str, group_id: str, update_group: UpdateGroup) -> ReadGroup:
        """Update an existing group
        See: `Update a group <https://developers.symphony.com/restapi/reference/updategroup>`_

        :param if_match: eTag of the group to be updated
        :param group_id: the ID of the group
        :param update_group: the group fields to be updated
        :return: the updated group
        """
        return await self._group_api.update_group(x_symphony_host="", if_match=if_match, group_id=group_id,
                                                  update_group=update_group)

    @retry(retry=refresh_bearer_token_if_unauthorized)
    async def update_avatar(self, group_id: str, image: str) -> ReadGroup:
        """Update the group avatar
        See: `Update the group avatar <https://developers.symphony.com/restapi/reference/updateavatar>`_

        :param group_id: the ID of the group
        :param image: The avatar image for the user profile picture.
            The image must be a base64-encoded .jpg, .png, or .gif. Image size limit: 2 MB
        :return: the updated group
        """
        upload_avatar = UploadAvatar(image=image)
        return await self._group_api.update_avatar(x_symphony_host="", group_id=group_id, upload_avatar=upload_avatar)

    @retry(retry=refresh_bearer_token_if_unauthorized)
    async def get_group(self, group_id: str) -> ReadGroup:
        """Retrieve a specific group
        See: `Retrieve a group <https://developers.symphony.com/restapi/reference/getgroup>`_

        :param group_id: the ID of the group to retrieve
        :return: the group details
        """
        return await self._group_api.get_group(x_symphony_host="", group_id=group_id)

    @retry(retry=refresh_bearer_token_if_unauthorized)
    async def add_member_to_group(self, group_id: str, user_id: int) -> ReadGroup:
        """Add a new user to an existing group.
        See: `Add a new user to an existing group <https://developers.symphony.com/restapi/reference/addmembertogroup>`_

        :param group_id: the ID of the group in which to add the user
        :param user_id: The ID of the user to be added into the group
        :return: the updated group
        """
        member = Member(member_id=user_id, member_tenant=extract_tenant_id(user_id))
        return await self._group_api.add_member_to_group(x_symphony_host="", group_id=group_id,
                                                         add_member=AddMember(member=member))


class OAuthSession:
    """Used to handle the bearer token needed to call Groups endpoints.
    """

    def __init__(self, login_client, session, retry_config):
        self._authentication_api = AuthenticationApi(login_client)
        self._auth_session = session
        self._bearer_token = None
        self._retry_config = retry_config

    @retry
    async def refresh(self):
        """Refreshes internal Bearer authentication token from the bot sessionToken.
        """
        jwt_token = await self._authentication_api.idm_tokens_post(await self._auth_session.session_token,
                                                                   scope="profile-manager")
        self._bearer_token = jwt_token.access_token

    async def get_auth_settings(self):
        """Used to set the authorization header defined in api_client.ApiClient.update_params_for_auth

        :return: the map of auth_settings containing the header value with the current bearer token
        """
        return {"bearerAuth": {"in": "header", "type": "bearer", "key": "Authorization",
                               "value": "Bearer " + await self._get_bearer_token()}}

    async def _get_bearer_token(self):
        """Returns the bearer token
        """
        if self._bearer_token is None:
            await self.refresh()
        return self._bearer_token
