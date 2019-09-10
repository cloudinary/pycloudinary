from .api import call_api
from cloudinary.api import only as _only

ROLES = [
    "master_admin", "admin", "billing", "technical_admin", "reports", "media_library_admin", "media_library_user"
]


def users(**options):
    uri = ['users']
    return call_api("get", uri, _only(options, "user_ids", "sub_account_id", "pending", "prefix"), **options)


def create_user(name, email, role, sub_account_ids, **options):
    uri = ['users']
    return call_api("post", uri, dict(name=name, email=email, role=role, sub_account_ids=sub_account_ids), **options)


def delete_user(user_id, **options):
    uri = ['users', user_id]
    return call_api("delete", uri, {}, **options)


def user(user_id, **options):
    uri = ['users', user_id]
    return call_api("get", uri, {}, **options)


def update_user(user_id, **options):
    uri = ['users', user_id]
    return call_api("put", uri, _only(options, "name", "email", "role", "sub_account_ids", "enabled"), **options)
