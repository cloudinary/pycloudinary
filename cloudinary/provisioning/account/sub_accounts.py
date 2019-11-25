from .account import _call_provisioning_api

SUB_ACCOUNTS_SUB_PATH = "sub_accounts"


def sub_accounts(enabled=True, ids=None, prefix=None, **options):
    """
    List all sub accounts

    :param enabled:     Whether to fetch enabled or disabled accounts. Default is all.
    :type enabled:      bool, optional
    :param ids:         List of sub-account IDs. Up to 100. When provided, other filters are ignored.
    :type ids:          list, optional
    :param prefix:      Search by prefix of the sub-account name. Case-insensitive.
    :type prefix:       str, optional
    :param options:     Generic advanced options dict, see online documentation
    :type options:      dict, optional
    :return:            A list of sub accounts
    :rtype:             dict
    """
    uri = [SUB_ACCOUNTS_SUB_PATH]
    return _call_provisioning_api("get", uri, params=dict(ids=ids, enabled=enabled, prefix=prefix), **options)


def create_sub_account(name, cloud_name=None, custom_attributes=None, enabled=True,
                       base_account=None, **options):
    """
    Create a new sub account

    :param name:                Name of the new sub accounnt
    :type name:                 str
    :param cloud_name:          A case-insensitive cloud name comprised of alphanumeric and underscore characters.
                                * Generates an error if the cloud name is not unique across all Cloudinary accounts.
    :type cloud_name:           str, optional
    :param custom_attributes:   Any custom attributes you want to associate with the sub-account
    :type custom_attributes:    dict, optional
    :param enabled:             Whether to create the account as enabled (default is enabled).
    :type enabled:              bool, optional
    :param base_account:        ID of sub-account from which to copy settings
    :type base_account:         str, optional
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    The created sub account
    :rtype:                     dict
    """
    uri = [SUB_ACCOUNTS_SUB_PATH]
    return _call_provisioning_api("post", uri,
                                  params=dict(
                                      name=name,
                                      cloud_name=cloud_name,
                                      custom_attributes=custom_attributes,
                                      enabled=enabled,
                                      base_account=base_account,
                                  ),
                                  **options)


def delete_sub_account(sub_account_id, **options):
    """
    Delete a sub account

    :param sub_account_id:      The id of the sub account
    :type sub_account_id:       str
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    Result message
    :rtype:                     dict
    """
    uri = [SUB_ACCOUNTS_SUB_PATH, sub_account_id]
    return _call_provisioning_api("delete", uri, {}, **options)


def sub_account(sub_account_id, **options):
    """
    Get information of a sub account

    :param sub_account_id:      The id of the sub account
    :type sub_account_id:       str
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    A sub account
    :rtype:                     dict
    """
    uri = [SUB_ACCOUNTS_SUB_PATH, sub_account_id]
    return _call_provisioning_api("get", uri, {}, **options)


def update_sub_account(sub_account_id, cloud_name=None, custom_attributes=None,
                       enabled=None, base_account=None,
                       **options):
    """
    Update a sub account

    :param sub_account_id:      The id of the sub account
    :type sub_account_id:       str
    :param cloud_name:          Unique cloud name
    :type cloud_name:           str, optional
    :param custom_attributes:   Any custom attributes you want to associate with the sub-account.
    :type custom_attributes:    dict, optional
    :param enabled:             Whether to create the account as enabled (default is enabled).
    :type enabled:              bool, optional
    :param base_account:        ID of sub-account from which to copy settings
    :type base_account:         str, optional
    :param options:             Generic advanced options dict, see online documentation
    :type options:              dict, optional
    :return:                    Updated sub account
    :rtype:                     dict
    """
    uri = [SUB_ACCOUNTS_SUB_PATH, sub_account_id]
    return _call_provisioning_api("put", uri,
                                  params=dict(
                                      cloud_name=cloud_name,
                                      custom_attributes=custom_attributes,
                                      enabled=enabled,
                                      base_account=base_account
                                  ),
                                  **options)
