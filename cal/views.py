from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone
import calendar
from django.forms.models import modelformset_factory
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q


# Create your views here.

from .models import Entry

MONTH_NAMES = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
]

DAY_NAMES = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
]


def reminders(request):
    """
    Data for the reminder sidebar.
    """
    today = timezone.now()
    tomorrow = today + datetime.timedelta(days=1)
    # we can merge two queries together easily like this:...
    return Entry.objects.filter(
        Q(date=today)|Q(date=tomorrow), 
        creator=request.user, 
        remind=True,
    )
#    # ...or like this:
#    return (
#        Entry.objects.filter(
#            date=today, 
#            creator=request.user, 
#            remind=True,
#        ) | 
#        Entry.objects.filter(
#            date=tomorrow,
#            creator=request.user,
#            remind=True,
#        )
#    )


@login_required
def year(request, year=None):
    """
    List three years per page.
    """

    now = timezone.now()
    if year:
        year = int(year)
    else:
        year = now.year

    years = []
    for yr in [year-1, year, year+1,]:
        months = []
        for n, month in enumerate(MONTH_NAMES):
            entries = Entry.objects.filter(date__year=yr, date__month=n+1)
            entry = (True if entries 
                else False)
            current = (True if (yr == now.year) and (n == now.month-1)
                else False)
            months.append({
                'n': n+1,
                'name': month, 
                'entry': entry, 
                'current': current,
                })
        years.append((yr, months))

    return render_to_response('cal/year.html', {
        'years': years,
        'user': request.user,
        'prev_year': year - 3,
        'next_year': year + 3,
        'reminders': reminders(request),
        })


@login_required
def month(request, year=None, month=None, change=None):
    """
    Display the days in the specified month.
    """
    # default to this month
    today = timezone.datetime.today()
    if not year:
        year, month = today.year, today.month
    else:
        year, month = int(year), int(month)
    date = timezone.datetime(year=year, month=month, day=15)

    # handle month change, with year rollover
    if change:
        monthDelta = datetime.timedelta(days=31)
        if change == 'prev': 
            monthDelta = datetime.timedelta(days=-31)
        date = date + monthDelta

    # intial values
    cal = calendar.Calendar()
    month_days = cal.itermonthdays(date.year, date.month)
    weeks = [[]]
    week_no = 0

    # process all the days in the month
    for day in month_days:
        entries = current = False
        if day:
            dayDate = datetime.date(year=date.year, month=date.month, day=day)
            entries = Entry.objects.filter(date=dayDate)
            current = (dayDate == today)
        weeks[week_no].append((day, entries, current))
        if len(weeks[week_no]) == 7:
            weeks.append([])
            week_no += 1

    return render_to_response(
        'cal/month.html',
        {
            'date': date,
            'user': request.user,
            'weeks': weeks,
            'month_name': MONTH_NAMES[date.month-1],
            'day_names': DAY_NAMES,
            'reminders': reminders(request),
        },
    )


@login_required
def day(request, year=None, month=None, day=None, change=None):
    """
    Display entries in a particular day.
    """
    # default to today
    today = timezone.datetime.today()
    if not year:
        year, month, day = today.year, today.month, today.day
    else:
        year, month, day = int(year), int(month), int(day)
    date = timezone.datetime(year=year, month=month, day=day)

    # handle day change with year and month rollover
    if change:
        dayDelta = datetime.timedelta(days=1)
        if change == 'prev':
            dayDelta = datetime.timedelta(days=-1)
        date = date + dayDelta

    # create a form for entry of new entries (sic)
    EntriesFormset = modelformset_factory(
        Entry, 
        extra=1, 
        exclude=('creator', 'date'),
        can_delete=True,
    )

    # save the changes if this is a post request
    if request.method == 'POST':
        formset = EntriesFormset(request.POST)

        if formset.is_valid():
            entries = formset.save(commit=False)

            # really delete forms marked for removal
            for entry in formset.deleted_objects:
                entry.delete()

            # add the current date and user, and really save it
            for entry in entries:
                entry.creator = request.user
                entry.date = date
                entry.save()
            return HttpResponseRedirect(reverse(
                    'cal.views.month', 
                    args=(year, month)
            ))

    # unposted form
    else:
        formset = EntriesFormset(
            queryset=Entry.objects.filter(date=date, creator=request.user)
        )

    context = {
        'entries': formset,
        'date': date,
        'month_name': MONTH_NAMES[date.month-1],
        'user': request.user,
    }
    context.update(csrf(request))
    return render_to_response('cal/day.html', context)
