from django.shortcuts import (
    get_object_or_404, 
    redirect,
    render, 
    render_to_response,
)
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone
import calendar
from django.forms.formsets import formset_factory
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
import locale
from . import settings

# Create your views here.

from .models import Entry
from .forms import EntryForm


# set the first day of the week (default 0=monday)
# (uses settings variable CAL_FIRST_DAY_OF_WEEK)
calendar.setfirstweekday(settings.CAL_FIRST_DAY_OF_WEEK)


MONTH_NAMES = calendar.month_name[1:]
DAY_NAMES = (
    calendar.day_name[calendar.firstweekday():] + 
    calendar.day_name[:calendar.firstweekday()]
)


def evaluateTimeSlots():
    """
    Calculate labels and starting times for diary day display.
    Returns a list of labels and start/end times of time slots.
    """
    DUMMY_DAY = timezone.datetime.today()
    TIME_START = datetime.time(hour=6)
    TIME_FINISH = datetime.time(hour=20)
    TIME_INC = datetime.timedelta(minutes=30)

    time = datetime.datetime.combine(DUMMY_DAY, TIME_START)
    finish = datetime.datetime.combine(DUMMY_DAY, TIME_FINISH)
    timeSlots = []
    while (time <= finish):
        thisTime = time.time()
        time += TIME_INC
        timeSlots.append((
            thisTime.strftime('%I:%M %p'), 
            thisTime.strftime('time%H%M'),
            thisTime,
            time.time(),
        ))
    return timeSlots


TIME_SLOTS = evaluateTimeSlots()



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
    ).order_by('date', 'time')
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
    cal = calendar.Calendar(calendar.firstweekday())
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


def getDate(year, month, day, change):
    """
    Helper function to obtain the date from kwargs.
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
    return date


@login_required
def day(request, year=None, month=None, day=None, change=None):
    """
    Display entries in a particular day in a calendar-style day view.
    """
    date = getDate(year, month, day, change)

    # obtain the day's entries divided into time slots
    time_slots = []
    for timeLabel, modalLabel, startTime, endTime in TIME_SLOTS:
        entries = Entry.objects\
            .filter(
                date=date, 
                time__gte=startTime, 
                time__lt=endTime, 
                creator=request.user
        )
        time_slots.append((
            timeLabel, 
            modalLabel,
            startTime,
            entries.first(),
        ))

    return render_to_response(
        'cal/day.html', 
        {
            'date': date,
            'user': request.user,
            'month_name': MONTH_NAMES[date.month-1],
            'time_slots': time_slots,
            'reminders': reminders(request),
        },
    )


@login_required
def day_list(request, year=None, month=None, day=None, change=None):
    """
    Display entries in a particular day in an editable list.
    """
    date = getDate(year, month, day, change)

    # create a form for entry of new entries (sic)
#    timeWidgetOptions = {
#        'format': 'HH:ii P',
#        'showMeridian': True,
#    }
#    durationWidgetOptions = {
#        'format': 'hh:ii',
#    }
    EntriesFormset = formset_factory(
        EntryForm, 
        extra=1, 
        exclude=('creator', 'date'),
        can_delete=True,
#        widgets = {
#            'time': TimeWidget(
#                bootstrap_version=3,
#                options=timeWidgetOptions,
#            ),
#            'duration': TimeWidget(
#                bootstrap_version=3,
#                options=durationWidgetOptions,
#            )
#        },
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
            queryset=Entry.objects\
                .filter(date=date, creator=request.user)\
                    .order_by('time')
        )

    context = {
        'entries': formset,
        'date': date,
        'month_name': MONTH_NAMES[date.month-1],
        'user': request.user,
    }
    context.update(csrf(request))
    return render_to_response('cal/day_list.html', context)


@login_required
def entry(
    request, 
    pk=None, 
    year=None, 
    month=None, 
    day=None, 
    hour=None, 
    minute=None,
    ):
    """
    Edit/create an entry for the diary.
    """
    date = timezone.now().date()
    time = timezone.now().time()
    entry = None
    if pk:                              # edit existing entry
        entry = get_object_or_404(Entry, pk=pk)
    else:                               # create new
        # determine the date and time to use - now is the default
        if year:                        # use date/time provided
            date = datetime.date(
                year=int(year),
                month=int(month),
                day=int(day),
            )
            time = datetime.time(
                hour=int(hour),
                minute=int(minute),
            )
        entry = Entry(
            date=date,
            time=time,
            creator=request.user,
        )

    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save(commit=False)
            # do any necessary tidying of entry attributes
            #
            entry.save()
            return redirect(
                'cal.views.day', 
                year=entry.date.year, 
                month=entry.date.month,
                day=entry.date.day,
            )
    else:
        form = EntryForm(instance=entry)
    return render(
        request, 
        'cal/entry.html', 
        {
            'form': form,
            'date': date,
        },
    )

