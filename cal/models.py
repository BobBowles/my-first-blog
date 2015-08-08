from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


# Create your models here.



class Entry(models.Model):
    """
    A calendar entry, some event entered in the calendar.
    """

    title = models.CharField(max_length=40)
    snippet = models.CharField(max_length=150, blank=True)
    body = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    date = models.DateField(blank=True)
    creator = models.ForeignKey(User, blank=True, null=True)
    remind = models.BooleanField(default=False)


    def __str__(self):
        if self.title:
            return self.creator.username + ' - ' + self.title
        else:
            return self.creator.username + ' - ' + self.snippet[:40]


    def short(self):
        if self.snippet:
            return '<i>{0}</i> - {1}'.format(self.title, self.snippet)
        else:
            return self.title
    short.allow_tags = True


    class Meta:
        verbose_name_plural = 'entries'



class EntryAdmin(admin.ModelAdmin):
    list_display = [
        'creator',
        'date',
        'title',
        'snippet',
        ]
    list_filter = [
        'creator',
        ]

