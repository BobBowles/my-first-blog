from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
import datetime
from django.utils import timezone
from django.forms import ValidationError


# Create your models here.

DEFAULT_DURATION = datetime.timedelta(hours=1)
DEFAULT_TIME = datetime.time(hour=12)



class Entry(models.Model):
    """
    A calendar entry, some event entered in the calendar.

    Entries need to be able to compare times and do basic temporal arithmetic.
    To do this (I think) we need to implement rich comparator methods so one
    entry knows how to compare itself with another.
    One possible (potentially undesirable) side-effect is that entries may
    consider each other 'equal' when they have neither the same start time
    nor the same duration. They will nevertheless be 'equivalent' in sharing
    a portion of time.
    """

    title = models.CharField(max_length=40)
    snippet = models.CharField(max_length=150, blank=True)
    body = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    date = models.DateField(blank=True)
    time = models.TimeField(blank=True, default=DEFAULT_TIME)
    duration = models.DurationField(blank=True, default=DEFAULT_DURATION)
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


    def time_end(self):
        """
        Calculate the time of the end of the entry from the start time and the
        duration.
        Sadly the naive method of adding the duration directly to the time 
        is not supported in python datetime arithmetic; a datetime object has 
        to be used.
        """
        the_time = datetime.datetime.combine(self.date, self.time)
        the_time_end = the_time + self.duration
        return the_time_end.time()


    def __eq__(self, other):
        """
        Determine if the entries are 'eqivalent' (not necessarily mathematically
        equal).
        NOTE: time period end time is non-inclusive.
        """
        # dates must be equal to start with
        # TODO: note time rounding kludge
        if (self.date.timetuple()[0:3] != other.date.timetuple()[0:3]):
            return False

        # time periods do not overlap; self happens before other
        if (self.time < other.time and self.time_end() <= other.time):
            return False

        # time periods do not overlap; self happens after other
        if (self.time > other.time and self.time >= other.time_end()):
            return False

        # anything else has to mean they overlap in time, right?
        return True


    def clean(self):
        """
        Override Model method to validate the content. We need the entry to be 
        invalid if it clashes in time with a pre-existing entry.
        """
        # do basic housekeeping first
        #super(models.Model, self).clean()

        # get the day's existing entries
        savedEntries = Entry.objects.filter(date=self.date)

        # ensure no time clashes
        for other in savedEntries:
            if self == other:
                # if we are just saving the same entry to the same time, its OK
                if not self.pk or (self.pk and self.pk != other.pk):
                    raise ValidationError(
            'Time clash not allowed. Please change the date/time/duration.'
                    )


    class Meta:
        verbose_name_plural = 'entries'


