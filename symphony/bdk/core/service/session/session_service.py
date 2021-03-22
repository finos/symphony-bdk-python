from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.gen.pod_api.session_api import SessionApi
from symphony.bdk.gen.pod_model.user_v2 import UserV2


class OboSessionService:
    """Service interface exposing OBO-enabled endpoints to get user session information.
    """

    def __init__(self, session_api: SessionApi,
                 auth_session: AuthSession):
        self._session_api = session_api
        self._auth_session = auth_session

    async def get_session(
            self
    ) -> UserV2:
        """
        Retrieves the {@link UserV2} session from the pod using an {@link AuthSession} holder.

        Returns: User session info
        """
        params = {
            'session_token': await self._auth_session.session_token
        }
        return await self._session_api.v2_sessioninfo_get(**params)


class SessionService(OboSessionService):
    """Service class for exposing endpoints to get user session information.
    """

    def __init__(self, session_api: SessionApi,
                 auth_session: AuthSession):
        super().__init__(session_api, auth_session)

