from enum import Enum

from cloudinary.api import only as _only
from .account import call_api


class Role(Enum):
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
    :param options: Advanced options
    :return: List of users associated with the account
    """
    uri = ['users']
    return call_api("get", uri, _only(options, "user_ids", "sub_account_id", "pending", "prefix"), **options)


def create_user(name, email, role, sub_account_ids, **options):
    """
    Create a user
    :param name: Name of the user
    :param email: Email of the user
    :param role: Role of the user - use cloudinary.account.Role.<ROLE>
    :param sub_account_ids: Sub accounts to associate with the user
    :param options: Advanced options
    :return: Details of created user
    """
    uri = ['users']
    return call_api("post", uri, dict(name=name, email=email, role=role, sub_account_ids=sub_account_ids), **options)


def delete_user(user_id, **options):
    """
    Delete a user
    :param user_id: ID of user to delete
    :param options: Advanced options
    :return: Result message
    """
    uri = ['users', user_id]
    return call_api("delete", uri, {}, **options)


def user(user_id, **options):
    """
    Get information of a user
    :param user_id: ID of the user
    :param options: Advanced options
    :return: A user
    """
    uri = ['users', user_id]
    return call_api("get", uri, {}, **options)


def update_user(user_id, **options):
    """
    Update a user
    :param user_id: ID of the user to update
    :param options: Advanced options
    :return: The updated user
    """
    uri = ['users', user_id]
    return call_api("put", uri, _only(options, "name", "email", "role", "sub_account_ids", "enabled"), **options)
