# Copyright Cloudinary
import zlib
import hashlib
import re
import struct
import uuid
import base64
import cloudinary

SHARED_CDN = "d3jpl91pxevbkh.cloudfront.net"

def build_array(arg):
  if isinstance(arg, list):
    return arg
  elif arg == None:
    return []
  else:
    return [arg]

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
     
  if not crop and not has_layer:
    width = height = None

  background = options.pop("background", None)
  if background:
    background = background.replace("#", "rgb:")
    
  base_transformations = build_array(options.pop("transformation", None))
  if any(isinstance(bs, dict) for bs in base_transformations):
    recurse = lambda bs: generate_transformation_string(**bs)[0] if isinstance(bs, dict) else generate_transformation_string(transformation=bs)[0]
    base_transformations = map(recurse, base_transformations)
    named_transformation = None
  else:
    named_transformation = ".".join(base_transformations)
    base_transformations = []

  effect = options.pop("effect", None)
  if isinstance(effect, list): 
    effect = ":".join([str(x) for x in effect])
  elif isinstance(effect, dict):
    effect = ":".join([str(x) for x in effect.items()[0]])
    
  border = options.pop("border", None)
  if isinstance(border, dict):
    border = "%(width)spx_solid_%(color)s" % {"color": border.get("color", "black").replace("#", "rgb:"), "width": str(border.get("width", 2))}
    
  params = {"w": width, "h": height, "t": named_transformation, "b": background, "e": effect, "c": crop, "a": angle, "bo": border}
  for param, option in {"q": "quality", "g": "gravity", "p": "prefix", "x": "x",
                        "y": "y", "r": "radius", "d": "default_image", "l": "overlay", "u": "underlay",
                        "f": "fetch_format", "pg": "page", "dn": "density", "dl": "delay", "cs": "color_space"}.items():
    params[param] = options.pop(option, None)

  transformations = [param + "_" + str(value) for param, value in params.items() if value]
  transformations.sort()
  transformation = ",".join(transformations)
  if "raw_transformation" in options:
    transformation = transformation + "," + options.pop("raw_transformation")
  url = "/".join([trans for trans in base_transformations + [transformation] if trans])
  return (url, options)
  
def api_sign_request(params_to_sign, api_secret):
  to_sign = "&".join(sorted([(k+"="+(",".join(v) if isinstance(v, list) else str(v))) for k, v in params_to_sign.items() if v]))
  return hashlib.sha1(to_sign + api_secret).hexdigest()

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
    
  cloud_name = options.pop("cloud_name", cloudinary.config().cloud_name or None)
  if cloud_name == None: 
    raise Exception("Must supply cloud_name in tag or in configuration")
  secure = options.pop("secure", cloudinary.config().secure)
  private_cdn = options.pop("private_cdn", cloudinary.config().private_cdn)
  secure_distribution = options.pop("secure_distribution", cloudinary.config().secure_distribution)
  
  if (not source) or ((type == "upload" or type=="asset") and re.match(r'^https?:', source)):
    return (original_source, options)
  if re.match(r'^https?:', source):
    source = smart_escape(source)
  elif format: 
    source = source + "." + format
  
  if cloud_name.startswith("/"):
    prefix = "/res" + cloud_name
  else:
    if secure and not secure_distribution:
      if private_cdn:
        raise Exception("secure_distribution not defined")
      else:
        secure_distribution = SHARED_CDN 
    
    if secure:
      prefix = "https://" + secure_distribution
    else:
      subdomain = "a" + str((zlib.crc32(source) & 0xffffffff)%5 + 1) + "." if cdn_subdomain else ""
      if cname:
        host = cname
      elif private_cdn:
        host = cloud_name + "-res.cloudinary.com"
      else:
        host = "res.cloudinary.com"    
      prefix = "http://" + subdomain + host
    if not private_cdn:
      prefix += "/" + cloud_name
  
  components = [prefix, resource_type, type, transformation, "v" + str(version) if version else "", source] 
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
  pack = lambda m: '%' + "%".join(["%02X" % x for x in struct.unpack('B'*len(m.group(1)), m.group(1))]).upper()
  return re.sub(r"([^ a-zA-Z0-9_.-\/:]+)", pack, string).replace(' ', '+')
  
def random_public_id():
  return base64.urlsafe_b64encode(hashlib.sha1(uuid.uuid4()).digest())[0:16]

def signed_preloaded_image(result):
  filename = ".".join([x for x in [result["public_id"], result["format"]] if x])
  path = "/".join([result["resource_type"], "upload", "v" + result["version"], filename])
  return path + "#" + result["signature"]
  
