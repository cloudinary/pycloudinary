# Copyright Cloudinary
import base64
import hashlib
import re
import struct
import time
import uuid
import zlib

import cloudinary
from cloudinary.compat import (PY3, to_bytes, to_bytearray, to_string,
    unquote, urlencode)

""" @deprecated: use cloudinary.SHARED_CDN """
SHARED_CDN = cloudinary.SHARED_CDN

def build_array(arg):
    if isinstance(arg, list):
        return arg
    elif arg == None:
        return []
    else:
        return [arg]

def encode_double_array(arg):
    return "|".join([",".join([str(i) for i in build_array(inner)]) for inner in build_array(arg)])

def encode_dict(arg):
    if isinstance(arg, dict):
        return "|".join((k + "=" + v) for k, v in arg.iteritems())
    else:
        return arg

def generate_transformation_string(**options):
    size = options.pop("size", None)
    if size:
        options["width"], options["height"] = size.split("x")
    width = options.get("width")
    height = options.get("height")
    has_layer = ("underlay" in options) or ("overlay" in options)

    crop = options.pop("crop", None)
    angle = ".".join([str(value) for value in build_array(options.pop("angle", None))])
    no_html_sizes = has_layer or angle or crop == "fit" or crop == "limit"

    if width and (float(width) < 1 or no_html_sizes):
        del options["width"]
    if height and (float(height) < 1 or no_html_sizes):
        del options["height"]

    background = options.pop("background", None)
    if background:
        background = background.replace("#", "rgb:")
    color = options.pop("color", None)
    if color:
        color = color.replace("#", "rgb:")

    base_transformations = build_array(options.pop("transformation", None))
    if any(isinstance(bs, dict) for bs in base_transformations):
        recurse = lambda bs: generate_transformation_string(**bs)[0] if isinstance(bs, dict) else generate_transformation_string(transformation=bs)[0]
        base_transformations = list(map(recurse, base_transformations))
        named_transformation = None
    else:
        named_transformation = ".".join(base_transformations)
        base_transformations = []

    effect = options.pop("effect", None)
    if isinstance(effect, list):
        effect = ":".join([str(x) for x in effect])
    elif isinstance(effect, dict):
        effect = ":".join([str(x) for x in list(effect.items())[0]])

    border = options.pop("border", None)
    if isinstance(border, dict):
        border = "%(width)spx_solid_%(color)s" % {"color": border.get("color", "black").replace("#", "rgb:"), "width": str(border.get("width", 2))}

    flags = ".".join(build_array(options.pop("flags", None)))

    params = {"w": width, "h": height, "t": named_transformation, "b": background, "co": color, "e": effect, "c": crop, "a": angle, "bo": border, "fl": flags}
    for param, option in {"q": "quality", "g": "gravity", "p": "prefix", "x": "x",
                          "y": "y", "r": "radius", "d": "default_image", "l": "overlay", "u": "underlay", "o": "opacity",
                          "f": "fetch_format", "pg": "page", "dn": "density", "dl": "delay", "cs": "color_space"}.items():
        params[param] = options.pop(option, None)

    transformations = [param + "_" + str(value) for param, value in params.items() if (value or value == 0)]
    transformations.sort()
    transformation = ",".join(transformations)
    if "raw_transformation" in options:
        transformation = transformation + "," + options.pop("raw_transformation")
    all_transformations = base_transformations + [transformation]
    url = "/".join([trans for trans in all_transformations if trans])
    return (url, options)

def sign_request(params, options):
    api_key = options.get("api_key", cloudinary.config().api_key)
    if not api_key: raise Exception("Must supply api_key")
    api_secret = options.get("api_secret", cloudinary.config().api_secret)
    if not api_secret: raise Exception("Must supply api_secret")

    params = dict( [ (k,v) for (k,v) in params.items() if v] )
    params["signature"] = api_sign_request(params, api_secret)
    params["api_key"] = api_key

    return params

def api_sign_request(params_to_sign, api_secret):
    to_sign = "&".join(sorted([(k+"="+(",".join(v) if isinstance(v, list) else str(v))) for k, v in params_to_sign.items() if v]))
    value = to_bytes(to_sign + api_secret)
    return hashlib.sha1(value).hexdigest()

