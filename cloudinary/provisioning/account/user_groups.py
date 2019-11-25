from cloudinary.api import only as _only
from .account import _call_provisioning_api

USER_GROUPS_SUB_PATH = "user_groups"


def user_groups(**options):
    """
    List all user groups

    :param options:         Generic advanced options dict, see online documentation
    :type options:          dict, optional
    :return:                List of user groups
    :rtype:                 ProvisioningAPIRespose
    """
    uri = [USER_GROUPS_SUB_PATH]
    return _call_provisioning_api("get", uri, {}, **options)


def create_user_group(name, **options):
    """
    Create a new user group

    :param name:            Name of the user group
    :type name:             str
    :param options:         Generic advanced options dict, see online documentation
    :type options:          dict, optional
    :return:                The newly created group
    :rtype:                 dict
    """
    uri = [USER_GROUPS_SUB_PATH]
    return _call_provisioning_api("post", uri, dict(name=name), **options)


def update_user_group(user_group_id, name, **options):
    """
    Update a user group

    :param user_group_id:       The id of the user group to update
    :type user_group_id:        str
    :param name:                Name of the user group
    :type name:                 str, optional
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    The updated group
    :rtype:                     dict
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id]
    return _call_provisioning_api("put", uri, dict(name=name), **options)


def delete_user_group(user_group_id, **options):
    """
    Delete a user group

    :param user_group_id:       The id of the user group to delete
    :type user_group_id:        str
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    The result message
    :rtype:                     dict
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id]
    return _call_provisioning_api("delete", uri, {}, **options)


def user_group(user_group_id, **options):
    """
    Get information of a user group

    :param user_group_id:       The id of the user group
    :type user_group_id:        str
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    Details of the group
    :rtype:                     dict
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id]
    return _call_provisioning_api("get", uri, {}, **options)


def add_user_to_group(user_group_id, user_id, **options):
    """
    Add a user to a user group

    :param user_group_id:       The id of the user group to add the user to
    :type user_group_id:        str
    :param user_id:             The user id to add
    :type user_id:              str
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    List of users in the group
    :rtype:                     dict
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id, "users", user_id]
    return _call_provisioning_api("post", uri, {}, **options)


def remove_user_from_group(user_group_id, user_id, **options):
    """
    Remove a user from a user group

    :param user_group_id:       The id of the user group to remove the user from
    :type user_group_id:        str
    :param user_id:             The id of the user to remove
    :type user_id:              str
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    List of users in the group
    :rtype:                     dict
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id, "users", user_id]
    return _call_provisioning_api("delete", uri, {}, **options)


def user_group_users(user_group_id, **options):
    """
    Get all users in a user group

    :param user_group_id:       The id of user group to get list of users
    :type user_group_id:        str
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    List of users in the group
    :rtype:                     dict
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id, "users"]
    return _call_provisioning_api("get", uri, {}, **options)


def user_in_user_groups(user_id, **options):
    """
    Get all user groups a user belongs to

    :param user_id:             The id of user
    :param user_id:             str
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    List of groups user is in
    :rtype:                     dict

    """
    uri = [USER_GROUPS_SUB_PATH, user_id]
    return _call_provisioning_api("get", uri, {}, **options)
