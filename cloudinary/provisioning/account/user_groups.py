from cloudinary.api import only as _only
from .account import _call_provisioning_api

USER_GROUPS_SUB_PATH = "user_groups"


def user_groups(**options):
    # type: (**any) -> ProvisioningAPIResponse
    """
    List all user groups
    :param options: Generic advanced options map, see online documentation
    :return:        List of user groups
    """
    uri = [USER_GROUPS_SUB_PATH]
    return _call_provisioning_api("get", uri, {}, **options)


def create_user_group(name, **options):
    # type: (str, **any) -> ProvisioningAPIResponse
    """
    Create a new user group
    :param name:    Name of the user group
    :param options: Generic advanced options map, see online documentation
    :return:        The newly created group
    """
    uri = [USER_GROUPS_SUB_PATH]
    return _call_provisioning_api("post", uri, dict(name=name), **options)


def update_user_group(user_group_id, **options):
    # type: (str, **any) -> ProvisioningAPIResponse
    """
    Update a user group
    :param user_group_id:       The id of the user group to update
    :param options:             Generic advanced options map, see online documentation
        :keyword name (str):    Name of the user group
    :return: The updated group
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id]
    return _call_provisioning_api("put", uri, _only(options, "name"), **options)


def delete_user_group(user_group_id, **options):
    # type: (str, **any) -> ProvisioningAPIResponse
    """
    Delete a user group
    :param user_group_id:   The id of the user group to delete
    :param options:         Generic advanced options map, see online documentation
    :return:                The result message
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id]
    return _call_provisioning_api("delete", uri, {}, **options)


def user_group(user_group_id, **options):
    # type: (str, **any) -> ProvisioningAPIResponse
    """
    Get information of a user group
    :param user_group_id:   The id of the user group
    :param options:         Generic advanced options map, see online documentation
    :return:                Details of the group
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id]
    return _call_provisioning_api("get", uri, {}, **options)


def add_user_to_group(user_group_id, user_id, **options):
    # type: (str, str, **any) -> ProvisioningAPIResponse
    """
    Add a user to a user group
    :param user_group_id:   The id of the user group to add the user to
    :param user_id:         The user id to add
    :param options:         Generic advanced options map, see online documentation
    :return:                List of users in the group
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id, "users", user_id]
    return _call_provisioning_api("post", uri, {}, **options)


def remove_user_from_group(user_group_id, user_id, **options):
    # type: (str, str, **any) -> ProvisioningAPIResponse
    """
    Remove a user from a user group
    :param user_group_id:   The id of the user group to remove the user from
    :param user_id:         The id of the user to remove
    :param options:         Generic advanced options map, see online documentation
    :return:                List of users in the group
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id, "users", user_id]
    return _call_provisioning_api("delete", uri, {}, **options)


def user_group_users(user_group_id, **options):
    # type: (str, **any) -> ProvisioningAPIResponse
    """
    Get all users in a user group
    :param user_group_id:   The id of user group to get list of users
    :param options:         Generic advanced options map, see online documentation
    :return:                List of users in the group
    """
    uri = [USER_GROUPS_SUB_PATH, user_group_id, "users"]
    return _call_provisioning_api("get", uri, {}, **options)


def user_in_user_groups(user_id, **options):
    # type: (str, **any) -> ProvisioningAPIResponse
    """
    Get all user groups a user belongs to
    :param user_id:     The id of user
    :param options:     Generic advanced options map, see online documentation
    :return:            List of groups user is in
    """
    uri = [USER_GROUPS_SUB_PATH, user_id]
    return _call_provisioning_api("get", uri, {}, **options)
