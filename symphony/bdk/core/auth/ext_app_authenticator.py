from abc import ABC, abstractmethod

from symphony.bdk.core.auth.auth_session import AppAuthSession
from symphony.bdk.core.auth.jwt_helper import validate_jwt, create_signed_jwt
from symphony.bdk.core.config.model.bdk_rsa_key_config import BdkRsaKeyConfig
from symphony.bdk.gen import ApiClient
from symphony.bdk.gen.login_api.authentication_api import AuthenticationApi
from symphony.bdk.gen.login_model.authenticate_extension_app_request import AuthenticateExtensionAppRequest
from symphony.bdk.gen.login_model.extension_app_tokens import ExtensionAppTokens
from symphony.bdk.gen.pod_api.pod_api import PodApi
from symphony.bdk.gen.pod_model.pod_certificate import PodCertificate


class ExtensionAppAuthenticator(ABC):

    @abstractmethod
    async def authenticate_extension_app(self, app_token: str):
        pass

    @abstractmethod
    async def validate_jwt(self, jwt: str):
        pass

    @abstractmethod
    async def validate_tokens(self, app_token: str, symphony_token: str):
        pass

    @abstractmethod
    async def get_pod_certificate(self):
        pass


class ExtensionAppAuthenticatorRsa(ExtensionAppAuthenticator):

    def __init__(self, login_client: ApiClient, pod_client: ApiClient, app_id: str,
                 private_key_config: BdkRsaKeyConfig):
        self._authentication_api = AuthenticationApi(login_client)
        self._pod_api = PodApi(pod_client)
        self._app_id = app_id
        self._private_key_config = private_key_config
        self._tokens = {}

    async def authenticate_extension_app(self, app_token: str) -> AppAuthSession:
        auth_session = AppAuthSession(self, app_token)
        await auth_session.refresh()

        return auth_session

    async def authenticate_and_retrieve_tokens(self, app_token: str) -> ExtensionAppTokens:
        jwt = create_signed_jwt(self._private_key_config, self._app_id)
        authentication_request = AuthenticateExtensionAppRequest(app_token=app_token, auth_token=jwt)
        return self._authentication_api.v1_pubkey_app_authenticate_extension_app_post(authentication_request)

    async def validate_jwt(self, jwt: str):
        return validate_jwt(jwt, self.get_pod_certificate().certificate)

    async def validate_tokens(self, app_token: str, symphony_token: str):
        return app_token in self._tokens and self._tokens[app_token] == symphony_token

    async def get_pod_certificate(self) -> PodCertificate:
        return self._pod_api.v1_podcert_get()
