from django.db import models
from cloudinary.models import CloudinaryField
from six import python_2_unicode_compatible

@python_2_unicode_compatible
class Poll(models.Model):
    question = models.CharField(max_length=200)
    image = CloudinaryField('image', null=True)

    def __str__(self):
        return self.question

@python_2_unicode_compatible
class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()

    def __str__(self):
        return self.choice.encode()

