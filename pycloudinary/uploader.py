# Copyright Cloudinary
import pycurl 
import time
import pycloudinary
from pycloudinary import utils
import json
import re
import StringIO

def now():
  return str(int(time.time()))

def build_upload_params(**options):
  params = {"timestamp": now(),
            "transformation" :  utils.generate_transformation_string(**options)[0],
            "public_id":  options.get("public_id"),
            "callback":  options.get("callback"),
            "format": options.get("format"),
            "type": options.get("type"),
            "tags": options.get("tags") and ",".join(utils.build_array(options["tags"]))}    
  if "eager" in options:
    params["eager"] = "|".join([utils.generate_transformation_string(**tr)[0] for tr in utils.build_array(options["eager"]) if tr])
  return params    
 
def upload(file, **options):
  params = build_upload_params(**options)
  if re.match(r"^https?:", file):
    params["file"] = file
  else:
    params["file"] = (pycurl.FORM_FILE, file)
  return call_api("upload", params, non_signable = ["file"], **options)

def destroy(public_id, **options):
  params = {
    "timestamp": now(),
    "type": options.get("type"),
    "public_id":  public_id
  }
  return call_api("destroy", params, **options)
  
# options may include 'exclusive' (boolean) which causes clearing this tag from all other resources 
def add_tag(tag, public_ids = [], **options):
  exclusive = options.pop("exclusive", None)
  command = "set_exclusive" if exclusive else "add"
  return call_tags_api(tag, command, public_ids, **options)    

def remove_tag(tag, public_ids = [], **options):
  return self.call_tags_api(tag, "remove", public_ids, **options)

def replace_tag(tag, public_ids = [], **options):
  return self.call_tags_api(tag, "replace", public_ids, **options)    

def call_tags_api(tag, command, public_ids = [], **options):
  params = {
    "timestamp": int(time.time()),
    "tag": tag,
    "public_ids":  utils.build_array(public_ids),
    "command":  command
  }
  return call_api("tags", params, **options)

def call_api(action, params, **options):
  return_error = options.get("return_error")
  api_key = options.get("api_key", pycloudinary.config().api_key)
  if not api_key: raise Exception("Must supply api_key")
  api_secret = options.get("api_secret", pycloudinary.config().api_secret)
  if not api_secret: raise Exception("Must supply api_secret")

  non_signable = options.get("non_signable", [])
  
  signable_params = dict([(k,v) for k,v in params.items() if k not in non_signable])
  params["signature"] = utils.api_sign_request(signable_params, api_secret)
  params["api_key"] = api_key

  api_url = utils.cloudinary_api_url(action, **options)
 
  c = pycurl.Curl()
  c.setopt(c.URL, api_url)
  c.setopt(c.POST, 1)
  c.setopt(c.HTTPPOST, [(k,v) for k, v in params.items() if v])
  b = StringIO.StringIO()
  c.setopt(pycurl.WRITEFUNCTION, b.write)
  c.perform()
  response = b.getvalue()
  code = c.getinfo(pycurl.HTTP_CODE)
  c.close()
  if not code in [200, 400, 500]:
    raise Exception("Server returned unexpected status code - %d - %s" % (code, response))
  try:
    result = json.loads(response) 
  except exception as e:
    # Error is parsing json
    raise Exception("Error parsing server response (%d) - %s. Got - %s", code, response, e)

  if "error" in result:
    if return_error:
      result["error"]["http_code"] = response.code
    else:
      raise Exception(result["error"]["message"])
  
  return result    

