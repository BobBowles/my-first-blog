from django.contrib import admin
from .models import Entry, EntryAdmin

# Register your models here.

admin.site.register(Entry, EntryAdmin)
