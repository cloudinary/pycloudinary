# Copyright Cloudinary
import time
import cloudinary
from cloudinary import utils
import json
import re
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib
import urllib2

_initialized = False

def now():
  return str(int(time.time()))

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
  params = {"timestamp": now(),
            "transformation" :  utils.generate_transformation_string(**options)[0],
            "public_id":  options.get("public_id"),
            "callback":  options.get("callback"),
            "format": options.get("format"),
            "type": options.get("type"),
            "backup": options.get("backup"),
            "headers": build_custom_headers(options.get("headers")),
            "eager": build_eager(options.get("eager")),
            "tags": options.get("tags") and ",".join(utils.build_array(options["tags"]))}    
  return params    
 
def upload(file, **options):
  params = build_upload_params(**options)
  return call_api("upload", params, file = file, **options)

def destroy(public_id, **options):
  params = {
    "timestamp": now(),
    "type": options.get("type"),
    "public_id":  public_id
  }
  return call_api("destroy", params, **options)

def explicit(public_id, **options):
   params = {
    "timestamp": now(),
    "type": options.get("type"),
    "public_id": public_id,
    "callback": options.get("callback"),
    "headers": build_custom_headers(options.get("headers")),
    "eager": build_eager(options.get("eager")),
    "tags": options.get("tags") and ",".join(utils.build_array(options["tags"]))}
   return call_api("explicit", params, **options)
  
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
    "timestamp": now(),
    "tag": tag,
    "public_ids":  utils.build_array(public_ids),
    "command":  command,
    "type": options.get("type")
  }
  return call_api("tags", params, **options)

TEXT_PARAMS = ["public_id", "font_family", "font_size", "font_color", "text_align", "font_weight", "font_style", "background", "opacity", "text_decoration"]  
def text(text, **options):
  params = {"timestamp": now(), "text": text}
  for key in TEXT_PARAMS:
    params[key] = options.get(key)
  return call_api("text", params, **options)

def call_api(action, params, **options):
  return_error = options.get("return_error")
  api_key = options.get("api_key", cloudinary.config().api_key)
  if not api_key: raise Exception("Must supply api_key")
  api_secret = options.get("api_secret", cloudinary.config().api_secret)
  if not api_secret: raise Exception("Must supply api_secret")

  params["signature"] = utils.api_sign_request(params, api_secret)
  params["api_key"] = api_key

  # Remove blank parameters
  for k, v in params.items():
    if not v:
      del params[k]

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
    if not isinstance(file, str):
      datagen, headers = multipart_encode({'file': file})
    elif not re.match(r'^https?:', file):
      datagen, headers = multipart_encode({'file': open(file)})
    else:
      params["file"] = file
  request = urllib2.Request(api_url + "?" + urllib.urlencode(params), datagen, headers)
    
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

