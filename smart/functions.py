#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from django.http.response import HttpResponse
from smart.models import *

EVENTS_PER_PAGE = 10


# response
def return_response(obj):
    response = {"code": 0, "response": obj}
    return HttpResponse(json.dumps(response), content_type='application/json')


def return_error(msg):
    response = {"code": 1, "response": msg}
    return HttpResponse(json.dumps(response), content_type='application/json')


# extra
def return_begin_events(owner_id, device_id=None, page=1):
    if device_id:
        device_events = DeviceEvents.objects.filter(owner_id=owner_id, device_id=device_id, is_deleted=0) \
                            .order_by('-event_date')[:EVENTS_PER_PAGE * page]
    else:
        device_events = DeviceEvents.objects.filter(owner_id=owner_id, is_deleted=0) \
                            .order_by('-event_date')[:EVENTS_PER_PAGE * page]
    return_data = {}
    i = 0
    for device_event in device_events:
        return_data[i] = {
            "id": device_event.pk,
            "device_id": device_event.device_id,
            "short_news": device_event.short_news,
            "long_news": device_event.long_news,
            "event_date": reformat_date(device_event.event_date),
            "event_date_begin": reformat_date(device_event.event_date_begin)
        }
        i += 1
    if return_data is False:
        return {"message": 'Новостей нет :('}
    return return_data


def return_end_events(owner_id, device_id=None, page=1):
    if device_id:
        device_events = DeviceEvents.objects.filter(owner_id=owner_id, device_id=device_id, is_deleted=0).exclude(
            event_date_end=None).order_by('-event_date_end')[:EVENTS_PER_PAGE * page]
    else:
        device_events = DeviceEvents.objects.filter(owner_id=owner_id, is_deleted=0).exclude(
            event_date_end=None).order_by('-event_date_end')[:EVENTS_PER_PAGE * page]
    return_data = {}
    i = 0
    for device_event in device_events:
        return_data[i] = {
            "id": device_event.pk,
            "device_id": device_event.device_id,
            "short_news": device_event.short_news,
            "long_news": device_event.long_news,
            "event_date_end": reformat_date(device_event.event_date_end)
        }
        i += 1
    if return_data is False:
        return {"message": 'Новостей нет :('}
    return return_data


def return_devices(owner_id, with_history=0):
    devices = Devices.objects.filter(owner_id=owner_id, is_deleted=0).order_by('title')
    return_data = {}
    i = 0
    for device in devices:
        return_data[i] = {
            "id": device.pk,
            "type": device.type,
            "title": device.title,
            "summary": device.summary,
            "description": device.description
        }
        if with_history:
            return_data[i].update({"history": {"begin": return_begin_events(owner_id, device.pk),
                                               "end": return_end_events(owner_id, device.pk)}})
        i += 1
    if return_data is False:
        return {"message": 'Устройств нет :('}
    return return_data


def reformat_date(date):
    return date.strftime("%d %B %Y %H:%M:%S")


def return_current_events(owner_id):
    device_events = DeviceEvents.objects.filter(owner_id=owner_id, event_date_end=None, is_deleted=0) \
        .order_by('event_date_begin')
    return_data = {}
    i = 0
    for device_event in device_events:
        return_data[i] = {
            "id": device_event.pk,
            "event_date_begin": reformat_date(device_event.event_date_begin)
        }
        i += 1
    if return_data is False:
        return {"message": 'Незавершенных задач нет :('}
    return return_data


def return_events(owner_id, device_id=None, page=1):
    return {"history": {"begin": return_begin_events(owner_id),
                        "end": return_end_events(owner_id)}}


def ended(event):
    return False


def return_login(owner_id):
    return_data = {"owner_key": owner_id,
                   "news": {
                       "begin": return_begin_events(owner_id),
                       "end": return_end_events(owner_id)
                   }, "devices": return_devices(owner_id, 1)}
    return return_data


def return_events_add_or_ended(owner_id, device_id):
    return_data = {"current_events": return_current_events(owner_id), "news": {"begin": return_begin_events(owner_id)},
                   "devices": {"id": device_id,
                               "history": {"begin": return_begin_events(owner_id, device_id)}}}
    return return_data


def return_owner_key(username):
    try:
        owner = Owners.objects.get(username=username)
    except Owners.DoesNotExist:
        return {"error": 'Что-то пошло не так! :('}
    return {"owner_key": owner.pk}
