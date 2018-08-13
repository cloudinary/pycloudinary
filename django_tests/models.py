from six import python_2_unicode_compatible

from cloudinary.models import CloudinaryField
from django.db import models


@python_2_unicode_compatible
class Poll(models.Model):
    question = models.CharField(max_length=200)
    image_width = models.PositiveIntegerField(null=True)
    image_height = models.PositiveIntegerField(null=True)
    image = CloudinaryField('image', null=True, width_field='image_width', height_field='image_height')

    def __str__(self):
        return self.question


@python_2_unicode_compatible
class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()

    def __str__(self):
        return self.choice.encode()
