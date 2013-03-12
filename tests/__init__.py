from django.conf import settings
settings.configure()
import api_test, image_test, uploader_test, utils_test
(api_test, image_test, uploader_test, utils_test) # appease pyflakes
