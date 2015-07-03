from django.db import models
from django.utils import timezone

# Create your models here.


class Post(models.Model):
    author = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    text = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    date_published = models.DateTimeField(blank=True, null=True)
    
    def publish(self):
        """
        Publish this post for public display.
        """
        self.date_published = timezone.now()
        self.save()
        
    def __str__(self):
        return self.title
