#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
from cloudinary.compat import  StringIO
from google.appengine.ext.webapp import template
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url


class MainHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        template_values = {
            'image_url': None,
            'thumbnail_url1': None,
            'thumbnail_url2': None
        }
        self.response.write(template.render(path, template_values))

    def post(self):
        image_url = None
        thumbnail_url1 = None
        thumbnail_url2 = None
        file_to_upload = self.request.get('file')
        if file_to_upload:
            str_file = StringIO(file_to_upload)
            str_file.name = 'file'
            upload_result = upload(str_file)
            image_url = upload_result['url']
            thumbnail_url1, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=100,
                                                     height=100)
            thumbnail_url2, options = cloudinary_url(upload_result['public_id'], format="jpg", crop="fill", width=200,
                                                     height=100, radius=20, effect="sepia")
        template_values = {
            'image_url': image_url,
            'thumbnail_url1': thumbnail_url1,
            'thumbnail_url2': thumbnail_url2
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.write(template.render(path, template_values))

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
