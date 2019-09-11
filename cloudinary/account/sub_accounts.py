from cloudinary.api import only as _only
from .account import call_api


def sub_accounts(**options):
    """
    List all sub accounts
    :param options: Advanced options 
    :return: A list of sub accounts
    """
    uri = ['sub_accounts']
    return call_api("get", uri, _only(options, "ids", "enabled", "prefix"), **options)


def create_sub_account(name, **options):
    """
    Create a new sub account
    :param name: Name of the new sub accounnt
    :param options: Advanced options 
    :return: The created sub account
    """
    uri = ['sub_accounts']
    return call_api("post", uri, dict(name=name,
                                      **_only(options, "cloud_name", "base_sub_account_id", "description")), **options)


def delete_sub_account(sub_account_id, **options):
    """
    Delete a sub account
    :param sub_account_id: ID of sub account to delete
    :param options: Advanced options 
    :return: Result message
    """
    uri = ['sub_accounts', sub_account_id]
    return call_api("delete", uri, {}, **options)


def sub_account(sub_account_id, **options):
    """
    Get information of a sub account
    :param sub_account_id: ID of sub account
    :param options: Advanced options 
    :return: A sub account
    """
    uri = ['sub_accounts', sub_account_id]
    return call_api("get", uri, {}, **options)


def update_sub_account(sub_account_id, **options):
    """
    Update a sub account
    :param sub_account_id: ID of sub account to update
    :param options: Advanced options 
    :return: Updated sub account
    """
    uri = ['sub_accounts', sub_account_id]
    return call_api("put", uri,
                    _only(options, "cloud_name", "description", "base_sub_account_id", "enabled"), **options)
