from typing import List

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.core.retry import retry
from symphony.bdk.gen.pod_api.app_entitlement_api import AppEntitlementApi
from symphony.bdk.gen.pod_api.application_api import ApplicationApi
from symphony.bdk.gen.pod_model.application_detail import ApplicationDetail
from symphony.bdk.gen.pod_model.pod_app_entitlement import PodAppEntitlement
from symphony.bdk.gen.pod_model.user_app_entitlement import UserAppEntitlement
from symphony.bdk.gen.pod_model.user_app_entitlement_patch import UserAppEntitlementPatch


class ApplicationService:
    """Service class for managing the applications and the application entitlements.

    This services used for retrieving information about a particular application or application entitlements,
    performing some actions related to the applications like:

    * Create an application
    * Update an existing application
    * Delete an existing application
    * Get the information of an existing application
    * Update application entitlements
    * Update user applications
    """

    def __init__(
        self,
        application_api: ApplicationApi,
        app_entitlement_api: AppEntitlementApi,
        auth_session: AuthSession,
        retry_config: BdkRetryConfig,
    ):
        self._application_api = application_api
        self._app_entitlement_api = app_entitlement_api
        self._auth_session = auth_session
        self._retry_config = retry_config

    @retry
    async def create_application(self, application_detail: ApplicationDetail) -> ApplicationDetail:
        """
        Create a new application.

        See:

        * `Create Application <https://developers.symphony.com/restapi/reference/create-app>`_
        * `Create Application with an RSA Public Key <https://developers.symphony.com/restapi/reference/create-application-with-an-rsa-public-key>`_

        :param application_detail:  Contains the following fields for creating an application: appId, name, appUrl,
                                    domain, and publisher. Note that appUrl is not required.

        :return: The created application.

        """
        params = {
            "application_detail": application_detail,
            "session_token": await self._auth_session.session_token,
        }
        return await self._application_api.v1_admin_app_create_post(**params)

    @retry
    async def update_application(
        self, app_id: str, application_detail: ApplicationDetail
    ) -> ApplicationDetail:
        """
        Update an existing application.

        See:

        * `Update Application <https://developers.symphony.com/restapi/reference/update-application>`_
        * `Update Application with an RSA Public Key <https://developers.symphony.com/restapi/reference/update-application-with-an-rsa-public-key>`_

        :param app_id:              Id of the application needs to be updated.
        :param application_detail:  Contains the following fields for creating an application: appId, name, appUrl,
                                    domain, and publisher. Note that appUrl is not required.

        :return: The updated application.

        """
        params = {
            "id": app_id,
            "application_detail": application_detail,
            "session_token": await self._auth_session.session_token,
        }
        return await self._application_api.v1_admin_app_id_update_post(**params)

    @retry
    async def delete_application(self, app_id: str) -> None:
        """
        Delete an existing application.

        See: `Delete Application <https://developers.symphony.com/restapi/reference/delete-application>`_

        :param app_id:  Id of the application needs to be deleted.

        """
        params = {"id": app_id, "session_token": await self._auth_session.session_token}
        await self._application_api.v1_admin_app_id_delete_post(**params)

    @retry
    async def get_application(self, app_id: str) -> ApplicationDetail:
        """
        Get an existing application.

        See: `Get Application <https://developers.symphony.com/restapi/reference/get-application>`_

        :param app_id:  Id of the application.

        :return: The detail of the lookup application.

        """
        params = {"id": app_id, "session_token": await self._auth_session.session_token}
        return await self._application_api.v1_admin_app_id_get_get(**params)

    @retry
    async def list_application_entitlements(self) -> List[PodAppEntitlement]:
        """
        Get the list of application entitlements for the company.

        See: `List App Entitlements <https://developers.symphony.com/restapi/reference/list-app-entitlements>`_

        :return: The list of application entitlements.

        """
        params = {"session_token": await self._auth_session.session_token}
        pod_app_entitlement_list = (
            await self._app_entitlement_api.v1_admin_app_entitlement_list_get(**params)
        )
        return pod_app_entitlement_list

    @retry
    async def update_application_entitlements(
        self, entitlements: List[PodAppEntitlement]
    ) -> List[PodAppEntitlement]:
        """
        Update the list of application entitlements for the company.

        See: `Update App Entitlements <https://developers.symphony.com/restapi/reference/update-application-entitlements>`_

        :param entitlements: The list of entitlements to be updated by.

        :return: The updated list of entitlements.

        """
        params = {
            "payload": entitlements,
            "session_token": await self._auth_session.session_token,
        }
        pod_app_entitlement_list = (
            await self._app_entitlement_api.v1_admin_app_entitlement_list_post(**params)
        )
        return pod_app_entitlement_list

    @retry
    async def list_user_applications(self, user_id: int) -> List[UserAppEntitlement]:
        """
        Get the list of Symphony application entitlements for a particular user.

        See: `User Apps <https://developers.symphony.com/restapi/reference/user-apps>`_

        :param user_id: User Id

        :return: The list of Symphony application entitlements for this user.

        """
        params = {"uid": user_id, "session_token": await self._auth_session.session_token}
        user_app_entitlement_list = (
            await self._app_entitlement_api.v1_admin_user_uid_app_entitlement_list_get(**params)
        )
        return user_app_entitlement_list

    @retry
    async def update_user_applications(
        self, user_id: int, user_app_entitlements: List[UserAppEntitlement]
    ):
        """
        Update the application entitlements for a particular user.

        See: `Update User Apps <https://developers.symphony.com/restapi/reference/update-user-apps>`_

        :param user_id:                 User Id
        :param user_app_entitlements:   The list of App Entitlements needs to be updated.

        :return: The updated list of Symphony application entitlements for this user.

        """
        params = {
            "uid": user_id,
            "payload": user_app_entitlements,
            "session_token": await self._auth_session.session_token,
        }
        user_app_entitlement_list = (
            await self._app_entitlement_api.v1_admin_user_uid_app_entitlement_list_post(**params)
        )
        return user_app_entitlement_list

    @retry
    async def patch_user_applications(
        self, user_id: int, user_app_entitlements: List[UserAppEntitlementPatch]
    ):
        """
        Updates particular app entitlements for a particular user. Supports partial update.

        See: `Update User Apps <https://developers.symphony.com/restapi/reference/partial-update-user-apps>`_

        :param user_id: User Id
        :param user_app_entitlements: The list of App Entitlements needs to be updated.

        :return: The updated list of Symphony application entitlements for this user.

        """
        params = {
            "uid": user_id,
            "payload": user_app_entitlements,
            "session_token": await self._auth_session.session_token,
        }
        user_app_entitlements_list = (
            await self._app_entitlement_api.v1_admin_user_uid_app_entitlement_list_patch(**params)
        )
        return user_app_entitlements_list
