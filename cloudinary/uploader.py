# Copyright Cloudinary
import json
import re
import sys
import urllib
from os.path import basename

import cloudinary
from cloudinary import utils
from cloudinary.api import Error
from cloudinary.compat import (urllib2, StringIO, string_types, urlencode,
    to_bytes, to_string)
from cloudinary.poster.encode import multipart_encode
from cloudinary.poster.streaminghttp import register_openers

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
              "unique_filename": options.get("unique_filename"),
              "discard_original_filename": options.get("discard_original_filename"),
              "invalidate": options.get("invalidate"),
              "notification_url": options.get("notification_url"),
              "eager_notification_url": options.get("eager_notification_url"),
              "eager_async": options.get("eager_async"),
              "proxy": options.get("proxy"),
              "folder": options.get("folder"),
              "overwrite": options.get("overwrite"),
              "tags": options.get("tags") and ",".join(utils.build_array(options["tags"])),
              "allowed_formats": options.get("allowed_formats") and ",".join(utils.build_array(options["allowed_formats"])),
              "face_coordinates": utils.encode_double_array(options.get("face_coordinates")),
              "context": utils.encode_dict(options.get("context")),
              "moderation": options.get("moderation"),
              "raw_convert": options.get("raw_convert"),
              "ocr": options.get("ocr"),
              "categorization": options.get("categorization"),
              "detection": options.get("detection"),
              "similarity_search": options.get("similarity_search"),
              "auto_tagging": options.get("auto_tagging") and float(options.get("auto_tagging"))}
    params = dict( [ (k, __safe_value(v)) for (k,v) in params.items()] )
    return params

def __safe_value(v):
    if isinstance(v, (bool)):
        if v:
            return "1"
        else:
            return "0"
    else:
        return v

def upload(file, **options):
    params = build_upload_params(**options)
    return call_api("upload", params, file = file, **options)

def upload_image(file, **options):
    result = upload(file, **options)
    return cloudinary.CloudinaryImage(result["public_id"], version=str(result["version"]),
        format=result["format"], metadata=result)

def upload_large(file, **options):
    """ Upload large raw files. Note that public_id should include an extension for best results. """
    with open(file, 'rb') as file_io:
        upload = upload_id = None
        index = 1
        public_id = options.get("public_id")
        chunk = file_io.read(20000000)
        while (chunk):
            chunk_io = StringIO.StringIO(chunk)
            chunk_io.name = basename(file)
            chunk = file_io.read(20000000)
            upload = upload_large_part(chunk_io, public_id=public_id,
                            upload_id=upload_id, part_number=index, final=chunk != "", **options)
            upload_id = upload.get("upload_id")
            public_id = upload.get("public_id")
            index += 1
        return upload

def upload_large_part(file, **options):
    """ Upload large raw files. Note that public_id should include an extension for best results. """
    params = {
        "timestamp": utils.now(),
        "type": options.get("type"),
        "backup": options.get("backup"),
        "final": options.get("final"),
        "part_number": options.get("part_number"),
        "upload_id": options.get("upload_id"),
        "public_id": options.get("public_id")
    }
    return call_api("upload_large", params, resource_type="raw", file=file, **options)


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
        "tags": options.get("tags") and ",".join(utils.build_array(options["tags"])),
        "face_coordinates": utils.encode_double_array(options.get("face_coordinates"))}
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

    datagen = to_bytes('')
    headers = {}
    if "file" in options:
        file = options["file"]
        if not isinstance(file, string_types):
            datagen, headers = multipart_encode({'file': file})
        elif not re.match(r'^https?:|^s3:|^data:[^;]*;base64,([a-zA-Z0-9\/+\n=]+)$', file):
            datagen, headers = multipart_encode({'file': open(file, "rb")})
        else:
            param_list.append(("file", file))
    url = api_url + '?' + urlencode(param_list)
    request = urllib2.Request(url, datagen, headers)
    request.add_header("User-Agent", cloudinary.USER_AGENT)

    code = 200
    try:
        response = urllib2.urlopen(request).read()
    except urllib2.HTTPError:
        e = sys.exc_info()[1]
        if not e.code in [200, 400, 500]:
            raise Error("Server returned unexpected status code - %d - %s" % (e.code, e.read()))
        code = e.code
        response = e.read()

    try:
        result = json.loads(to_string(response))
    except Exception:
        e = sys.exc_info()[1]
        # Error is parsing json
        raise Error("Error parsing server response (%d) - %s. Got - %s", code, response, e)

    if "error" in result:
        if return_error:
            result["error"]["http_code"] = response.code
        else:
            raise Error(result["error"]["message"])

    return result


