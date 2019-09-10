from .api import call_api
from cloudinary.api import only as _only


def sub_accounts(**options):
    uri = ['sub_accounts']
    return call_api("get", uri, _only(options, "ids", "enabled", "prefix"), **options)


def create_sub_account(name, **options):
    uri = ['sub_accounts']
    return call_api("post", uri, dict(name=name,
                                      **_only(options, "cloud_name", "base_sub_account_id", "description")), **options)


def delete_sub_account(sub_account_id, **options):
    uri = ['sub_accounts', sub_account_id]
    return call_api("delete", uri, {}, **options)


def sub_account(sub_account_id, **options):
    uri = ['sub_accounts', sub_account_id]
    return call_api("get", uri, {}, **options)


def update_sub_account(sub_account_id, **options):
    uri = ['sub_accounts', sub_account_id]
    return call_api("put", uri,
                    _only(options, "cloud_name", "description", "base_sub_account_id", "enabled"), **options)
