from django.conf import settings

"""
Custom settings and their defaults for the cal app are defined here.
"""

def get(key, default):
    return getattr(settings, key, default)


CAL_FIRST_DAY_OF_WEEK = get('CAL_FIRST_DAY_OF_WEEK', 0)

