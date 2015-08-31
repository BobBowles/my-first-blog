# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('cal', '0002_auto_20150810_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='duration',
            field=models.TimeField(default=datetime.time(1, 0), blank=True),
        ),
    ]
