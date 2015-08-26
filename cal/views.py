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


DATE_SLUG_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M'
TIME_SLUG_FORMAT = '%H-%M'
DATETIME_SLUG_FORMAT = '%Y-%m-%d_%H-%M'


def evaluateTimeSlots():
    """
    Calculate labels and starting times for diary day display.
    Returns a list of labels and start/end times of time slots.
    """
    DUMMY_DAY = timezone.localtime(timezone.now()).date()
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
            thisTime.strftime(TIME_FORMAT), 
            thisTime.strftime(TIME_SLUG_FORMAT),
            thisTime,
            time.time(),
        ))
    return timeSlots


TIME_SLOTS = evaluateTimeSlots()



def reminders(request):
    """
    Data for the reminder sidebar.
    """
    today = timezone.localtime(timezone.now()).date()
    tomorrow = today + datetime.timedelta(days=1)
    # we can merge two queries together easily like this:...
    return Entry.objects.filter(
        Q(date=today)|Q(date=tomorrow), 
        creator=request.user, 
        remind=True,
    ).order_by('date', 'time')



@login_required
def year(request, year=None):
    """
    List three years per page.
    """

    now = timezone.localtime(timezone.now()).date()
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
    today = timezone.localtime(timezone.now()).date()
    if not year:
        year, month = today.year, today.month
    else:
        year, month = int(year), int(month)
    date = timezone.datetime(year=year, month=month, day=15).date()

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
        nav_slug = None
        if day:
            dayDate = datetime.date(year=date.year, month=date.month, day=day)
            entries = Entry.objects.filter(date=dayDate)
            nav_slug = dayDate.strftime(DATE_SLUG_FORMAT)
            current = (dayDate == today)
        weeks[week_no].append((day, nav_slug, entries, current))
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
    print('DEPRECATED:  Getting kwargs date...')
    today = timezone.localtime(timezone.now()).date()
    if not year:
        year, month, day = today.year, today.month, today.day
    else:
        year, month, day = int(year), int(month), int(day)
    date = timezone.datetime(year=year, month=month, day=day).date()

    # handle day change with year and month rollover
    if change:
        dayDelta = datetime.timedelta(days=1)
        if change == 'prev':
            dayDelta = datetime.timedelta(days=-1)
        date = date + dayDelta
    return date


def getDateFromSlug(slug, change):
    """
    Helper to derive a date from an iso format slug.
    """
    # default to today
    print('Getting slug date...')
    today = timezone.localtime(timezone.now()).date()
    date = None
    if not slug:
        date = today
    else:
        date = datetime.datetime.strptime(slug, DATE_SLUG_FORMAT)

    # handle day change with year and month rollover
    if change:
        dayDelta = datetime.timedelta(days=1)
        if change == 'prev':
            dayDelta = datetime.timedelta(days=-1)
        date = date + dayDelta
    return date.date()


@login_required
def multi_day(request, year=None, month=None, day=None, slug=None, change=None):
    """
    Display entries in a calendar-style 4-day layout.
    """
    today = timezone.localtime(timezone.now()).date()
    now = timezone.localtime(timezone.now()).time()
    date = (
        getDate(year, month, day, change) if year # deprecated
        else getDateFromSlug(slug, change)
    )

    # get date information etc for the days to display
    date_slots = []
    dayDelta = datetime.timedelta(days=1)
    for i in range(0, settings.CAL_MULTI_DAY_NUMBER):
        day = date + i*dayDelta
        dayHeader = day.strftime('%a %d')
        date_slug = day.strftime(DATE_SLUG_FORMAT)
        date_slots.append((
            day,
            dayHeader,
            date_slug,
        ))

    # header information
    date_start_head = date_slots[0][0].strftime('%b %d')
    date_end_head = date_slots[-1][0].strftime('%b %d')
    nav_slug = date_slots[0][0].strftime(DATE_SLUG_FORMAT)

    # obtain the days' entries divided into time slots
    # rows represent times...
    time_slots = []
    for timeLabel, time_slug, startTime, endTime in TIME_SLOTS:
        # cols represent days...
        day_entries = []
        currentTime = (now >= startTime and now < endTime)
        for day, dayHeader, date_slug in date_slots:
            entries = Entry.objects\
                .filter(
                    date=day, 
                    time__gte=startTime, 
                    time__lt=endTime, 
                    creator=request.user
            )
            day_entries.append((
                '_'.join((date_slug, time_slug)), 
                entries.first(),
                (currentTime and day == today),
            ))
        time_slots.append((
            timeLabel, 
            startTime,
            day_entries,
        ))

    return render_to_response(
        'cal/multi_day.html', 
        {
            'date': date,
            'date_start_head': date_start_head,
            'date_end_head': date_end_head,
            'nav_slug': nav_slug,
            'user': request.user,
            'month_name': MONTH_NAMES[date.month-1],
            'time_slots': time_slots,
            'date_slots': date_slots,
            'reminders': reminders(request),
        },
    )


