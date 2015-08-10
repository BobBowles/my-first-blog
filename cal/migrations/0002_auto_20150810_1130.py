# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='duration',
            field=models.DurationField(blank=True, default=datetime.timedelta(0, 3600)),
        ),
        migrations.AddField(
            model_name='entry',
            name='time',
            field=models.TimeField(blank=True, default=datetime.time(12, 0)),
        ),
    ]
