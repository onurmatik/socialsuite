# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-19 16:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tokens', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RateLimitStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('resource', models.CharField(max_length=100)),
                ('limit', models.PositiveIntegerField()),
                ('remaining', models.PositiveIntegerField()),
                ('reset', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='oauthtoken',
            name='retry_after',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='oauthtoken',
            name='access_level',
            field=models.CharField(choices=[(1, 'Read only'), (2, 'Read and Write'), (3, 'Read, Write and Access direct messages')], default='w', max_length=1),
        ),
        migrations.AddField(
            model_name='ratelimitstatus',
            name='token',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tokens.OAuthToken'),
        ),
    ]
