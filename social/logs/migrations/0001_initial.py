# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-02 16:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=150)),
                ('code', models.CharField(blank=True, max_length=5, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('retry_after', models.DateTimeField(blank=True, null=True)),
                ('type', models.CharField(choices=[('i', 'info'), ('w', 'warning'), ('e', 'error')], default='i', max_length=1)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
