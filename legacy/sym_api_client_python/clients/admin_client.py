import logging

from .api_client import APIClient


# child class of APIClient --> Extends error handling functionality
# AdminClient class contains a series of functions corresponding to all
# pod admin endpoints on the REST API.
class AdminClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def admin_get_user(self, user_id):
        """
        Returns details for a particular user.

        Calling this endpoint requires the
        ACCESS_USER_PROVISIONING_API and ACCESS_ADMIN_API privileges.
        """
        logging.debug('AdminClient/admin_get_user()')
        url = '/pod/v2/admin/user/{0}'.format(user_id)
        return self.bot_client.execute_rest_call("GET", url)

    def admin_list_users(self, skip=0, limit=50):
        """
        Returns a list of users ID, including user metadata

        Calling this endpoint requires the ACCESS_USER_PROVISIONING_API privilege.
        """
        logging.debug('AdminClient/admin_list_users()')
        url = '/pod/v2/admin/user/list'
        params = {'skip': skip, 'limit': limit}

        return self.bot_client.execute_rest_call("GET", url, params=params)
    
    def admin_create_user(self, user_attributes):
        """
        Creates a new user, either End-User or Service User.

        --End-User Accounts are assigned to employees. 
        To create an end user account, the accountType field must be NORMAL.
        -- Service User Accounts are a type of account used for bots or applications, 
        rather than end-users. To create a service user account, 
        the accountType field must be SYSTEM.

        Calling this endpoint requires the
        ACCESS_USER_PROVISIONING_API and ACCESS_ADMIN_API privileges.

        TODO: Add `Password` object generation
        """
        logging.debug('AdminClient/admin_list_users()')
        url = '/pod/v2/admin/user/create'
        return self.bot_client.execute_rest_call("POST", url, json=user_attributes)
    
    def admin_update_user(self, user_id, updated_user_attributes):
        """
        Updates an existing user.

        BODY PARAMS

            emailAddress
            The user's email address.

            firstName
            The user's first name.

            lastName
            The user's last name.

            userName
            The user's name. The username must be unique and must not match any existing usernames or app IDs.

            displayName
            The user's display name.

            companyName
            The name of the user's company.

            department
            The user's department.

            division
            The user's division.

            title
            The user's title.

            twoFactorAuthPhone
            The user's two factor authentication mobile phone number.

            workPhoneNumber
            The user's work phone number.

            mobilePhoneNumber
            The user's mobile number.

            smsNumber
            The user's SMS number.

            accountType
            The user's account type. Possible values: NORMAL, SYSTEM.

            location
            The user's location.

            jobFunction
            The user's job function. Possible values: Project Manager, Trader, Sales, Strategist, Business Development Executive, Corporate Access, Analyst, Other, Research Analyst, Developer, Economist, Portfolio Manager, Director.

            assetClasses
            The user's asset classes. Possible values: Fixed Income, Currencies, Commodities, Equities.

            industries
            The user's industries. Possible values: Conglomerates, Healthcare, Transportation, Services, Energy & Utilities, Real Estate, Consumer Cyclicals, Financials, Basic Materials, Consumer Non-Cyclicals, Technology.

            currentKey
            A UserKeyRequest Object object containing the current RSA key information to use for authenticating the user. When updating the user, this can be set (rotated) to a new key, in which case the existing key is stored in the previousKey and can be used for authentication during the current session. For more information see RSA Bot Authentication Workflow.

            previousKey
            A UserKeyRequest Object object containing the RSA key information from the previous key in a key rotation scenario. The previous key can be used when the currentKey has been updated during the current session. The previousKey is valid for 72 hours. For more information see RSA Bot Authentication Workflow.



        Calling this endpoint requires the ACCESS_USER_PROVISIONING_API and ACCESS_ADMIN_API privileges.
        """
        logging.debug('AdminClient/admin_update_user()')
        url = '/pod/v2/admin/user/{0}/update'.format(user_id)
        return self.bot_client.execute_rest_call("POST", url, json=updated_user_attributes)

    def admin_get_user_avatar(self, user_id):
        """
        Returns the URL of the avatar of a particular user.

        Calling this endpoint requires the ACCESS_USER_PROVISIONING_API privilege.
        """
        logging.debug('AdminClient/admin_get_user_avatar')
        url = '/pod/v1/admin/user/{0}/avatar'.format(user_id)
        return self.bot_client.execute_rest_call("GET", url)

    def admin_update_avatar(self, user_id, image_encoded_string):
        """
        Updates the avatar of a particular user. file_path to base64 encoded image

        TODO: base64 encode the image in the file_path

        Calling this endpoint requires the User Provisioning role with ACCESS_USER_PROVISIONING_API privilege.
        """
        logging.debug('AdminClient/admin_update_avatar')
        url = '/pod/v1/admin/user/{0}/avatar/update'.format(user_id)
        #base64encode the image file
        data = {'image': image_encoded_string}
        return self.bot_client.execute_rest_call("POST", url, json=data)    

    def admin_get_user_status(self, user_id):
        """
        Get the status, active or inactive, for a particular user.

        Calling this endpoint requires the User Provisioning role with ACCESS_USER_PROVISIONING_API privilege.
        """
        logging.debug('AdminClient/admin_get_user_status()')
        url = '/pod/v1/admin/user/{0}/status'.format(user_id)
        return self.bot_client.execute_rest_call("GET", url)

    def admin_update_user_status(self, user_id, status):
        """
        Update the status of a particular user.

        `status` can be 'ENABLED' or 'DISABLED' 

        Calling this endpoint requires the User Provisioning role with ACCESS_USER_PROVISIONING_API privilege.
        """
        logging.debug('AdminClient/admin_update_user_status()')
        url = '/pod/v1/admin/user/{0}/status/update'.format(user_id)
        data  = {'status': status}
        return self.bot_client.execute_rest_call("POST", url, json=data)

    def admin_list_pod_features(self):
        """
        Returns the full set of Symphony features available for this pod.

        Features entitlements definition:

            postReadEnabled: Allows the user to read wall posts.
            postWriteEnabled: Allows the user to write wall posts.
            delegatesEnabled: Allows the user to have delegates.
            isExternalIMEnabled: Allows the user to chat in external IM/MIMs.
            canShareFilesExternally: Allows the user to share files externally.
            canCreatePublicRoom: Allows the user to create internal public rooms.
            canUpdateAvatar: Allows the user to edit profile picture.
            isExternalRoomEnabled: Allows the user to chat in private external rooms.
            canCreatePushedSignals: Allows the user to create push signals.
            canUseCompactMode: Enables Lite Mode.
            mustBeRecorded: Must be recorded in meetings.
            sendFilesEnabled: Allows the user to send files internally.
            canUseInternalAudio: Allows the user to use audio in internal Meetings.
            canUseInternalVideo: Allows the user to use video in internal Meetings.
            canProjectInternalScreenShare: Allows the user to share screens in internal Meetings.
            canViewInternalScreenShare: Allows the user to view shared screens in internal Meetings.
            canCreateMultiLateralRoom: Allows the user to create multi-lateral room.
            canJoinMultiLateralRoom: Allows the user to join multi-lateral room.
            canUseFirehose: Allows the user to use Firehose.
            canUseInternalAudioMobile: Allows the user to use audio in internal meetings on mobile.
            canUseInternalVideoMobile: Allows the user to use video in internal meetings on mobile.
            canProjectInternalScreenShareMobile: Allows the user to share screens in internal meetings on mobile.
            canViewInternalScreenShareMobile: Allows the user to view shared screens in internal meetings on mobile.
            canManageSignalSubscription: Allows the user to manage signal subscriptions.

Calling this endpoint requires the User Provisioning role with ACCESS_USER_PROVISIONING_API privilege.
"""
        logging.debug('AdminClient/admin_list_pod_features()')
        url = '/pod/v1/admin/system/features/list'
        return self.bot_client.execute_rest_call("GET", url)

    def admin_get_user_features(self, user_id):
        """
        Returns the list of Symphony feature entitlements for a particular user.

        Use the data returned from this endpoint with Find Users to filter users by a specific entitlement.

        Calling this endpoint requires the User Provisioning role with ACCESS_USER_PROVISIONING_API privilege.
        """
        logging.debug('AdminClient/admin_get_user_features()')
        url = '/pod/v1/admin/user/{0}/features'.format(user_id)
        return self.bot_client.execute_rest_call("GET", url)

    def admin_update_user_features(self, user_id, feature_list):
        """
        Updates the feature entitlements for a particular user.

        featureList -the features to update. Specified by entitlement name and enabled (true or false).

        Calling this endpoint requires the User Provisioning role with ACCESS_USER_PROVISIONING_API privilege.
        """
        logging.debug('AdminClient/admin_update_user_features()')
        url = '/pod/v1/admin/user/{0}/features/update'.format(user_id)
        return self.bot_client.execute_rest_call("POST", url, json=feature_list)

    def admin_find_users(self, filters, skip=0, limit=50):
        """
        Finds a list of users based on a specified role or feature entitlement.

        'filters' is a dictionary that can contain:
            'role'    -- int64: User role
            'feature' -- string: Feature entitlement value
            'status'  -- string: 'ENABLED' or 'DISABLED'

        Calling this endpoint requires the User Provisioning role
        with ACCESS_USER_PROVISIONING_API privilege.
        """ 
        logging.debug('AdminClient/admin_find_users()')
        url = '/pod/v1/admin/user/find'
        params = {'skip': skip, 'limit': limit}
        return self.bot_client.execute_rest_call("POST", url, params=params, json=filters)

    def admin_list_roles(self):
        """
        Returns a list of all roles available in the company (pod).

        Calling this endpoint requires the ACCESS_ADMIN_API privilege.
        """
        logging.debug('AdminClient/admin_list_roles()')
        url = '/pod/v1/admin/system/roles/list'
        return self.bot_client.execute_rest_call("GET", url)

    def admin_add_role(self, user_id, payload={}):
        """
        Add a role or optional entitleable action to a user's account. For example: {"id":"COMPLIANCE_OFFICER.MONITOR_ROOMS"}

        Calling this endpoint requires the User Provisioning role with ACCESS_USER_PROVISIONING_API privilege.
        """
        logging.debug('AdminClient/admin_add_role()')
        url = '/pod/v1/admin/user/{0}/roles/add'.format(user_id)

        return self.bot_client.execute_rest_call("POST", url, json=payload)

    def admin_remove_role(self, user_id, payload={}):
        """
        Remove a role or optional entitleable action to a user's account. For example: {"id":"L2_SUPPORT"}

        Calling this endpoint requires the User Provisioning role with ACCESS_USER_PROVISIONING_API privilege.
        """
        logging.debug('AdminClient/admin_remove_role()')
        url = '/pod/v1/admin/user/{0}/roles/remove'.format(user_id)
        return self.bot_client.execute_rest_call("POST", url, json=payload)


    def import_message(self, imported_message):
        logging.debug('MessageClient/import_message()')
        url = '/agent/v4/message/import'
        return self.bot_client.execute_rest_call("POST", url, json=imported_message)

    # go on admin clients
    def suppress_message(self, message_id):
        logging.debug('MessageClient/suppress_message()')
        url = '/pod/v1/admin/messagesuppression/{0}/suppress'.format(message_id)
        return self.bot_client.execute_rest_call("POST", url)



