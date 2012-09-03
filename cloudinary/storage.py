from django.core.files.storage import Storage
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import cloudinary.utils
import cloudinary.uploader
import urllib2


class CloudinaryStorage(Storage):
    def __init__(self):
        pass

    def _open(self, name, mode='rb'):
        if mode != 'rb':
            raise IOError('Files can only be open for binary read')

        url = self.url(name)
        return urllib2.urlopen(url)

    def _save(self, name, content):
        result = cloudinary.uploader.upload(content)

        result['relative'] = True
        (source, options) = cloudinary.utils.cloudinary_url(
            result['public_id'],
            **result
        )
        return source

    def delete(self, name):
        # Parse the public ID from the name and delete
        cloudinary.uploader.destroy(name.split('/')[-1].split('.')[0])

    def exists(self, name):
        # Since Cloudinary generates names automatically,
        # this shouldn't be an issue. It merely means that
        # exists() and get_available_name(), which isn't needed.
        #
        # This could be implemented by trying to open (or better yet,
        # with a HEAD request) and catching a 404 HTTPError.
        return False

    def size(self, name):
        # There's not much use for the size and there's
        # no way to get it without opening the file
        raise NotImplementedError('Can\'t get size with Cloudinary')

    def url(self, name):
        (source, options) = cloudinary.utils.cloudinary_url(name)
        return source

    def listdir(path):
        raise NotImplementedError('Can\'t list files with Cloudinary')

    def modified_time(name):
        raise NotImplementedError('Can\'t get modified time with Cloudinary')
