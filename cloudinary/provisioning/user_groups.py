from .api import call_api
from cloudinary.api import only as _only


def user_groups(**options):
    uri = ['user_groups']
    return call_api("get", uri, {}, **options)


def create_user_group(name, **options):
    uri = ['user_groups']
    return call_api("post", uri, dict(name=name), **options)


def update_user_group(user_group_id, **options):
    uri = ['user_groups', user_group_id]
    return call_api("put", uri, _only(options, "name"), **options)


def delete_user_group(user_group_id, **options):
    uri = ['user_groups', user_group_id]
    return call_api("delete", uri, {}, **options)


def user_group(user_group_id, **options):
    uri = ['user_groups', user_group_id]
    return call_api("get", uri, {}, **options)


def add_user_to_user_group(user_group_id, user_id, **options):
    uri = ['user_groups', user_group_id, 'users', user_id]
    return call_api("post", uri, {}, **options)


def remove_user_from_user_group(user_group_id, user_id, **options):
    uri = ['user_groups', user_group_id, 'users', user_id]
    return call_api("delete", uri, {}, **options)


def users_in_user_group(user_group_id, **options):
    uri = ['user_groups', user_group_id, 'users']
    return call_api("get", uri, {}, **options)


def user_in_user_groups(user_id, **options):
    uri = ['users', user_id]
    return call_api("get", uri, {}, **options)
