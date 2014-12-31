# Copyright Cloudinary
import json, re, sys
from os.path import basename
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

def upload_large(file, **options):
    """ Upload large raw files. Note that public_id should include an extension for best results. """
    with open(file, 'rb') as file_io:
        upload = upload_id = None
        index = 1
        public_id = options.get("public_id")
        chunk = file_io.read(20000000)
        while (chunk):
            chunk_io = BytesIO(chunk)
            chunk_io.name = basename(file)
            chunk = file_io.read(20000000)
            upload = upload_large_part(chunk_io, public_id=public_id,
                            upload_id=upload_id, part_number=index, final=chunk == "", **options)
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
        "tags": options.get("tags") and ",".join(utils.build_array(options["tags"])),
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
        "headers": utils.build_custom_headers(options.get("headers")),
        "eager": utils.build_eager(options.get("eager")),
        "tags": options.get("tags") and ",".join(utils.build_array(options["tags"])),
        "face_coordinates": utils.encode_double_array(options.get("face_coordinates")),
        "custom_coordinates": utils.encode_double_array(options.get("custom_coordinates"))}
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
    try:
        file_io = None
        return_error = options.get("return_error")
        if options.get("unsigned"):
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
    
        datagen = []
        headers = {}
        if "file" in options:
            file = options["file"]
            if not isinstance(file, string_types):
                datagen, headers = multipart_encode({'file': file})
            elif not re.match(r'^https?:|^s3:|^data:[^;]*;base64,([a-zA-Z0-9\/+\n=]+)$', file):
                file_io = open(file, "rb")
                datagen, headers = multipart_encode({'file': file_io})
            else:
                param_list.append(("file", file))

        if _is_gae():
            # Might not be needed in the future but for now this is needed in GAE
            datagen = "".join(datagen)

        request = urllib2.Request(api_url + "?" + urlencode(param_list), datagen, headers)
        request.add_header("User-Agent", cloudinary.USER_AGENT)
    
        kw = {}
        if 'timeout' in options:
            kw['timeout'] = options['timeout']

        code = 200
        try:
            response = urllib2.urlopen(request, **kw).read()
        except HTTPError:
            e = sys.exc_info()[1]
            if not e.code in [200, 400, 500]:
                raise Error("Server returned unexpected status code - %d - %s" % (e.code, e.read()))
            code = e.code
            response = e.read()
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
