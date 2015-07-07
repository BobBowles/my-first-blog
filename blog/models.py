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
        
    def approved_comments(self):
        """
        List the comments on this post that have been approved.
        """
        return self.comments.filter(approved=True)
        
    def __str__(self):
        return self.title
        
        
class Comment(models.Model):
    post = models.ForeignKey('blog.Post', related_name='comments')
    
    # option here for registered users only making comments 
    # - other changes needed for this to work, eg, registration page for new 
    # users
    #author = models.ForeignKey('auth.User')
    author = models.CharField(max_length=200)
    
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    
    def approve(self):
        self.approved = True
        self.save()
        
    def __str__(self):
        return self.text
    
