#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from datetime import datetime
from time import strftime
from django.contrib.auth.models import User, UserManager


class UnixTimestampField(models.DateTimeField):
    """UnixTimestampField: creates a DateTimeField that is represented on the
    database as a TIMESTAMP field rather than the usual DATETIME field.
    """
    def __init__(self, null=False, blank=False, **kwargs):
        super(UnixTimestampField, self).__init__(**kwargs)
        # default for TIMESTAMP is NOT NULL unlike most fields, so we have to
        # cheat a little:
        self.blank, self.isnull = blank, null
        self.null = True  # To prevent the framework from shoving in "not null".

    def db_type(self, connection):
        typ = ['TIMESTAMP']
        # See above!
        if self.isnull:
            typ += ['NULL']
        if self.auto_created:
            typ += ['default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP']
        return ' '.join(typ)

    def to_python(self, value):
        if isinstance(value, int):
            return datetime.fromtimestamp(value)
        else:
            return models.DateTimeField.to_python(self, value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        # Use '%Y%m%d%H%M%S' for MySQL < 4.1
        return strftime('%Y-%m-%d %H:%M:%S', value.timetuple())


class Owners(User):
    """User with app settings."""
    # Use UserManager to get the create_user method, etc.
    # login = models.CharField(max_length=15, unique=True)
    # password = models.CharField(max_length=50)
    objects = UserManager()
    is_deleted = models.BooleanField(default=0)


class Devices(models.Model):
    owner = models.ForeignKey(Owners, null=True)
    KETTLE = 0
    DEVICES_TYPE_CHOICES = (
        (KETTLE, 'Чайник'),
    )
    #may be change in foreign key
    type = models.IntegerField(choices=DEVICES_TYPE_CHOICES, default=KETTLE)
    title = models.CharField(max_length=100)
    summary = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=500, null=True)
    device_date = UnixTimestampField(auto_created=True)
    is_deleted = models.BooleanField(default=0)


class DeviceEvents(models.Model):
    owner = models.ForeignKey(Owners)
    device = models.ForeignKey(Devices)
    event_date_begin = UnixTimestampField()
    event_date_end = UnixTimestampField(null=True, blank=True)
    short_news = models.CharField(max_length=100, null=True, blank=True)
    long_news = models.CharField(max_length=500, null=True, blank=True)
    event_date = UnixTimestampField(auto_created=True)
    is_deleted = models.BooleanField(default=0)
