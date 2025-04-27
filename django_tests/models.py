from six import python_2_unicode_compatible
from cloudinary.models import CloudinaryField
from django.db import models

@python_2_unicode_compatible
class Poll(models.Model):
    """
    Represents a poll with a question and an optional image.
    """
    question = models.CharField(max_length=200)
    image = CloudinaryField('image', null=True, width_field='image_width', height_field='image_height')
    image_width = models.PositiveIntegerField(null=True)
    image_height = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        """
        Custom save method to update modified_at timestamp.
        """
        self.modified_at = timezone.now()
        super(Poll, self).save(*args, **kwargs)

@python_2_unicode_compatible
class Choice(models.Model):
    """
    Represents a choice in a poll and the number of votes it has received.
    """
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.choice_text

    def vote(self):
        """
        Increment the vote count for this choice.
        """
        self.votes += 1
        self.save()

    def save(self, *args, **kwargs):
        """
        Custom save method to update poll's modified_at timestamp.
        """
        self.poll.save()  # Update the parent poll's modified_at timestamp
        super(Choice, self).save(*args, **kwargs)
