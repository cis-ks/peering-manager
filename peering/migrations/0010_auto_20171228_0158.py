# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-28 00:58
from __future__ import unicode_literals

from django.db import migrations
import peering.fields


class Migration(migrations.Migration):

    dependencies = [
        ('peering', '0009_auto_20171226_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='autonomoussystem',
            name='asn',
            field=peering.fields.ASNField(unique=True),
        ),
    ]