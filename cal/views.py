from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone
from django.shortcuts import render_to_response

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


@login_required
def main(request, year=None):
    """
    List three years per page.
    """

    now = timezone.now()
    if year:
        year = int(year)
    else:
        year = now.year

    years = []
    for yr in [year, year+1, year+2]:
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

    return render_to_response(('cal/main.html', {
        'years': years,
        'user': request.user,
        'year': year,
#        'reminders': reminders(request),
        }))
