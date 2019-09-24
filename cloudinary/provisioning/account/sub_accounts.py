from cloudinary.api import only
from .account import _call_provisioning_api

SUB_ACCOUNTS_SUB_PATH = "sub_accounts"


def sub_accounts(**options):
    """
    List all sub accounts
    :param options: Generic advanced options map, see online documentation.
                enabled Optional. Whether to fetch enabled or disabled accounts. Default is all.
                ids     Optional. List of sub-account IDs. Up to 100. When provided, other filters are ignored.
                prefix  Optional. Search by prefix of the sub-account name. Case-insensitive.
    :return: A list of sub accounts
    """
    uri = [SUB_ACCOUNTS_SUB_PATH]
    return _call_provisioning_api("get", uri, params=only(options, "ids", "enabled", "prefix"), **options)


def create_sub_account(name, **options):
    """
    Create a new sub account
    :param name: Name of the new sub accounnt
    :param options: Generic advanced options map, see online documentation.
                cloudName        Optional, unique (case insensitive)
                customAttributes Advanced custom attributes for the sub-account.
                enabled          Optional. Whether to create the account as enabled (default is enabled).
                baseAccount      Optional. ID of sub-account from which to copy settings
    :return: The created sub account
    """
    uri = [SUB_ACCOUNTS_SUB_PATH]
    return _call_provisioning_api("post", uri,
                                  params=dict(
                                      name=name,
                                      **only(options, "cloud_name", "base_sub_account_id", "description")
                                  ),
                                  **options)


def delete_sub_account(sub_account_id, **options):
    """
    Delete a sub account
    :param sub_account_id: The id of the sub account
    :param options: Generic advanced options map, see online documentation. 
    :return: Result message
    """
    uri = [SUB_ACCOUNTS_SUB_PATH, sub_account_id]
    return _call_provisioning_api("delete", uri, {}, **options)


def sub_account(sub_account_id, **options):
    """
    Get information of a sub account
    :param sub_account_id: The id of the sub account
    :param options: Generic advanced options map, see online documentation. 
    :return: A sub account
    """
    uri = [SUB_ACCOUNTS_SUB_PATH, sub_account_id]
    return _call_provisioning_api("get", uri, {}, **options)


def update_sub_account(sub_account_id, **options):
    """
    Update a sub account
    :param sub_account_id: The id of the sub account
    :param options: Generic advanced options map, see online documentation.
                cloudName        Optional, unique (case insensitive)
                customAttributes Advanced custom attributes for the sub-account.
                enabled          Optional. Whether to create the account as enabled (default is enabled).
                baseAccount      Optional. ID of sub-account from which to copy settings
    :return: Updated sub account
    """
    uri = [SUB_ACCOUNTS_SUB_PATH, sub_account_id]
    return _call_provisioning_api("put", uri,
                                  params=only(options, "cloud_name", "description", "base_sub_account_id", "enabled"),
                                  **options)
