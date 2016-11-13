#!/usr/bin/env python
import os, sys

from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from cloudinary.api import delete_resources_by_tag, resources_by_tag

# config
os.chdir(os.path.join(os.path.dirname(sys.argv[0]), '.'))
if os.path.exists('settings.py'):
    exec(open('settings.py').read())

DEFAULT_TAG = "python_sample_basic"

def dump_response(response):
    print("Upload response:")
    for key in sorted(response.keys()):
        print("  %s: %s" % (key, response[key]))

def upload_files():
    print("--- Upload a local file")
    response = upload("pizza.jpg", tags = DEFAULT_TAG)
    dump_response(response)
    url, options = cloudinary_url(response['public_id'],
        format = response['format'],
        width = 200,
        height = 150,
        crop = "fill"
    )
    print("Fill 200x150 url: " + url)
    print("")

    print("--- Upload a local file with custom public ID")
    response = upload("pizza.jpg",
        tags = DEFAULT_TAG,
        public_id = "custom_name",
    )
    dump_response(response)
    url, options = cloudinary_url(response['public_id'],
        format = response['format'],
        width = 200,
        height = 150,
        crop = "fit"
    )
    print("Fit into 200x150 url: " + url)
    print("")

    print("--- Upload a local file with eager transformation of scaling to 200x150")
    response = upload("lake.jpg",
        tags = DEFAULT_TAG,
        public_id = "eager_custom_name",
        eager = dict(
            width = 200,
            height = 150,
            crop = "scale"
        ),
    )
    dump_response(response)
    url, options = cloudinary_url(response['public_id'],
        format = response['format'],
        width = 200,
        height = 150,
        crop = "scale",
    )
    print("scaling to 200x150 url: " + url)
    print("")

    print("--- Upload by fetching a remote image")
    response = upload("http://res.cloudinary.com/demo/image/upload/couple.jpg",
        tags = DEFAULT_TAG,
    )
    dump_response(response)
    url, options = cloudinary_url(response['public_id'],
        format = response['format'],
        width = 200,
        height = 150,
        crop = "thumb",
        gravity = "faces",
    )
    print("Face detection based 200x150 thumbnail url: " + url)
    print("")

    print("--- Fetch an uploaded remote image, fitting it into 500x500 and reducing saturation")
    response = upload("http://res.cloudinary.com/demo/image/upload/couple.jpg",
        tags = DEFAULT_TAG,
        width = 500,
        height = 500,
        crop = "fit",
        effect = "saturation:-70",
    )
    dump_response(response)
    url, options = cloudinary_url(response['public_id'],
        format = response['format'],
        width = 200,
        height = 150,
        crop = "fill",
        gravity = "faces",
        radius = 10,
        effect = "sepia",
    )
    print("Fill 200x150, round corners, apply the sepia effect, url: " + url)
    print("")

def cleanup():
    response = resources_by_tag(DEFAULT_TAG)
    resources = response.get('resources', [])
    if not resources:
        print("No images found")
        return
    print("Deleting {0:d} images...".format(len(resources)))
    delete_resources_by_tag(DEFAULT_TAG)
    print("Done!")
    pass

if len(sys.argv) > 1:
    if sys.argv[1] == 'upload': upload_files()
    if sys.argv[1] == 'cleanup': cleanup()
else:
    print("--- Uploading files and then cleaning up")
    print("    you can only one instead by passing 'upload' or 'cleanup' as an argument")
    print("")
    upload_files()
