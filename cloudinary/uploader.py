# Copyright Cloudinary
import json, re, sys
from os.path import basename, getsize
import urllib
import cloudinary
import socket
from cloudinary import utils
from cloudinary.api import Error
from cloudinary.poster.encode import multipart_encode
from cloudinary.poster.streaminghttp import register_openers
from cloudinary.compat import urllib2, BytesIO, string_types, urlencode, to_bytes, to_string, PY3, HTTPError
_initialized = False

def upload(file, **options):
    params = utils.build_upload_params(**options)
    return call_api("upload", params, file = file, **options)

def unsigned_upload(file, upload_preset, **options):
    return upload(file, upload_preset=upload_preset, unsigned=True, **options)

def upload_image(file, **options):
    result = upload(file, **options)
    return cloudinary.CloudinaryImage(result["public_id"], version=str(result["version"]),
        format=result.get("format"), metadata=result)

def upload_resource(file, **options):
    result = upload(file, **options)
    return cloudinary.CloudinaryResource(result["public_id"], version=str(result["version"]),
        format=result.get("format"), type=result["type"], resource_type=result["resource_type"], metadata=result)

def upload_large(file, **options):
    """ Upload large files. """
    upload_id = utils.random_public_id()
    with open(file, 'rb') as file_io:
        upload = None
        current_loc = 0
        chunk_size = options.get("chunk_size", 20000000)
        file_size = getsize(file)
        chunk = file_io.read(chunk_size)        
        while (chunk):
            chunk_io = BytesIO(chunk)
            chunk_io.name = basename(file)
            range = "bytes {0}-{1}/{2}".format(current_loc, current_loc + len(chunk) - 1, file_size)
            current_loc += len(chunk)
            upload = upload_large_part(chunk_io, http_headers={"Content-Range": range, "X-Unique-Upload-Id": upload_id}, **options)
            options["public_id"] = upload.get("public_id")
            chunk = file_io.read(chunk_size)
        return upload

def upload_large_part(file, **options):
    """ Upload large files. """
    params = utils.build_upload_params(**options)
    if 'resource_type' not in options: options['resource_type'] = "raw"
    return call_api("upload", params, file=file, **options)

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
        "invalidate": options.get("invalidate"),
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
        "headers": utils.build_custom_headers(options.get("headers")),
        "eager": utils.build_eager(options.get("eager")),
        "eager_notification_url": options.get("eager_notification_url"),
        "eager_async": options.get("eager_async"),
        "tags": options.get("tags") and ",".join(utils.build_array(options["tags"])),
        "face_coordinates": utils.encode_double_array(options.get("face_coordinates")),
        "custom_coordinates": utils.encode_double_array(options.get("custom_coordinates")),
        "invalidate": options.get("invalidate"),
        "context": utils.encode_dict(options.get("context")),
        "responsive_breakpoints": utils.generate_responsive_breakpoints_string(options.get("responsive_breakpoints"))}
     return call_api("explicit", params, **options)

def create_archive(**options):
    params = utils.archive_params(**options)
    if options.get("target_format") is not None:
        params["target_format"] = options.get("target_format")
    return call_api("generate_archive", params, **options)

def create_zip(**options):
    return create_archive(target_format="zip", **options)

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

def call_api(action, params, http_headers={}, return_error=False, unsigned=False, file=None, timeout=None, **options):
    try:
        file_io = None
        if unsigned:
          params = utils.cleanup_params(params)
        else:
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
    
        if file:
            if not isinstance(file, string_types):
                param_list.append(("file", file))
            elif not re.match(r'ftp:|https?:|s3:|data:[^;]*;base64,([a-zA-Z0-9\/+\n=]+)$', file):
                file_io = open(file, "rb")
                param_list.append(('file', file_io))
            else:
                param_list.append(("file", file))

        datagen, headers = multipart_encode(param_list)
        
        if _is_gae():
            # Might not be needed in the future but for now this is needed in GAE
            datagen = "".join(datagen)

        request = urllib2.Request(api_url, datagen, headers)
        request.add_header("User-Agent", cloudinary.get_user_agent())
        for k, v in http_headers.items():
            request.add_header(k, v)
    
        kw = {}
        if timeout is not None:
            kw['timeout'] = timeout

        code = 200
        try:
            response = urllib2.urlopen(request, **kw).read()
        except HTTPError:
            e = sys.exc_info()[1]
            if not e.code in [200, 400, 500]:
                raise Error("Server returned unexpected status code - %d - %s" % (e.code, e.read()))
            code = e.code
            response = e.read()
        except urllib2.URLError:
            e = sys.exc_info()[1]
            raise Error("Error - %s" % str(e))
        except socket.error:
            e = sys.exc_info()[1]
            raise Error("Socket error: %s" % str(e))
    
        try:
            result = json.loads(to_string(response))
        except Exception:
            e = sys.exc_info()[1]
            # Error is parsing json
            raise Error("Error parsing server response (%d) - %s. Got - %s", code, response, e)
    
        if "error" in result:
            if return_error:
                result["error"]["http_code"] = code
            else:
                raise Error(result["error"]["message"])
    
        return result
    finally:
        if file_io: file_io.close()    

def _is_gae():
    if PY3:
        return False
    else:
        import httplib
        return 'appengine' in str(httplib.HTTP)
