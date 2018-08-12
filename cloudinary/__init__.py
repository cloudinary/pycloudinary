from __future__ import absolute_import

import logging
import numbers
import os
import re
from math import ceil

from six import python_2_unicode_compatible, string_types

logger = logging.getLogger("Cloudinary")
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

from platform import python_version

from cloudinary import utils
from cloudinary.api import GeneralError
from cloudinary.cache import responsive_breakpoints_cache
from cloudinary.http_client import HttpClient
from cloudinary.compat import urlparse, parse_qs
from cloudinary.search import Search

CF_SHARED_CDN = "d3jpl91pxevbkh.cloudfront.net"
OLD_AKAMAI_SHARED_CDN = "cloudinary-a.akamaihd.net"
AKAMAI_SHARED_CDN = "res.cloudinary.com"
SHARED_CDN = AKAMAI_SHARED_CDN
CL_BLANK = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

VERSION = "1.12.0"

USER_AGENT = "CloudinaryPython/{} (Python {})".format(VERSION, python_version())
""" :const: USER_AGENT """

USER_PLATFORM = ""
"""
Additional information to be passed with the USER_AGENT, e.g. "CloudinaryMagento/1.0.1".
This value is set in platform-specific implementations that use cloudinary_php.

The format of the value should be <ProductName>/Version[ (comment)].
@see http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.43

**Do not set this value in application code!**
"""


def get_user_agent():
    """Provides the `USER_AGENT` string that is passed to the Cloudinary servers.
    Prepends  `USER_PLATFORM` if it is defined.

    :returns: the user agent
    :rtype: str
    """

    if USER_PLATFORM == "":
        return USER_AGENT
    else:
        return USER_PLATFORM + " " + USER_AGENT


def import_django_settings():
    try:
        from django.core.exceptions import ImproperlyConfigured

        try:
            from django.conf import settings as _django_settings

            # We can get a situation when Django module is installed in the system, but not initialized,
            # which means we are running not in a Django process.
            # In this case the following line throws ImproperlyConfigured exception
            if 'cloudinary' in _django_settings.INSTALLED_APPS:
                from django import get_version as _get_django_version
                global USER_PLATFORM
                USER_PLATFORM = "Django/{django_version}".format(django_version=_get_django_version())

            if 'CLOUDINARY' in dir(_django_settings):
                return _django_settings.CLOUDINARY
            else:
                return None

        except ImproperlyConfigured:
            return None

    except ImportError:
        return None


class Config(object):
    def __init__(self):
        django_settings = import_django_settings()
        if django_settings:
            self.update(**django_settings)
        elif os.environ.get("CLOUDINARY_CLOUD_NAME"):
            self.update(
                cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
                api_key=os.environ.get("CLOUDINARY_API_KEY"),
                api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
                secure_distribution=os.environ.get("CLOUDINARY_SECURE_DISTRIBUTION"),
                private_cdn=os.environ.get("CLOUDINARY_PRIVATE_CDN") == 'true'
            )
        elif os.environ.get("CLOUDINARY_URL"):
            cloudinary_url = os.environ.get("CLOUDINARY_URL")
            self._parse_cloudinary_url(cloudinary_url)

    def _parse_cloudinary_url(self, cloudinary_url):
        uri = urlparse(cloudinary_url.replace("cloudinary://", "http://"))
        for k, v in parse_qs(uri.query).items():
            if self._is_nested_key(k):
                self._put_nested_key(k, v)
            else:
                self.__dict__[k] = v[0]
        self.update(
            cloud_name=uri.hostname,
            api_key=uri.username,
            api_secret=uri.password,
            private_cdn=uri.path != ''
        )
        if uri.path != '':
            self.update(secure_distribution=uri.path[1:])

    def __getattr__(self, i):
        if i in self.__dict__:
            return self.__dict__[i]
        else:
            return None

    def update(self, **keywords):
        for k, v in keywords.items():
            self.__dict__[k] = v

    def _is_nested_key(self, key):
        return re.match(r'\w+\[\w+\]', key)

    def _put_nested_key(self, key, value):
        chain = re.split(r'[\[\]]+', key)
        chain = [key for key in chain if key]
        outer = self.__dict__
        last_key = chain.pop()
        for inner_key in chain:
            if inner_key in outer:
                inner = outer[inner_key]
            else:
                inner = dict()
                outer[inner_key] = inner
            outer = inner
        if isinstance(value, list):
            value = value[0]
        outer[last_key] = value


_config = Config()


def config(**keywords):
    global _config
    _config.update(**keywords)
    return _config


def reset_config():
    global _config
    _config = Config()


_http_client = HttpClient()