def cloudinary_url(source, **options):
    original_source = source

    type = options.pop("type", "upload")
    if type == 'fetch':
        options["fetch_format"] = options.get("fetch_format", options.pop("format", None))
    transformation, options = generate_transformation_string(**options)

    resource_type = options.pop("resource_type", "image")
    version = options.pop("version", None)
    format = options.pop("format", None)
    cdn_subdomain = options.pop("cdn_subdomain", cloudinary.config().cdn_subdomain)
    cname = options.pop("cname", cloudinary.config().cname)
    shorten = options.pop("shorten", cloudinary.config().shorten)

    cloud_name = options.pop("cloud_name", cloudinary.config().cloud_name or None)
    if cloud_name == None:
        raise Exception("Must supply cloud_name in tag or in configuration")
    secure = options.pop("secure", cloudinary.config().secure)
    private_cdn = options.pop("private_cdn", cloudinary.config().private_cdn)
    secure_distribution = options.pop("secure_distribution", cloudinary.config().secure_distribution)
    sign_url = options.pop("sign_url", cloudinary.config().sign_url)
    api_secret = options.pop("api_secret", cloudinary.config().api_secret)

    if (not source) or ((type == "upload" or type=="asset") and re.match(r'^https?:', source)):
        return (original_source, options)
    if re.match(r'^https?:', source):
        source = smart_escape(source)
    else:
        source = smart_escape(unquote(source))
        if format:
          source = source + "." + format

    if cloud_name.startswith("/"):
        prefix = "/res" + cloud_name
    else:
        shared_domain = not private_cdn
        if secure:
            if not secure_distribution or secure_distribution == cloudinary.OLD_AKAMAI_SHARED_CDN:
              secure_distribution = cloud_name + "-res.cloudinary.com" if private_cdn else cloudinary.SHARED_CDN
            shared_domain = shared_domain or secure_distribution == cloudinary.SHARED_CDN
            prefix = "https://" + secure_distribution
        else:
            subdomain = "a" + str((zlib.crc32(to_bytearray(source)) & 0xffffffff)%5 + 1) + "." if cdn_subdomain else ""
            if cname:
                host = cname
            elif private_cdn:
                host = cloud_name + "-res.cloudinary.com"
            else:
                host = "res.cloudinary.com"
            prefix = "http://" + subdomain + host
        if shared_domain:
            prefix += "/" + cloud_name

    if shorten and resource_type == "image" and type == "upload":
        resource_type = "iu"
        type = ""

    if source.find("/") >= 0 and not re.match(r'^https?:/', source) and not re.match(r'^v[0-9]+', source) and not version:
        version = "1"

    rest = "/".join(filter(lambda x: x, [transformation, "v" + str(version) if version else "", source]))

    if sign_url:
        value = to_bytes(rest + api_secret)
        signature = base64.urlsafe_b64encode(hashlib.sha1(value).digest())[0:8]
        signature = to_string(signature)
        rest = "s--%(signature)s--/%(rest)s" % {"signature": signature, "rest": rest}

    components = [prefix, resource_type, type, rest]
    source = re.sub(r'([^:])/+', r'\1/', "/".join(components))

    return (source, options)

def cloudinary_api_url(action = 'upload', **options):
    cloudinary_prefix = options.get("upload_prefix", cloudinary.config().upload_prefix) or "https://api.cloudinary.com"
    cloud_name = options.get("cloud_name", cloudinary.config().cloud_name)
    if not cloud_name: raise Exception("Must supply cloud_name")
    resource_type = options.get("resource_type", "image")
    return "/".join([cloudinary_prefix, "v1_1", cloud_name, resource_type, action])

# Based on ruby's CGI::unescape. In addition does not escape / :
def smart_escape(string):
    string = to_bytearray(string)
    pack = lambda m: to_bytes('%' + "%".join(["%02X" % x for x in struct.unpack('B'*len(m.group(1)), m.group(1))]).upper())
    pattern = to_bytes(r'([^a-zA-Z0-9_.\-\/:]+)')
    return to_string(re.sub(pattern, pack, string))

def random_public_id():
    return base64.urlsafe_b64encode(hashlib.sha1(uuid.uuid4()).digest())[0:16]

def signed_preloaded_image(result):
    filename = ".".join([x for x in [result["public_id"], result["format"]] if x])
    path = "/".join([result["resource_type"], "upload", "v" + result["version"], filename])
    return path + "#" + result["signature"]

def now():
  return str(int(time.time()))

def private_download_url(public_id, format, **options):
  cloudinary_params = sign_request({
    "timestamp": now(),
    "public_id": public_id,
    "format": format,
    "type": options.get("type"),
    "attachment": options.get("attachment"),
    "expires_at": options.get("expires_at")
  }, options)

  return cloudinary_api_url("download", **options) + "?" + urlencode(cloudinary_params)

def zip_download_url(tag, **options):
  cloudinary_params = sign_request({
    "timestamp": now(),
    "tag": tag,
    "transformation": generate_transformation_string(**options)[0]
  }, options)

  return cloudinary_api_url("download_tag.zip", **options) + "?" + urlencode(cloudinary_params)
