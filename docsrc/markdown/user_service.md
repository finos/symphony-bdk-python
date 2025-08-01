# User service
The User Service is a component at the service layer of the BDK which covers the User part of the [REST API documentation](https://developers.symphony.com/restapi).
More precisely:
* [Create user](https://rest-api.symphony.com/main/user-management/create-user-v2)
* [Update user](https://rest-api.symphony.com/main/user-management/update-user-v2)
* [Suspend user](https://rest-api.symphony.com/v20.10/main/user-management/suspend-user-v1)
* [Unsuspend user](https://rest-api.symphony.com/v20.10/main/user-management/suspend-user-v1)
* [Get user details](https://rest-api.symphony.com/main/user-management/get-user-v2)
* [List all user details](https://rest-api.symphony.com/main/user-management/list-users-v2)
* [List users by ids](https://rest-api.symphony.com/main/user-management/users-lookup-v3)
* [List users by emails](https://rest-api.symphony.com/main/user-management/users-lookup-v3)
* [List users by usernames](https://rest-api.symphony.com/main/user-management/users-lookup-v3)
* [Search users](https://rest-api.symphony.com/main/user-management/search-users)
* [Find users by filter](https://rest-api.symphony.com/main/user-management/find-users)
* [Add role to user](https://rest-api.symphony.com/main/user-management/add-role)
* [List roles](https://rest-api.symphony.com/main/user-management/list-roles)
* [Remove a role](https://rest-api.symphony.com/main/user-management/remove-role)
* [Get avatar](https://rest-api.symphony.com/main/user-management/user-avatar)
* [Update avatar](https://rest-api.symphony.com/main/user-management/update-user-avatar)
* [Get disclaimer](https://rest-api.symphony.com/main/user-management/user-disclaimer)
* [Remove disclaimer](https://rest-api.symphony.com/main/user-management/unassign-user-disclaimer)
* [Add disclaimer](https://rest-api.symphony.com/main/user-management/update-disclaimer)
* [Get user delegates](https://rest-api.symphony.com/main/user-management/delegates)
* [Update user delegates](https://rest-api.symphony.com/main/user-management/update-delegates)
* [Get feature entitlements for a user](https://rest-api.symphony.com/main/user-management/features)
* [Update feature entitlements for a user](https://rest-api.symphony.com/main/user-management/update-features)
* [Get user status](https://rest-api.symphony.com/main/user-management/user-status)
* [Update user status](https://rest-api.symphony.com/main/user-management/update-user-status)
* [Follow a user](https://rest-api.symphony.com/main/user-management/follow-user)
* [Unfollow a user](https://rest-api.symphony.com/main/user-management/unfollow-user)
* [List user followers](https://rest-api.symphony.com/main/user-management/list-user-followers)
* [List followed users](https://rest-api.symphony.com/main/user-management/list-users-followed)
* [List audit trail](https://rest-api.symphony.com/main/user-management/list-audit-trail-v1)
* [Get user manifest](https://rest-api.symphony.com/main/user-management/user-manifest)
* [Update user manifest](https://rest-api.symphony.com/main/user-management/update-user-manifest)


## How to use
The central component for the User Service is the `UserService` class, it exposes the service APIs endpoints mentioned above.  
The service is accessible from the`SymphonyBdk` object by calling the `users()` method:

```python
class UsersMain:
    @staticmethod
    async def run():
        bdk_config = BdkConfigLoader.load_from_file("path/to/config.yaml")
        async with SymphonyBdk(bdk_config) as bdk:
            users_service = bdk.users()
            users = await users_service.list_users_by_ids([123, 456])
            print(users)


if __name__ == "__main__":
    asyncio.run(UsersMain.run())
```