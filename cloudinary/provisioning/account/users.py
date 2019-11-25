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


def users(user_ids=None, sub_account_id=None, pending=None, prefix=None, **options):
    """
    List all users

    :param user_ids:        The ids of the users to fetch
    :type user_ids:         list, optional
    :param sub_account_id:  The id of a sub account
    :type sub_account_id:   str, optional
    :param pending:         Whether the user is pending
    :type pending:          bool, optional
    :param prefix:          User prefix
    :type prefix:           str, optional
    :param options:         Generic advanced options dict, see online documentation.
    :type options:          dict, optional
    :return:                List of users associated with the account
    :rtype:                 dict
    """

    uri = [USERS_SUB_PATH]
    return _call_provisioning_api("get", uri,
                                  params=dict(
                                      user_ids=user_ids,
                                      sub_account_id=sub_account_id,
                                      pending=pending,
                                      prefix=prefix
                                  ), **options)


def create_user(name, email, role, sub_account_ids=None, **options):
    """
    Create a user

    :param name:                Username
    :type name:                 str
    :param email:               User's email
    :type email:                str
    :param role:                User's role
    :type role:                 str
    :param sub_account_ids:     Optional. Sub accounts to associate with the user
    :type sub_account_ids:      list, optional
    :param options:             Generic advanced options dict, see online documentation.
    :type options:              dict, optional
    :return:                    Details of created user
    :rtype:                     dict
    """
    uri = [USERS_SUB_PATH]
    return _call_provisioning_api("post", uri,
                                  params=dict(name=name, email=email, role=role, sub_account_ids=sub_account_ids),
                                  **options)


def delete_user(user_id, **options):
    """
    Delete a user

    :param user_id:             The id of user to delete
    :type user_id:              The id of user to delete
    :param options:             Generic advanced options dict, see online documentation.
    :type options:              dict, optional
    :return:                    Result message
    :rtype:                     dict
    """
    uri = [USERS_SUB_PATH, user_id]
    return _call_provisioning_api("delete", uri, {}, **options)


def user(user_id, **options):
    """
    Get information of a user

    :param user_id:             The id of the user
    :type user_id:              str
    :param options:             Generic advanced options dict, see online documentation.
    :type options:              dict, optional
    :return:                    A user
    :rtype:                     dict

    """
    uri = [USERS_SUB_PATH, user_id]
    return _call_provisioning_api("get", uri, {}, **options)


def update_user(user_id, name=None, email=None, role=None, sub_account_ids=None, enabled=True, **options):
    """
    Update a user

    :param user_id:             The id of the user to update
    :type user_id:              str
    :param name:                Username
    :type name:                 str, optional
    :param email:               User's email
    :type email:                str, optional
    :param role:                User's role
    :type role:                 Role, optional
    :param sub_account_ids:     Sub-accounts for which the user should have access
                                * If not provided or empty, the user should have access to all accounts
    :type sub_account_ids:      list, optional
    :param enabled:             Whether the account is enabled
    :type enabled:              bool, optional
    :param options:             Generic advanced options dict, see online documentation.
    :type options:              dict, optional
    :return:                    The updated user
    :rtype:                     dict
    """
    uri = [USERS_SUB_PATH, user_id]
    return _call_provisioning_api("put", uri,
                                  params=dict(
                                      user=user,
                                      name=name,
                                      email=email,
                                      role=role,
                                      sub_account_ids=sub_account_ids,
                                      enabled=enabled
                                  ),
                                  **options)
