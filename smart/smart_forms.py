#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.forms import *
from smart.models import *


class LoginForm(ModelForm):
    class Meta:
        model = Owners
        fields = ['username', 'password']


class DeviceForm(ModelForm):
    class Meta:
        model = Devices
        fields = ['title']


class DeviceEventsForm(ModelForm):
    class Meta:
        model = DeviceEvents
        field = ['event_date_begin']
        exclude = ['event_date']