#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate
from smart.functions import *
from smart.smart_forms import *
from smart.models import *


def register(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        form = LoginForm(request_data)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            try:
                Owners.objects.get(username=username)
            except Owners.DoesNotExist:
                new_owner = Owners.objects.create(username=username)
                new_owner.set_password(password)
                new_owner.save()
                return HttpResponse(json.dumps(return_owner_key(username)), content_type='application/json')
            return HttpResponse(json.dumps({"error": 'Пользователь с таким логином уже существует!'}),
                                content_type='application/json')
        else:
            return HttpResponse(json.dumps({"error": 'Неверный формат данных!'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({"error": ''}), content_type='application/json')


def log_in(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        username = request_data["username"]
        password = request_data["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                owner = Owners.objects.get(username=username, is_deleted=0)
            except User.DoesNotExist:
                return HttpResponse(json.dumps({"error": 'Неверный логин или пароль!'}),
                                    content_type='application/json')
            return HttpResponse(json.dumps(return_login(owner.pk)), content_type='application/json')
        else:
            return HttpResponse(json.dumps({"error": 'Неверный логин или пароль!'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({"error": ''}), content_type='application/json')


def devices_add(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        form = DeviceForm(request_data)
        if form.is_valid():
            owner_id = request_data["owner"]
            try:
                Owners.objects.get(id=owner_id, is_deleted=0)
            except Owners.DoesNotExist:
                return HttpResponse(json.dumps({"error": 'Доступ запрещен!'}),
                                    content_type='application/json')
            title = form.cleaned_data["title"]
            try:
                new_device = Devices.objects.get(id=request_data["device"])
            except Devices.DoesNotExist:
                return HttpResponse(json.dumps({"error": 'Неверный ключ активации!'}),
                                    content_type='application/json')
            if new_device.owner_id:
                return HttpResponse(json.dumps({"error": 'Доступ запрещен!'}), content_type='application/json')
            new_device.owner_id = owner_id
            new_device.title = title
            new_device.device_date = datetime.now()
            new_device.save(force_update=True)
            return HttpResponse(json.dumps(return_devices(owner_id)), content_type='application/json')
        else:
            return HttpResponse(json.dumps({"error": 'Неверный формат данных!'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({"error": ''}), content_type='application/json')


def devices_about_more(request):
    if request.method == 'GET':
        owner_id = request.GET["owner"]
        device_id = request.GET["device"]
        page = request.GET["page"]
        return HttpResponse(json.dumps(return_events(owner_id, device_id, page)),
                            content_type='application/json')
    else:
        return HttpResponse(json.dumps({"error": ''}), content_type='application/json')


def events_more(request):
    if request.method == 'GET':
        owner_id = request.GET["owner"]
        page = request.GET["page"]
        return HttpResponse(json.dumps(return_events(owner_id, page=page)), content_type='application/json')
    else:
        return HttpResponse(json.dumps({"error": ''}), content_type='application/json')


def events_add(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        form = DeviceEventsForm(request_data)
        print form
        if form.is_valid():
            owner_id = request_data["owner"]
            device_id = request_data["device"]
            try:
                Devices.objects.get(id=device_id, owner_id=owner_id, is_deleted=0)
            except Devices.DoesNotExist:
                return HttpResponse(json.dumps({"error": 'Доступ запрещен!'}), content_type='application/json')
            event_date_begin = form.cleaned_data["event_date_begin"]
            new_event = DeviceEvents.objects.create(owner_id=owner_id, device_id=device_id,
                                                    event_date_begin=event_date_begin,
                                                    event_date=datetime.now())
            new_event.save()
            return HttpResponse(json.dumps(return_events_add_or_ended(owner_id, device_id)),
                                content_type='application/json')
        else:
            return HttpResponse(json.dumps({"error": 'Неверный формат данных!'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({"error": ''}), content_type='application/json')


def events_ended(request):
    if request.method == 'GET':
        owner_id = request.GET["owner"]
        device_id = request.GET["device"]
        event_id = request.GET["event"]
        try:
            event = DeviceEvents.objects.get(id=event_id, device_id=device_id, owner_id=owner_id, event_date_end=None,
                                             is_deleted=0)
        except Devices.DoesNotExist or DeviceEvents.DoesNotExist:
            return HttpResponse(json.dumps({"error": 'Доступ запрещен!'}), content_type='application/json')
        if ended(event):
            return HttpResponse(json.dumps(return_events_add_or_ended(owner_id, device_id)),
                                content_type='application/json')
        else:
            return HttpResponse(json.dumps({"wait": "1"}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({"error": ''}), content_type='application/json')


def devices_remove(request):
    if request.method == 'GET':
        owner_id = request.GET["owner"]
        device_id = request.GET["device"]
        try:
            device = Devices.objects.get(id=device_id, owner_id=owner_id, is_deleted=0)
        except Devices.DoesNotExist:
            return HttpResponse(json.dumps({"error": 'Доступ запрещен!'}), content_type='application/json')
        device.is_deleted = 1
        events = DeviceEvents.objects.filter(device_id=device_id, owner_id=owner_id,
                                             is_deleted=0)
        for event in events:
            event.is_deleted = 1
            event.save()
        device.save()
        return HttpResponse(json.dumps({"success": '1'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({"error": ''}), content_type='application/json')