@login_required
def day(request, year=None, month=None, day=None, slug=None, change=None):
    """
    Display entries in a particular day in a calendar-style day view.
    """
    date = (
        getDate(year, month, day, change) if year # deprecated
        else getDateFromSlug(slug, change)
    )
    currentDate = (date == timezone.now().date())
    now = timezone.localtime(timezone.now()).time()
    date_slug = date.strftime(DATE_SLUG_FORMAT)

    # obtain the day's entries divided into time slots
    time_slots = []
    for timeLabel, time_slug, startTime, endTime in TIME_SLOTS:
        entries = Entry.objects\
            .filter(
                date=date, 
                time__gte=startTime, 
                time__lt=endTime, 
                creator=request.user
        )
        time_slots.append((
            timeLabel, 
            '_'.join((date_slug, time_slug)),
            startTime,
            entries.first(),
            (currentDate and (now >= startTime and now < endTime)),
        ))

    return render_to_response(
        'cal/day.html', 
        {
            'date': date,
            'nav_slug': date_slug,
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
    EntriesFormset = formset_factory(
        EntryForm, 
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
            queryset=Entry.objects\
                .filter(date=date, creator=request.user)\
                    .order_by('time')
        )

    context = {
        'entries': formset,
        'date': date,
        'month_name': MONTH_NAMES[date.month-1],
        'user': request.user,
        'reminders': reminders(request),
    }
    context.update(csrf(request))
    return render_to_response('cal/day_list.html', context)


@login_required
def entry(
    request, 
    pk=None, 
    year=None, month=None, day=None, hour=None, minute=None, # deprecated
    slug=None,
    ):
    """
    Edit/create an entry for the diary.
    """
    # defaults are here and now if no date/time is provided
    date = timezone.now().date()
    time = timezone.now().time()
    entry = None
    
    #
    if pk:                              # edit existing entry
        entry = get_object_or_404(Entry, pk=pk)
    else:                               # make a new entry
        # determine the date and time to use
        if year:                        # deprecated
            print('Entry using DEPRECATED kwargs year, etc.')
            date = datetime.date(
                year=int(year),
                month=int(month),
                day=int(day),
            )
            time = datetime.time(
                hour=int(hour),
                minute=int(minute),
            )
        elif slug:
            date_time = datetime.datetime.strptime(slug, DATETIME_SLUG_FORMAT)
            date, time = date_time.date(), date_time.time()
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
            
            entry.save()

            # in case the date has been edited re-calculate the navigation slug
            return redirect(
                'cal.views.day', 
                #year=entry.date.year, month=entry.date.month, day=entry.date.day,
                slug=entry.date.strftime(DATE_SLUG_FORMAT),
            )
    else:
        form = EntryForm(instance=entry)
    return render(
        request, 
        'cal/entry.html', 
        {
            'form': form,
            'date': entry.date,
            'reminders': reminders(request),
        },
    )


@login_required
def entry_delete(request, pk):
    """
    Remove a diary entry.
    """
    entry = get_object_or_404(Entry, pk=pk)
    date = entry.date
    entry.delete()
    return redirect(
        'cal.views.day', 
        year=date.year,
        month=date.month,
        day=date.day,
    )

