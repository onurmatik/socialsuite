# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-03 07:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20160202_0629'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='follow_history',
            new_name='follow_profile_history',
        ),
    ]
