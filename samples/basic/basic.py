import cloudinary
import cloudinary.uploader
from cloudinary.api import delete_resources_by_tag, resources_by_tag
import os, sys

# config
os.chdir(os.path.join(os.path.dirname(sys.argv[0]), '.'))
if os.path.exists('settings.py'):
    execfile('settings.py')

# uploads data
SAMPLE_PATHS = dict(
    pizza = "pizza.jpg",
    lake = "lake.jpg",
    couple = "http://res.cloudinary.com/demo/image/upload/couple.jpg",
)

DEFAULT_OPTIONS = dict(tags = "python_sample_basic")
DEFAULT_THUMBS = dict(width = 200, height = 150)
EAGER_OPTIONS = dict(DEFAULT_THUMBS, crop = "scale")

# <title>, <filepath>, <upload params>, <display params>
UPLOADS = [
    ["unnamed local, crop - fill", SAMPLE_PATHS["pizza"], {}, dict(crop = "fill")],
    ["named local, crop - fit", SAMPLE_PATHS["pizza"], dict(public_id = "named"), dict(crop = "fit")],
    ["local with eager tranformations", SAMPLE_PATHS["lake"], 
        dict(public_id = "eager", eager = EAGER_OPTIONS), EAGER_OPTIONS
    ],

    ["fetch remotely + crop gravity faces", SAMPLE_PATHS["couple"], {}, 
        dict(crop = "thumb", gravity = "faces")],
    ["fetch remotely with effects", SAMPLE_PATHS["couple"], dict(public_id = "transformed",
        width = 500, height = 500, crop = "fit", effect = "saturation:-70"),
        dict(crop = "fill", gravity = "face", radius = 10),
    ],
]

# upload code
""" Uploads specified files and returns responses """
def do_upload(filename, params):
    return cloudinary.uploader.upload(filename, **dict(DEFAULT_OPTIONS.items() + params.items()))

def show_response(title, response, url):
    print "done -- public_id: %(public_id)s (%(format)s) size: %(width)dx%(height)d" % (
        dict(response, title=title))
    print "  " + url

def upload(uploads):
    for index, item in enumerate(uploads):
        title, filename, upload_params, display_params = item
        print "uploading " + title + "..."
        response = do_upload(filename, upload_params)
        url = cloudinary.utils.cloudinary_url(response["public_id"], **dict(
            [("format", response["format"])] + DEFAULT_THUMBS.items() + display_params.items()
        ))[0]
        show_response(title, response, url)

def cleanup():
    tag = DEFAULT_OPTIONS['tags']
    response = resources_by_tag(tag)
    count = len(response.get('resources', []))
    if (count == 0):
        print "No images found"
        return
    print "Deleting %d images..." % (count,)
    delete_resources_by_tag(tag)
    print "Done!"
    pass

if len(sys.argv) > 1:
    if sys.argv[1] == 'upload': upload(UPLOADS)
    if sys.argv[1] == 'cleanup': cleanup()
    if 'test' in sys.argv:
        print os.getcwd(), sys.argv, __package__, __name__

