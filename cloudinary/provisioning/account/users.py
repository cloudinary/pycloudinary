from cloudinary.api import only
from .account import _call_provisioning_api

USERS_SUB_PATH = "users"


class Role(object):
    """
    A user role to use in the user management API (create/update user).
    """
    MASTER_ADMIN = "master_admin"
    ADMIN = "admin"
    BILLING = "billing"
    TECHNICAL_ADMIN = "technical_admin"
    REPORTS = "reports"
    MEDIA_LIBRARY_ADMIN = "media_library_admin"
    MEDIA_LIBRARY_USER = "media_library_user"


def users(**options):
    """
    List all users
    :param options: Generic advanced options map, see online documentation.
    :return: List of users associated with the account
    """
    uri = [USERS_SUB_PATH]
    return _call_provisioning_api("get", uri,
                                  params=only(options, "user_ids", "sub_account_id", "pending", "prefix"), **options)


def create_user(name, email, role, sub_account_ids=None, **options):
    """
    Create a user
    :param name: Name of the user
    :param email: Email of the user
    :param role: Role of the user - use cloudinary.account.Role.<ROLE>
    :param sub_account_ids: Optional. Sub accounts to associate with the user
    :param options: Generic advanced options map, see online documentation.
    :return: Details of created user
    """
    uri = [USERS_SUB_PATH]
    return _call_provisioning_api("post", uri,
                                  params=dict(name=name, email=email, role=role, sub_account_ids=sub_account_ids),
                                  **options)


def delete_user(user_id, **options):
    """
    Delete a user
    :param user_id: ID of user to delete
    :param options: Generic advanced options map, see online documentation.
    :return: Result message
    """
    uri = [USERS_SUB_PATH, user_id]
    return _call_provisioning_api("delete", uri, {}, **options)


def user(user_id, **options):
    """
    Get information of a user
    :param user_id: ID of the user
    :param options: Generic advanced options map, see online documentation.
    :return: A user
    """
    uri = [USERS_SUB_PATH, user_id]
    return _call_provisioning_api("get", uri, {}, **options)


def update_user(user_id, **options):
    """
    Update a user
    :param user_id: ID of the user to update
    :param options: Generic advanced options map, see online documentation.
    :return: The updated user
    """
    uri = [USERS_SUB_PATH, user_id]
    return _call_provisioning_api("put", uri,
                                  params=only(options, "name", "email", "role", "sub_account_ids", "enabled"),
                                  **options)
