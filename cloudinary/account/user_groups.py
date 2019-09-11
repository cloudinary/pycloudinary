from cloudinary.api import only as _only
from .account import call_api


def user_groups(**options):
    """
    List all user groups
    :param options: Advanced options
    :return: List of user groups
    """
    uri = ['user_groups']
    return call_api("get", uri, {}, **options)


def create_user_group(name, **options):
    """
    Create a new user group
    :param name: Name of the user group
    :param options: Advanced options
    :return: The created user group
    """
    uri = ['user_groups']
    return call_api("post", uri, dict(name=name), **options)


def update_user_group(user_group_id, **options):
    """
    Update a user group
    :param user_group_id: ID of the user group to update
    :param options: Advanced options
    :return: The updated user group
    """
    uri = ['user_groups', user_group_id]
    return call_api("put", uri, _only(options, "name"), **options)


def delete_user_group(user_group_id, **options):
    """
    Delete a user group
    :param user_group_id: ID of the user group to delete
    :param options: Advanced options
    :return: The deleted user group
    """
    uri = ['user_groups', user_group_id]
    return call_api("delete", uri, {}, **options)


def user_group(user_group_id, **options):
    """
    Get information of a user group
    :param user_group_id: ID of the user group
    :param options: Advanced options
    :return: The user group
    """
    uri = ['user_groups', user_group_id]
    return call_api("get", uri, {}, **options)


def add_user_to_user_group(user_group_id, user_id, **options):
    """
    Add a user to a user group
    :param user_group_id: ID of the user group to add the user to
    :param user_id: ID of user to add
    :param options: Advanced options
    :return: List of users in the group
    """
    uri = ['user_groups', user_group_id, 'users', user_id]
    return call_api("post", uri, {}, **options)


def remove_user_from_user_group(user_group_id, user_id, **options):
    """
    Remove a user from a user group
    :param user_group_id: ID of the user group to remove the user from
    :param user_id: ID of the user to remove
    :param options: Advanced options
    :return: List of users in the group
    """
    uri = ['user_groups', user_group_id, 'users', user_id]
    return call_api("delete", uri, {}, **options)


def users_in_user_group(user_group_id, **options):
    """
    Get all users in a user group
    :param user_group_id: ID of user group to get list of users
    :param options: Advanced options
    :return: List of users in the group
    """
    uri = ['user_groups', user_group_id, 'users']
    return call_api("get", uri, {}, **options)


def user_in_user_groups(user_id, **options):
    """
    Get all user groups a user belongs to
    :param user_id: ID of user
    :param options: Advanced options
    :return: List of groups user is in
    """
    uri = ['users', user_id]
    return call_api("get", uri, {}, **options)
