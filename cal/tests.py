from django.test import TestCase
from .models import Entry
from django.utils import timezone
import datetime
from django.forms import ValidationError
import traceback

# Create your tests here.



def create_entry(dateDelta, time, duration, title, snippet, body):
    """
    Utility to create an entry for testing.
    """
    date = timezone.datetime.today() + dateDelta
    return Entry(
        title=title,
        snippet=snippet,
        body=body,
        date=date,
        time=time,
        duration=duration,
    )



class EntryModelTests(TestCase):
    """
    Tests of the entry model methods. 
    These tests are primarily about making sure entries can do basic time
    arithmetic and comparisons, with the intention that they can determine time
    collisions.
    """


    def test_time_end_calculation(self):
        """
        Make sure the time arithmetic works as expected.
        """
        dateDelta = datetime.timedelta(days=0)
        time = datetime.time(hour=12)
        duration = datetime.timedelta(hours=1)
        entry = create_entry(
            dateDelta, 
            time,
            duration,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        result = datetime.time(hour=13)
        self.assertEqual(entry.time_end(), result)


    def test_entry_time_relation_eq_different_days(self):
        """
        Entries on different days are not equal.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time = datetime.time(hour=12)
        duration = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time,
            duration,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        dateDelta2 = datetime.timedelta(days=1)
        entry2 = create_entry(
            dateDelta2, 
            time,
            duration,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertFalse(entry1 == entry2)


    def test_entry_time_relation_eq_identity(self):
        """
        Entries with identical dates, times, and durations are equal.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        dateDelta2 = datetime.timedelta(days=0)
        time2 = datetime.time(hour=12)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta2, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertTrue(entry1 == entry2)


    def test_entry_time_relation_eq_before(self):
        """
        Entries on the same day where the first ends before the second starts
        are not equal.
        """
        dateDelta = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        time2 = datetime.time(hour=14)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertFalse(entry1 == entry2)


    def test_entry_time_relation_eq_after(self):
        """
        Entries on the same day where the first starts after the second ends
        are not equal.
        """
        dateDelta = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        time2 = datetime.time(hour=9)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertFalse(entry1 == entry2)


    def test_entry_time_relation_eq_consecutive(self):
        """
        Entries on the same day where the first and second events are 
        consecutive are not equal.
        """
        dateDelta = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        time2 = entry1.time_end()
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertFalse(entry1 == entry2)


    def test_entry_time_relation_eq_envelope(self):
        """
        Entries on the same day where one event encompasses the other are 
        'equal'.
        """
        dateDelta = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=3)
        entry1 = create_entry(
            dateDelta, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        time2 = datetime.time(hour=13)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
#        print('Entry1: date: {0} start: {1} duration: {2} end: {3}'
#            .format(
#                entry1.date.timetuple()[0:3], 
#                entry1.time, 
#                entry1.duration, 
#                entry1.time_end(),
#            )
#        )
#        print('Entry2: date: {0} start: {1} duration: {2} end: {3}'
#            .format(
#                entry2.date.timetuple()[0:3], 
#                entry2.time, 
#                entry2.duration, 
#                entry2.time_end(),
#            )
#        )
        self.assertTrue(entry1 == entry2)


    def test_entry_time_relation_clean_clash(self):
        """
        Make sure cleaning the data raises the correct Exception when times
        clash with pre-existing entry data.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        entry1.save()
        dateDelta2 = datetime.timedelta(days=0)
        time2 = datetime.time(hour=12)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta2, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertTrue(entry1 == entry2)
        self.assertRaisesMessage(
            ValidationError, 
            'Time clash not allowed. Please change the date/time/duration.',
            entry2.clean,
        )


    def test_entry_time_relation_clean_no_clash(self):
        """
        Make sure cleaning the data raises no Exception when times do not
        clash with pre-existing entry data.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        entry1.save()
        dateDelta2 = datetime.timedelta(days=0)
        time2 = datetime.time(hour=14)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta2, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        # make sure an exception is NOT raised
        try:
            entry2.clean()
            self.assertFalse(entry1 == entry2)
        except Exception as e:
            traceback.print_exc()
            self.fail(
    'Cleaning an entry with no time clash raised an unexpected exception: {0}'
    .format(e)
            )


    def test_entry_time_relation_clean_save_existing(self):
        """
        Make sure cleaning the data raises no Exception we are just posting back.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        entry1.save()
        entry2 = Entry.objects.filter(
            date=entry1.date, 
            time=entry1.time,
        ).first()
        # make sure an exception is NOT raised
        try:
            entry2.clean()
            self.assertTrue(entry1 == entry2)
        except Exception as e:
            traceback.print_exc()
            self.fail(
    'Cleaning an entry that already exists raised an unexpected exception: {0}'
    .format(e)
            )

