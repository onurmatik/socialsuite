# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-09 11:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0005_auto_20160208_0850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='created_at',
            field=models.DateTimeField(db_index=True),
        ),
    ]
