from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone
from django.shortcuts import render_to_response
import calendar

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
#        'reminders': reminders(request),
        })


@login_required
def month(request, year=None, month=None, change=None):
    """
    Display the days in the specified month.
    """
    now = timezone.now()
    if not year:
        year, month = now.year, now.months
    else:
        year, month = int(year), int(month)

    # handle month change, remembering end-of-year rollover
    if change in ['prev', 'next']:
        currentMonth = timezone.datetime(year=year, month=month, day=15)
        monthDelta = datetime.timedelta(days=31)
        if change == 'prev': 
            monthDelta = datetime.timedelta(days=-31)
        currentMonth = currentMonth + monthDelta
        year, month = currentMonth.year, currentMonth.month

    # intial values
    cal = calendar.Calendar()
    month_days = cal.itermonthdays(year, month)
    weeks = [[]]
    week_no = 0

    # process all the days in the month
    for day in month_days:
        entries = current = False
        if day:
            date = datetime.date(year=year, month=month, day=day)
            entries = Entry.objects.filter(date=date)
            current = (
                now.year == year and
                now.month == month and
                now.day == day
            )
        weeks[week_no].append((day, entries, current))
        if len(weeks[week_no]) == 7:
            weeks.append([])
            week_no += 1

    return render_to_response(
        'cal/month.html',
        {
            'year': year,
            'month': month,
            'user': request.user,
            'weeks': weeks,
            'month_name': MONTH_NAMES[month-1],
            'day_names': DAY_NAMES,
        },
    )