@python_2_unicode_compatible
class CloudinaryResource(object):
    def __init__(self, public_id=None, format=None, version=None,
                 signature=None, url_options=None, metadata=None, type=None, resource_type=None,
                 default_resource_type=None):
        self.metadata = metadata
        metadata = metadata or {}
        self.public_id = public_id or metadata.get('public_id')
        self.format = format or metadata.get('format')
        self.version = version or metadata.get('version')
        self.signature = signature or metadata.get('signature')
        self.type = type or metadata.get('type') or "upload"
        self.resource_type = resource_type or metadata.get('resource_type') or default_resource_type
        self.url_options = url_options or {}

    def __str__(self):
        return self.public_id

    def __len__(self):
        return len(self.public_id) if self.public_id is not None else 0

    def validate(self):
        return self.signature == self.get_expected_signature()

    def get_prep_value(self):
        if None in [self.public_id,
                    self.type,
                    self.resource_type]:
            return None
        prep = ''
        prep = prep + self.resource_type + '/' + self.type + '/'
        if self.version: prep = prep + 'v' + str(self.version) + '/'
        prep = prep + self.public_id
        if self.format: prep = prep + '.' + self.format
        return prep

    def get_presigned(self):
        return self.get_prep_value() + '#' + self.get_expected_signature()

    def get_expected_signature(self):
        return utils.api_sign_request({"public_id": self.public_id, "version": self.version}, config().api_secret)

    @property
    def url(self):
        return self.build_url(**self.url_options)

    def __build_url(self, **options):
        combined_options = dict(format=self.format, version=self.version, type=self.type,
                                resource_type=self.resource_type or "image")
        combined_options.update(options)
        public_id = combined_options.get('public_id') or self.public_id
        return utils.cloudinary_url(public_id, **combined_options)

    def build_url(self, **options):
        return self.__build_url(**options)[0]

    @staticmethod
    def default_poster_options(options):
        options["format"] = options.get("format", "jpg")

    @staticmethod
    def default_source_types():
        return ['webm', 'mp4', 'ogv']

    @staticmethod
    def _validate_srcset_data(srcset_data):
        """
        Helper function. Validates srcset_data parameters

        :param srcset_data: A dictionary containing the following keys:
                breakpoints A list of breakpoints.
                min_width   Minimal width of the srcset images
                max_width   Maximal width of the srcset images.
                max_images  Number of srcset images to generate.

        :return: bool True on success or False on failure
        """
        if not all(k in srcset_data and isinstance(srcset_data[k], numbers.Number) for k in ("min_width", "max_width",
                                                                                             "max_images")):
            logger.warning("Either valid (min_width, max_width, max_images)" +
                           "or breakpoints must be provided to the image srcset attribute")
            return False

        if srcset_data["min_width"] > srcset_data["max_width"]:
            logger.warning("min_width must be less than max_width")
            return False

        if srcset_data["max_images"] <= 0:
            logger.warning("max_images must be a positive integer")
            return False

        return True

    def _generate_breakpoints(self, srcset_data):
        """
        Helper function. Calculates static responsive breakpoints using provided parameters.

        Either the breakpoints or min_width, max_width, max_images must be provided.

        :param srcset_data: A dictionary containing the following keys:
                                breakpoints A list of breakpoints.
                                min_width   Minimal width of the srcset images
                                max_width   Maximal width of the srcset images.
                                max_images  Number of srcset images to generate.

        :return: A list of breakpoints

        :raises ValueError: In case of invalid or missing parameters
        """
        breakpoints = srcset_data.get("breakpoints", list())

        if breakpoints:
            return breakpoints

        if not self._validate_srcset_data(srcset_data):
            return None

        min_width, max_width, max_images = srcset_data["min_width"], srcset_data["max_width"], srcset_data["max_images"]

        if max_images == 1:
            # if user requested only 1 image in srcset, we return max_width one
            min_width = max_width

        step_size = int(ceil(float(max_width - min_width) / (max_images - 1 if max_images > 1 else 1)))

        curr_breakpoint = min_width

        while curr_breakpoint < max_width:
            breakpoints.append(curr_breakpoint)
            curr_breakpoint += step_size

        breakpoints.append(max_width)

        return breakpoints

    def _fetch_breakpoints(self, srcset_data=None, **options):
        """
        Helper function. Retrieves responsive breakpoints list from cloudinary server

        When passing special string to transformation `width` parameter of form `auto:breakpoints{parameters}:json`,
        the response contains JSON with data of the responsive breakpoints

        :param srcset_data: A dictionary containing the following keys:
                                min_width   Minimal width of the srcset images
                                max_width   Maximal width of the srcset images
                                bytes_step  Minimal bytes step between images
                                max_images  Number of srcset images to generate
        :param options: Additional options

        :return: Resulting breakpoints
        """
        if srcset_data is None:
            srcset_data = dict()

        min_width = srcset_data.get("min_width", 50)
        max_width = srcset_data.get("max_width", 1000)
        bytes_step = srcset_data.get("bytes_step", 20000)
        max_images = srcset_data.get("max_images", 20)
        transformation = srcset_data.get("transformation")

        kbytes_step = int(ceil(float(bytes_step)/1024))

        breakpoints_width_param = "auto:breakpoints_{min_width}_{max_width}_{kbytes_step}_{max_images}:json".format(
            min_width=min_width, max_width=max_width, kbytes_step=kbytes_step, max_images=max_images)
        breakpoints_url = utils.cloudinary_scaled_url(self.public_id, breakpoints_width_param, transformation, options)

        return _http_client.get_json(breakpoints_url).get("breakpoints", None)

    def _get_or_generate_breakpoints(self, srcset_data, **options):
        """
        Helper function. Gets from cache or calculates srcset breakpoints using provided parameters

        :param srcset_data: A dictionary containing the following keys:
                                breakpoints A list of breakpoints.
                                min_width   Minimal width of the srcset images
                                max_width   Maximal width of the srcset images
                                max_images  Number of srcset images to generate
        :param options: Additional options

        :return: Resulting breakpoints
        """

        breakpoints = srcset_data.get("breakpoints")

        if breakpoints:
            return breakpoints

        if srcset_data.get("use_cache"):
            breakpoints = responsive_breakpoints_cache.instance.get(self.public_id, **options)
            if not breakpoints:
                try:
                    breakpoints = self._fetch_breakpoints(srcset_data, **options)
                except GeneralError as e:
                    logger.warning("Failed getting responsive breakpoints: {error}".format(error=e.message))

                if breakpoints:
                    responsive_breakpoints_cache.instance.set(self.public_id, breakpoints, **options)

        if not breakpoints:
            # Static calculation if cache is not enabled or we failed to fetch breakpoints
            breakpoints = self._generate_breakpoints(srcset_data)

        return breakpoints

    def _generate_srcset_attribute(self, breakpoints, transformation=None, **options):
        """
        Helper function. Generates srcset attribute value of the HTML img tag.

        :param srcset_data: A dictionary containing the following keys:
                                breakpoints A list of breakpoints.
                                min_width   Minimal width of the srcset images
                                max_width   Maximal width of the srcset images.
                                max_images  Number of srcset images to generate.
        :param options:     Additional options

        :return:  Resulting srcset attribute value

        :raises ValueError: In case of invalid or missing parameters
        """
        if not breakpoints:
            return None

        if transformation is None:
            transformation = dict()

        return ", ".join(["{0} {1}w".format(utils.cloudinary_scaled_url(
            self.public_id, w, transformation, options), w) for w in breakpoints])

    @staticmethod
    def _generate_sizes_attribute(breakpoints):
        """
        Helper function. Generates sizes attribute value of the HTML img tag.

        :param srcset_data: A dictionary containing the following keys:
                                breakpoints     A list of breakpoints.
                                min_width       Minimal width of the srcset images
                                max_width       Maximal width of the srcset images.
                                max_images      Number of srcset images to generate.

        :return: Resulting 'sizes' attribute value

        :raises ValueError: In case of invalid or missing parameters
        """
        if not breakpoints:
            return None

        return ", ".join("(max-width: {bp}px) {bp}px".format(bp=bp) for bp in breakpoints)

    def _generate_image_responsive_attributes(self, attributes, srcset_data, **options):
        """
        Helper function. Generates srcset and sizes attributes of the image tag

        Create both srcset and sizes here to avoid fetching breakpoints twice

        :param attributes: Existing attributes
        :param srcset_data: A dictionary containing the following keys:
                                breakpoints     A list of breakpoints.
                                min_width       Minimal width of the srcset images
                                max_width       Maximal width of the srcset images.
                                max_images      Number of srcset images to generate.
        :param options:     Additional options

        :return: The responsive attributes
        """
        responsive_attributes = dict()

        if not srcset_data:
            return responsive_attributes

        breakpoints = None

        if "srcset" not in attributes:
            breakpoints = self._get_or_generate_breakpoints(srcset_data, **options)
            transformation = srcset_data.get("transformation")
            srcset_attr = self._generate_srcset_attribute(breakpoints, transformation, **options)
            if srcset_attr:
                responsive_attributes["srcset"] = srcset_attr

        if "sizes" not in attributes and srcset_data.get("sizes") is True:
            if not breakpoints:
                breakpoints = self._get_or_generate_breakpoints(srcset_data, **options)
            sizes_attr = self._generate_sizes_attribute(breakpoints)
            if sizes_attr:
                responsive_attributes["sizes"] = sizes_attr

        return responsive_attributes

    def image(self, **options):
        """
        Generates HTML img tag

        :param options: Additional options

        :return: Resulting img tag
        """
        if options.get("resource_type", self.resource_type) == "video":
            self.default_poster_options(options)

        srcset_data = config().srcset or dict()
        srcset_data = srcset_data.copy()
        srcset_data.update(options.pop("srcset", dict()))

        custom_attributes = options.pop("attributes", dict())

        src, attrs = self.__build_url(**options)

        client_hints = attrs.pop("client_hints", config().client_hints)
        responsive = attrs.pop("responsive", False)
        hidpi = attrs.pop("hidpi", False)

        if (responsive or hidpi) and not client_hints:
            attrs["data-src"] = src

            classes = "cld-responsive" if responsive else "cld-hidpi"
            if "class" in attrs:
                classes += " " + attrs["class"]
            attrs["class"] = classes

            src = attrs.pop("responsive_placeholder", config().responsive_placeholder)
            if src == "blank":
                src = CL_BLANK

        responsive_attrs = self._generate_image_responsive_attributes(custom_attributes, srcset_data, **options)

        if responsive_attrs:
            # width and height attributes override srcset behavior, they should be removed from html attributes.
            for key in {"width", "height"}:
                attrs.pop(key, None)

        attrs.update(responsive_attrs)
        # Explicitly provided attributes override options
        attrs.update(custom_attributes)

        if src:
            attrs["src"] = src

        return u"<img {0}/>".format(utils.html_attrs(attrs))

    def video_thumbnail(self, **options):
        self.default_poster_options(options)
        return self.build_url(**options)

    # Creates an HTML video tag for the provided +source+
    #
    # ==== Options
    # * <tt>source_types</tt> - Specify which source type the tag should include. defaults to webm, mp4 and ogv.
    # * <tt>source_transformation</tt> - specific transformations to use for a specific source type.
    # * <tt>poster</tt> - override default thumbnail:
    #   * url: provide an ad hoc url
    #   * options: with specific poster transformations and/or Cloudinary +:public_id+
    #
    # ==== Examples
    #   CloudinaryResource("mymovie.mp4").video()
    #   CloudinaryResource("mymovie.mp4").video(source_types = 'webm')
    #   CloudinaryResource("mymovie.ogv").video(poster = "myspecialplaceholder.jpg")
    #   CloudinaryResource("mymovie.webm").video(source_types = ['webm', 'mp4'], poster = {'effect': 'sepia'})
    def video(self, **options):
        public_id = options.get('public_id', self.public_id)
        source = re.sub("\.({0})$".format("|".join(self.default_source_types())), '', public_id)

        source_types = options.pop('source_types', [])
        source_transformation = options.pop('source_transformation', {})
        fallback = options.pop('fallback_content', '')
        options['resource_type'] = options.pop('resource_type', self.resource_type or 'video')

        if not source_types: source_types = self.default_source_types()
        video_options = options.copy()

        if 'poster' in video_options:
            poster_options = video_options['poster']
            if isinstance(poster_options, dict):
                if 'public_id' in poster_options:
                    video_options['poster'] = utils.cloudinary_url(poster_options['public_id'], **poster_options)[0]
                else:
                    video_options['poster'] = self.video_thumbnail(public_id=source, **poster_options)
        else:
            video_options['poster'] = self.video_thumbnail(public_id=source, **options)

        if not video_options['poster']: del video_options['poster']

        nested_source_types = isinstance(source_types, list) and len(source_types) > 1
        if not nested_source_types:
            source = source + '.' + utils.build_array(source_types)[0]

        video_url = utils.cloudinary_url(source, **video_options)
        video_options = video_url[1]
        if not nested_source_types:
            video_options['src'] = video_url[0]
        if 'html_width' in video_options: video_options['width'] = video_options.pop('html_width')
        if 'html_height' in video_options: video_options['height'] = video_options.pop('html_height')

        sources = ""
        if nested_source_types:
            for source_type in source_types:
                transformation = options.copy()
                transformation.update(source_transformation.get(source_type, {}))
                src = utils.cloudinary_url(source, format=source_type, **transformation)[0]
                video_type = "ogg" if source_type == 'ogv' else source_type
                mime_type = "video/" + video_type
                sources += "<source {attributes}>".format(attributes=utils.html_attrs({'src': src, 'type': mime_type}))

        html = "<video {attributes}>{sources}{fallback}</video>".format(
            attributes=utils.html_attrs(video_options), sources=sources, fallback=fallback)
        return html


class CloudinaryImage(CloudinaryResource):
    def __init__(self, public_id=None, **kwargs):
        super(CloudinaryImage, self).__init__(public_id=public_id, default_resource_type="image", **kwargs)


class CloudinaryVideo(CloudinaryResource):
    def __init__(self, public_id=None, **kwargs):
        super(CloudinaryVideo, self).__init__(public_id=public_id, default_resource_type="video", **kwargs)
