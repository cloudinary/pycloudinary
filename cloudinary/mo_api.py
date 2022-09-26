from cloudinary.api_client.call_api import call_json_api, call_api


def ping(**options):
    options["is_mo"] = True
    return call_api("get", ["ping"], {}, **options)


def invalidate(*urls, **options):
    options["is_mo"] = True
    return call_json_api("post", ["invalidate"], {"urls": list(urls)}, **options)


def warm_up(url, **options):
    options["is_mo"] = True
    return call_json_api("post", ["cache_warm_up"], {"url": url}, **options)
