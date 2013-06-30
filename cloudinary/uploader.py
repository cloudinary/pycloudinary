# Copyright Cloudinary
import cloudinary
from cloudinary import utils
import json
import re
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib
import urllib2

_initialized = False

def build_eager(transformations):
    eager = []
    for tr in utils.build_array(transformations):
        format = tr.get("format")
        single_eager = "/".join([x for x in [utils.generate_transformation_string(**tr)[0], format] if x])
        eager.append(single_eager)
    return "|".join(eager)

def build_custom_headers(headers):
    if headers == None:
        return None
    elif isinstance(headers, list):
        pass
    elif isinstance(headers, dict):
        headers = [k + ": " + v for k, v in headers.items()]
    else:
        return headers
    return "\n".join(headers)

def build_upload_params(**options):
    params = {"timestamp": utils.now(),
              "transformation": utils.generate_transformation_string(**options)[0],
              "public_id": options.get("public_id"),
              "callback": options.get("callback"),
              "format": options.get("format"),
              "type": options.get("type"),
              "backup": options.get("backup"),
              "faces": options.get("faces"),
              "image_metadata": options.get("image_metadata"),
              "exif": options.get("exif"),
              "colors": options.get("colors"),
              "headers": build_custom_headers(options.get("headers")),
              "eager": build_eager(options.get("eager")),
              "use_filename": options.get("use_filename"),
              "discard_original_filename": options.get("discard_original_filename"),
              "invalidate": options.get("invalidate"),
              "notification_url": options.get("notification_url"),
              "eager_notification_url": options.get("eager_notification_url"),
              "eager_async": options.get("eager_async"),
              "tags": options.get("tags") and ",".join(utils.build_array(options["tags"]))}
    return params

def upload(file, **options):
    params = build_upload_params(**options)
    return call_api("upload", params, file = file, **options)

def upload_image(file, **options):
    result = upload(file, **options)
    return cloudinary.CloudinaryImage(result["public_id"], version=str(result["version"]),
        format=result["format"], metadata=result)

def destroy(public_id, **options):
    params = {
        "timestamp": utils.now(),
        "type": options.get("type"),
        "invalidate": options.get("invalidate"),
        "public_id":    public_id
    }
    return call_api("destroy", params, **options)

def rename(from_public_id, to_public_id, **options):
    params = {
        "timestamp": utils.now(),
        "type": options.get("type"),
        "overwrite": options.get("overwrite"),
        "from_public_id": from_public_id,
        "to_public_id": to_public_id
    }
    return call_api("rename", params, **options)

def explicit(public_id, **options):
     params = {
        "timestamp": utils.now(),
        "type": options.get("type"),
        "public_id": public_id,
        "callback": options.get("callback"),
        "headers": build_custom_headers(options.get("headers")),
        "eager": build_eager(options.get("eager")),
        "tags": options.get("tags") and ",".join(utils.build_array(options["tags"]))}
     return call_api("explicit", params, **options)

def generate_sprite(tag, **options):
     params = {
        "timestamp": utils.now(),
        "tag": tag,
        "async": options.get("async"),
        "notification_url": options.get("notification_url"),
        "transformation": utils.generate_transformation_string(fetch_format=options.get("format"), **options)[0]
        }
     return call_api("sprite", params, **options)

def multi(tag, **options):
     params = {
        "timestamp": utils.now(),
        "tag": tag,
        "format": options.get("format"),
        "async": options.get("async"),
        "notification_url": options.get("notification_url"),
        "transformation": utils.generate_transformation_string(**options)[0]
        }
     return call_api("multi", params, **options)

def explode(public_id, **options):
     params = {
        "timestamp": utils.now(),
        "public_id": public_id,
        "format": options.get("format"),
        "notification_url": options.get("notification_url"),
        "transformation": utils.generate_transformation_string(**options)[0]
        }
     return call_api("explode", params, **options)

# options may include 'exclusive' (boolean) which causes clearing this tag from all other resources
def add_tag(tag, public_ids = [], **options):
    exclusive = options.pop("exclusive", None)
    command = "set_exclusive" if exclusive else "add"
    return call_tags_api(tag, command, public_ids, **options)

def remove_tag(tag, public_ids = [], **options):
    return call_tags_api(tag, "remove", public_ids, **options)

def replace_tag(tag, public_ids = [], **options):
    return call_tags_api(tag, "replace", public_ids, **options)

def call_tags_api(tag, command, public_ids = [], **options):
    params = {
        "timestamp": utils.now(),
        "tag": tag,
        "public_ids": utils.build_array(public_ids),
        "command": command,
        "type": options.get("type")
    }
    return call_api("tags", params, **options)

TEXT_PARAMS = ["public_id", "font_family", "font_size", "font_color", "text_align", "font_weight", "font_style", "background", "opacity", "text_decoration"]
def text(text, **options):
    params = {"timestamp": utils.now(), "text": text}
    for key in TEXT_PARAMS:
        params[key] = options.get(key)
    return call_api("text", params, **options)

def call_api(action, params, **options):
    return_error = options.get("return_error")
    params = utils.sign_request(params, options)

    param_list = []
    for k, v in params.items():
        if isinstance(v, list):          
            for vv in v:
              param_list.append((k+"[]", vv))
        elif v:
            param_list.append((k, v))            

    api_url = utils.cloudinary_api_url(action, **options)

    global _initialized
    if not _initialized:
        _initialized = True
        # Register the streaming http handlers with urllib2
        register_openers()

    datagen = ""
    headers = {}
    if "file" in options:
        file = options["file"]
        if not isinstance(file, basestring):
            datagen, headers = multipart_encode({'file': file})
        elif not re.match(r'^https?:|^s3:|^data:image\/\w*;base64,([a-zA-Z0-9\/+\n=]+)$', file):
            datagen, headers = multipart_encode({'file': open(file, "rb")})
        else:
            param_list.append(("file", file))
    request = urllib2.Request(api_url + "?" + urllib.urlencode(param_list), datagen, headers)

    code = 200
    try:
        response = urllib2.urlopen(request).read()
    except urllib2.HTTPError, e:
        if not e.code in [200, 400, 500]:
            raise Exception("Server returned unexpected status code - %d - %s" % (e.code, e.read()))
        code = e.code
        response = e.read()

    try:
        result = json.loads(response)
    except Exception, e:
        # Error is parsing json
        raise Exception("Error parsing server response (%d) - %s. Got - %s", code, response, e)

    if "error" in result:
        if return_error:
            result["error"]["http_code"] = response.code
        else:
            raise Exception(result["error"]["message"])

    return result


